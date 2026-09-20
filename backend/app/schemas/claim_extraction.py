from pydantic import BaseModel, Field


class ExtractedClaim(BaseModel):
    field: str = Field(
        description="The name of the field extracted, e.g., 'supplier_name', 'address'"
    )
    value: str = Field(
        description="The extracted value exactly as it appears in the text, normalized"
    )


class ClaimExtractionResult(BaseModel):
    claims: list[ExtractedClaim] = Field(
        default_factory=list,
        description="List of extracted claims. Empty if no supported fields are found.",
    )
