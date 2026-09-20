from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Supplier(BaseModel):
    id: str
    name: str
    website: str | None = None
    location: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    product_or_service: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
