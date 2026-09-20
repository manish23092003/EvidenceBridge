from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EvidenceSourceType(str, Enum):
    WEB = "WEB"
    DOCUMENT = "DOCUMENT"
    USER_PROVIDED = "USER_PROVIDED"


class Evidence(BaseModel):
    id: str
    verification_id: str
    field: str
    value: str
    source_url: str | None = None
    source_title: str | None = None
    snippet: str | None = None
    claim_ids: list[str] = Field(default_factory=list)
    source_type: EvidenceSourceType
    created_at: datetime = Field(default_factory=utc_now)
