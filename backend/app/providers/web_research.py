from typing import Protocol

from app.schemas.research import SearchResult


class WebResearchError(Exception):
    pass


class WebResearchConfigurationError(WebResearchError):
    pass


class WebResearchAuthenticationError(WebResearchError):
    pass


class WebResearchRateLimitError(WebResearchError):
    pass


class WebResearchTimeoutError(WebResearchError):
    pass


class WebResearchProviderError(WebResearchError):
    pass


class WebResearchProvider(Protocol):
    def search(self, query: str, limit: int = 5) -> SearchResult:
        """
        Executes a web search for the given query and returns a normalized SearchResult.
        """
        ...
