from fastapi import APIRouter, status

from app.schemas.intake import CreateVerificationRequest, CreateVerificationResponse
from app.services.verification_service import VerificationService

router = APIRouter(
    prefix="/api/v1/verification-requests", tags=["Verification Requests"]
)


@router.post(
    "", response_model=CreateVerificationResponse, status_code=status.HTTP_201_CREATED
)
def create_verification_request(
    data: CreateVerificationRequest,
) -> CreateVerificationResponse:
    supplier, verification = VerificationService.create_verification(data)

    return CreateVerificationResponse(
        verification_id=verification.id,
        supplier_id=supplier.id,
        status=verification.status,
        purchase_amount=verification.purchase_amount,
        currency=verification.currency,
        created_at=verification.created_at,
    )
