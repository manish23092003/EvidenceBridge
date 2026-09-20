from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    url: str = Field(description="The source URL of the research result")
    title: str = Field(description="Title of the research result page")
    snippet: str = Field(description="Text snippet summarizing the match")
    content: str | None = Field(default=None, description="Full content if available")
    published_date: str | None = Field(
        default=None, description="Optional publication date string"
    )
    last_updated: str | None = Field(
        default=None, description="Optional last updated date string"
    )
    position: int | None = Field(
        default=None, description="Position in the search results"
    )


class SearchResult(BaseModel):
    query: str = Field(description="The original search query")
    results: list[SearchResultItem] = Field(
        default_factory=list, description="The individual research items retrieved"
    )
