from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FindingStatus(str, Enum):
    CONSISTENT = "CONSISTENT"
    MISMATCH = "MISMATCH"
    NOT_FOUND = "NOT_FOUND"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class Finding(BaseModel):
    id: str
    verification_id: str
    field: str
    status: FindingStatus
    claim_value: str | None = None
    evidence_value: str | None = None
    explanation: str
    evidence_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
