from pydantic import BaseModel, Field

from app.schemas.claim import Claim
from app.schemas.evidence import Evidence


class EvidenceComparisonRequest(BaseModel):
    claims: list[Claim] = Field(description="The claims extracted from the document")
    evidence: list[Evidence] = Field(description="The normalized evidence collected")
