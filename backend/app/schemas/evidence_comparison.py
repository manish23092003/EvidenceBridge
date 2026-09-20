from pydantic import BaseModel, Field

from app.schemas.finding import FindingStatus


class ComparisonEvaluation(BaseModel):
    status: FindingStatus = Field(
        description="The evaluated status of the claim based on evidence"
    )
    explanation: str = Field(
        description="Brief explanation of why this status was assigned based ONLY on the evidence provided"
    )
    evidence_ids: list[str] = Field(
        default_factory=list,
        description="List of evidence IDs that support this finding. Must ONLY use IDs provided in the input.",
    )
    evidence_value: str | None = Field(
        default=None,
        description="A short, exact quote from the evidence that supports the finding, if applicable",
    )
