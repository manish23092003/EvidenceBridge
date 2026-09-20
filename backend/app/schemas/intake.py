from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CreateVerificationRequest(BaseModel):
    supplier_name: str
    website: str | None = None
    location: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    product_or_service: str | None = None
    purchase_amount: float = Field(ge=0.0)
    currency: str = "INR"
    document_filename: str | None = None


class CreateVerificationResponse(BaseModel):
    verification_id: str
    supplier_id: str
    status: str
    purchase_amount: float
    currency: str
    created_at: datetime
