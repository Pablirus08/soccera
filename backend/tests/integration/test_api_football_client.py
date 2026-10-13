import httpx
import pytest
import respx

from soccera.common.exceptions import DataSourceAuthError, DataSourceError, RateLimitExceededError
from soccera.config import Settings
from soccera.ingestion.providers.api_football.client import ApiFootballClient

BASE_URL = "https://v3.football.api-sports.io"


def make_client() -> ApiFootballClient:
    settings = Settings(
        api_football_base_url=BASE_URL,
        api_football_key="test-key",
        api_football_rate_limit_per_minute=1000,
        api_football_timeout_seconds=5,
    )
    return ApiFootballClient(settings=settings)


@respx.mock
def test_get_returns_response_list():
    respx.get(f"{BASE_URL}/leagues").mock(
        return_value=httpx.Response(200, json={"response": [{"league": {"id": 39}}], "errors": []})
    )

    with make_client() as client:
        result = client.get("leagues")

    assert result == [{"league": {"id": 39}}]


@respx.mock
def test_get_raises_auth_error_on_401_without_retrying():
    route = respx.get(f"{BASE_URL}/leagues").mock(return_value=httpx.Response(401))

    with make_client() as client, pytest.raises(DataSourceAuthError):
        client.get("leagues")

    assert route.call_count == 1


@respx.mock
def test_get_raises_data_source_error_on_api_errors_payload():
    respx.get(f"{BASE_URL}/leagues").mock(
        return_value=httpx.Response(
            200, json={"response": [], "errors": {"league": "Invalid league id"}}
        )
    )

    with make_client() as client, pytest.raises(DataSourceError):
        client.get("leagues")


@respx.mock
def test_get_retries_on_5xx_then_succeeds(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _seconds: None)
    route = respx.get(f"{BASE_URL}/leagues")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(200, json={"response": [{"league": {"id": 39}}], "errors": []}),
    ]

    with make_client() as client:
        result = client.get("leagues")

    assert result == [{"league": {"id": 39}}]
    assert route.call_count == 2


@respx.mock
def test_get_raises_rate_limit_error_after_exhausting_retries(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _seconds: None)
    route = respx.get(f"{BASE_URL}/leagues").mock(return_value=httpx.Response(429))

    with make_client() as client, pytest.raises(RateLimitExceededError):
        client.get("leagues")

    assert route.call_count == 5
