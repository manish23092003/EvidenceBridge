from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ClaimSource(str, Enum):
    USER_INPUT = "USER_INPUT"
    DOCUMENT = "DOCUMENT"


class Claim(BaseModel):
    id: str
    verification_id: str
    field: str
    value: str
    source: ClaimSource
    created_at: datetime = Field(default_factory=utc_now)
