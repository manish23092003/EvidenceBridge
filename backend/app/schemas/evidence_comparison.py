from pydantic import BaseModel, Field

from app.schemas.finding import FindingStatus


class ComparisonEvaluation(BaseModel):
    status: FindingStatus = Field(
        description="The classification of the supplier's claim against the evidence."
    )
    explanation: str = Field(
        description=(
            "Brief explanation of why this status was assigned based ONLY "
            "on the evidence provided."
        )
    )
    evidence_ids: list[str] = Field(
        default_factory=list,
        description=(
            "List of evidence IDs that support this finding. Must ONLY use IDs "
            "provided in the input."
        ),
    )
    evidence_value: str | None = Field(
        default=None,
        description=(
            "A short, direct quote or extracted value from the evidence "
            "that supports the conclusion, if applicable."
        ),
    )
