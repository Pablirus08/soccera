"""
Thin wrapper around Sofascore's public JSON API. Sofascore blocks plain HTTP
clients (and headless browsers) by TLS fingerprint, and the api.sofascore.com
host is blocked outright, so every call goes through curl_cffi impersonating
Chrome against www.sofascore.com/api/v1. A small delay between calls keeps
the request rate polite.
"""

import time
from typing import Any

from curl_cffi import requests as cffi_requests

from soccera.logging import get_logger

logger = get_logger(__name__)

API_PREFIX = "https://www.sofascore.com/api/v1"
MIN_SECONDS_BETWEEN_CALLS = 0.5


class SofascoreError(RuntimeError):
    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.code = code


class SofascoreClient:
    def __init__(self) -> None:
        self._session = cffi_requests.Session(impersonate="chrome")
        self._last_call = 0.0

    def close(self) -> None:
        self._session.close()

    def get(self, path: str) -> dict[str, Any]:
        # Sofascore 403s any path with a trailing slash.
        url = f"{API_PREFIX}{path.rstrip('/')}"
        logger.debug("sofascore.request", path=path)

        wait = MIN_SECONDS_BETWEEN_CALLS - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        response = self._session.get(url, timeout=20)
        self._last_call = time.monotonic()

        try:
            data = response.json()
        except ValueError:
            raise SofascoreError(
                f"Sofascore {response.status_code} non-JSON response for {path}",
                code=response.status_code,
            ) from None
        # Sofascore answers blocks/missing resources with an {"error": {...}} body.
        if isinstance(data, dict) and "error" in data:
            err = data["error"]
            raise SofascoreError(
                f"Sofascore {err.get('code')} {err.get('reason')} for {path}", code=err.get("code")
            )
        return data
