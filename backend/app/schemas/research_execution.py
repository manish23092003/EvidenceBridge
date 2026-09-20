from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.claim import Claim
from app.schemas.research import SearchResultItem
from app.schemas.research_planning import ResearchPurpose


class ResearchExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    NO_RESULTS = "NO_RESULTS"
    FAILED = "FAILED"


class ResearchExecutionItem(BaseModel):
    query: str = Field(description="The actual web search query executed")
    purpose: ResearchPurpose = Field(description="The primary purpose of this query")
    claim_ids: list[str] = Field(
        description="IDs of the claims this query investigates"
    )
    status: ResearchExecutionStatus = Field(
        description="The status of the query execution"
    )
    results: list[SearchResultItem] = Field(
        default_factory=list, description="The search results retrieved"
    )
    error: str | None = Field(
        default=None, description="Safe error message if the query failed"
    )


class ResearchExecutionResult(BaseModel):
    queries: list[ResearchExecutionItem] = Field(
        default_factory=list,
        description="List of executed research queries and their outcomes",
    )


class ResearchRequest(BaseModel):
    claims: list[Claim] = Field(
        description="List of extracted claims to perform research on"
    )
