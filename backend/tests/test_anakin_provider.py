from unittest.mock import MagicMock

import httpx
import pytest

from app.config import get_settings
from app.providers.anakin import AnakinProvider
from app.providers.web_research import (
    WebResearchAuthenticationError,
    WebResearchConfigurationError,
    WebResearchProviderError,
    WebResearchRateLimitError,
    WebResearchTimeoutError,
)


@pytest.fixture
def configured_provider(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "anakin_api_key", "test-key")
    return AnakinProvider()


def mock_httpx_response(
    monkeypatch, status_code: int, json_data: dict = None, exc: Exception = None
):
    def mock_post(*args, **kwargs):
        if exc:
            raise exc

        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = json_data or {}

        if status_code >= 400:
            mock_resp.text = "Error content"

            def raise_for_status():
                raise httpx.HTTPStatusError(
                    "Error", request=MagicMock(), response=mock_resp
                )

            mock_resp.raise_for_status = raise_for_status
        else:
            mock_resp.raise_for_status = MagicMock()

        return mock_resp

    monkeypatch.setattr(httpx.Client, "post", mock_post)


def test_successful_search(monkeypatch, configured_provider):
    mock_data = {
        "results": [
            {
                "url": "https://example.com/supplier",
                "title": "ABC Industrial Solutions",
                "snippet": "We provide CNC components in Bengaluru.",
                "date": "2026-09-01",
            }
        ]
    }
    mock_httpx_response(monkeypatch, 200, mock_data)

    result = configured_provider.search("ABC Industrial Solutions Bengaluru")

    assert result.query == "ABC Industrial Solutions Bengaluru"
    assert len(result.results) == 1
    assert result.results[0].url == "https://example.com/supplier"
    assert result.results[0].title == "ABC Industrial Solutions"
    assert result.results[0].snippet == "We provide CNC components in Bengaluru."
    assert result.results[0].published_date == "2026-09-01"
    assert result.results[0].position == 1


def test_empty_query(configured_provider):
    with pytest.raises(
        WebResearchConfigurationError, match="Search query cannot be empty"
    ):
        configured_provider.search("")


def test_empty_result(monkeypatch, configured_provider):
    mock_httpx_response(monkeypatch, 200, {"results": []})
    result = configured_provider.search("Query with no results")
    assert result.query == "Query with no results"
    assert result.results == []


def test_authentication_failure(monkeypatch, configured_provider):
    mock_httpx_response(monkeypatch, 401)
    with pytest.raises(
        WebResearchAuthenticationError, match="Anakin authentication failed"
    ):
        configured_provider.search("test")


def test_rate_limiting(monkeypatch, configured_provider):
    mock_httpx_response(monkeypatch, 429)
    with pytest.raises(WebResearchRateLimitError, match="rate limit exceeded"):
        configured_provider.search("test")


def test_timeout(monkeypatch, configured_provider):
    mock_httpx_response(monkeypatch, 200, exc=httpx.TimeoutException("Timeout"))
    with pytest.raises(WebResearchTimeoutError, match="Anakin API timeout"):
        configured_provider.search("test")


def test_provider_failure(monkeypatch, configured_provider):
    mock_httpx_response(monkeypatch, 500)
    with pytest.raises(WebResearchProviderError, match="Anakin returned HTTP 500"):
        configured_provider.search("test")


def test_request_error(monkeypatch, configured_provider):
    mock_httpx_response(monkeypatch, 200, exc=httpx.RequestError("Network Down"))
    with pytest.raises(
        WebResearchProviderError, match="Failed to connect to Anakin API"
    ):
        configured_provider.search("test")
