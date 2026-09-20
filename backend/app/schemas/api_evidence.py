from pydantic import BaseModel, Field

from app.schemas.claim import Claim
from app.schemas.research_execution import ResearchExecutionResult


class EvidenceNormalizationRequest(BaseModel):
    execution_result: ResearchExecutionResult = Field(
        description="The results of web research orchestration"
    )
    original_claims: list[Claim] = Field(
        description="The original claims used to generate the research"
    )
