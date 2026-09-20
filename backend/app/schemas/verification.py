from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class VerificationRequest(BaseModel):
    id: str
    supplier_id: str
    purchase_amount: float = Field(ge=0.0)
    currency: str = "INR"
    document_filename: str | None = None
    status: VerificationStatus = VerificationStatus.PENDING
    created_at: datetime = Field(default_factory=utc_now)
