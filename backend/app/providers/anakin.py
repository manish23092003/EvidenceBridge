from typing import Any

import httpx

from app.config import get_settings
from app.providers.web_research import (
    WebResearchAuthenticationError,
    WebResearchConfigurationError,
    WebResearchProvider,
    WebResearchProviderError,
    WebResearchRateLimitError,
    WebResearchTimeoutError,
)
from app.schemas.research import SearchResult, SearchResultItem


class AnakinProvider(WebResearchProvider):
    """
    HTTP REST adapter for Anakin.io search API.
    Used as fallback due to lack of stable anakin-sdk package for web search explicitly.
    """

    BASE_URL = "https://api.anakin.io/v1"

    def __init__(self, api_key: str | None = None, timeout_seconds: int | None = None):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.anakin_api_key
        self.timeout = timeout_seconds or self.settings.anakin_timeout_seconds

        if not self.api_key:
            # We don't necessarily raise here to allow instantiation,
            # but it will fail when searching.
            pass

    def search(self, query: str, limit: int | None = None) -> SearchResult:
        if not query or not query.strip():
            raise WebResearchConfigurationError("Search query cannot be empty.")

        if not self.api_key:
            raise WebResearchConfigurationError("Anakin API key is not configured.")

        actual_limit = limit if limit is not None else self.settings.anakin_search_limit

        # Anakin synchronous search payload
        payload = {"prompt": query, "limit": actual_limit}

        headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}

        try:
            with httpx.Client(
                base_url=self.BASE_URL, headers=headers, timeout=self.timeout
            ) as client:
                response = client.post("/search", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as e:
            raise WebResearchTimeoutError(
                f"Anakin API timeout after {self.timeout}s."
            ) from e
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status in (401, 403):
                raise WebResearchAuthenticationError(
                    "Anakin authentication failed. Check API key."
                ) from e
            elif status == 429:
                # If this fails, wait a bit and retry.
                # If we exhaust retries, it raises the last exception.
                raise WebResearchRateLimitError("Anakin rate limit exceeded.") from e
            else:
                raise WebResearchProviderError(
                    f"Anakin returned HTTP {status}: {e.response.text}"
                ) from e
        except httpx.RequestError as e:
            raise WebResearchProviderError(
                f"Failed to connect to Anakin API: {str(e)}"
            ) from e
        except Exception as e:
            raise WebResearchProviderError(
                f"Unexpected error communicating with Anakin: {str(e)}"
            ) from e

        # Parse the JSON results from Anakin
        # We handle typical search output structures defensively.
        return self._parse_response(query, data)

    def _parse_response(self, query: str, data: dict[str, Any]) -> SearchResult:
        items = []

        # Depending on Anakin's exact schema, the results usually come in a
        # data/results list. We will parse assuming standard JSON layout or
        # fallback safely if no results exist.
        raw_results = (
            data.get("data", {}).get("results", [])
            if "data" in data
            else data.get("results", [])
        )

        if not raw_results:
            return SearchResult(query=query, results=[])

        for idx, item in enumerate(raw_results):
            # Extract basic fields
            url = item.get("url") or item.get("link")
            title = item.get("title", "")
            snippet = item.get("snippet", "") or item.get("content", "")
            published_date = item.get("date") or item.get("published_date")
            last_updated = item.get("last_updated")

            if url:
                items.append(
                    SearchResultItem(
                        url=url,
                        title=title,
                        snippet=snippet,
                        published_date=published_date,
                        last_updated=last_updated,
                        position=idx + 1,
                    )
                )

        return SearchResult(query=query, results=items)
