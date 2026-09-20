from fastapi import APIRouter, Depends, HTTPException, status

from app.providers.gemini import GeminiProvider
from app.providers.llm import LLMProvider
from app.schemas.api_comparison import EvidenceComparisonRequest
from app.schemas.finding import Finding
from app.services.evidence_comparison_service import EvidenceComparisonService

router = APIRouter(prefix="/api/v1/evidence", tags=["Evidence"])


def get_llm_provider() -> LLMProvider:
    return GeminiProvider()


def get_evidence_comparison_service(
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> EvidenceComparisonService:
    return EvidenceComparisonService(llm_provider=llm_provider)


@router.post("/compare", response_model=list[Finding])
async def compare_evidence(
    request: EvidenceComparisonRequest,
    service: EvidenceComparisonService = Depends(get_evidence_comparison_service),
) -> list[Finding]:
    """
    Compares extracted supplier claims against retrieved evidence using an LLM.
    Returns structured findings matching the input claims to the evidence.
    """
    try:
        return service.generate_findings(
            claims=request.claims, evidence_list=request.evidence
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare evidence due to an internal service error.",
        )
