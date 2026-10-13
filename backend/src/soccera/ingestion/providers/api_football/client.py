from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from soccera.common.exceptions import DataSourceAuthError, DataSourceError, RateLimitExceededError
from soccera.common.rate_limiter import RateLimiter
from soccera.config import Settings, get_settings
from soccera.logging import get_logger

logger = get_logger(__name__)


class _RetryableStatusError(Exception):
    """Internal signal for tenacity to retry on — never escapes this module."""

    def __init__(self, response: httpx.Response):
        self.response = response
        super().__init__(f"retryable status {response.status_code}")


class ApiFootballClient:
    """
    Thin HTTP client for api-sports.io's API-Football v3. Handles auth,
    rate limiting, and retries — knows nothing about soccer domain
    concepts. ApiFootballAdapter builds on top of this.
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._rate_limiter = RateLimiter(
            max_calls=self._settings.api_football_rate_limit_per_minute, period_seconds=60.0
        )
        self._client = httpx.Client(
            base_url=self._settings.api_football_base_url,
            headers={"x-apisports-key": self._settings.api_football_key},
            timeout=self._settings.api_football_timeout_seconds,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ApiFootballClient":
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Calls a GET endpoint and returns the "response" list from
        API-Football's envelope. Raises DataSourceError subclasses on
        failure; never returns a malformed/partial payload silently.
        """
        self._rate_limiter.acquire()
        try:
            response = self._request_with_retry(endpoint, params or {})
        except _RetryableStatusError as exc:
            if exc.response.status_code == 429:
                raise RateLimitExceededError(
                    f"API-Football rate limit exceeded for {endpoint} after retries"
                ) from exc
            raise DataSourceError(
                f"API-Football request to {endpoint} kept failing "
                f"({exc.response.status_code}) after retries"
            ) from exc
        payload = response.json()

        errors = payload.get("errors")
        if errors:
            raise DataSourceError(f"API-Football returned errors for {endpoint}: {errors}")

        return payload.get("response", [])

    @retry(
        retry=retry_if_exception_type(_RetryableStatusError),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        reraise=True,
    )
    def _request_with_retry(self, endpoint: str, params: dict[str, Any]) -> httpx.Response:
        try:
            response = self._client.get(endpoint, params=params)
        except httpx.TransportError as exc:
            logger.warning("api_football.transport_error", endpoint=endpoint, error=str(exc))
            raise DataSourceError(f"Network error calling {endpoint}: {exc}") from exc

        if response.status_code in (401, 403):
            raise DataSourceAuthError(
                f"API-Football auth failed ({response.status_code}) for {endpoint}"
            )

        if response.status_code == 429:
            logger.warning("api_football.rate_limited", endpoint=endpoint)
            raise _RetryableStatusError(response)

        if response.status_code >= 500:
            logger.warning(
                "api_football.server_error", endpoint=endpoint, status=response.status_code
            )
            raise _RetryableStatusError(response)

        if response.status_code >= 400:
            raise DataSourceError(
                f"API-Football request to {endpoint} failed with {response.status_code}: "
                f"{response.text}"
            )

        return response
