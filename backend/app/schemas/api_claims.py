from pydantic import BaseModel, Field

from app.schemas.claim import Claim


class ClaimExtractionRequest(BaseModel):
    verification_id: str = Field(description="The verification request ID")
    text: str = Field(description="Normalized document text to extract claims from")


class ClaimExtractionResponse(BaseModel):
    claims: list[Claim] = Field(description="List of extracted claims")
