import uuid

from app.schemas.intake import CreateVerificationRequest
from app.schemas.supplier import Supplier
from app.schemas.verification import VerificationRequest, VerificationStatus


class VerificationService:
    @staticmethod
    def create_verification(
        request_data: CreateVerificationRequest,
    ) -> tuple[Supplier, VerificationRequest]:
        # Generate domain IDs
        supplier_id = str(uuid.uuid4())
        verification_id = str(uuid.uuid4())

        # Create Domain Models
        supplier = Supplier(
            id=supplier_id,
            name=request_data.supplier_name,
            website=request_data.website,
            location=request_data.location,
            email=request_data.email,
            phone=request_data.phone,
            product_or_service=request_data.product_or_service,
        )

        verification = VerificationRequest(
            id=verification_id,
            supplier_id=supplier_id,
            purchase_amount=request_data.purchase_amount,
            currency=request_data.currency,
            document_filename=request_data.document_filename,
            status=VerificationStatus.PENDING,
        )

        # Note: Persistence is intentionally omitted for this task.
        # This service acts as a pure function returning domain models.

        return supplier, verification
