from pydantic import BaseModel, Field, computed_field


class PdfExtractionResult(BaseModel):
    filename: str | None = None
    page_count: int = Field(ge=1)
    character_count: int = Field(ge=0)
    text: str

    @computed_field
    def has_text(self) -> bool:
        return self.character_count > 0
