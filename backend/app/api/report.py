from fastapi import APIRouter, Depends

from app.schemas.report import ReportRequest, VerificationReport
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/v1/report", tags=["Report"])


def get_report_service() -> ReportService:
    return ReportService()


@router.post("", response_model=VerificationReport)
async def generate_report(
    request: ReportRequest, service: ReportService = Depends(get_report_service)
) -> VerificationReport:
    """
    Generates a deterministic verification report from existing findings and evidence.
    Does NOT perform new web research or LLM evaluations.
    """
    return service.generate_report(
        verification_id=request.verification_id,
        supplier=request.supplier,
        purchase_amount=request.purchase_amount,
        currency=request.currency,
        findings=request.findings,
        evidence_list=request.evidence,
    )
