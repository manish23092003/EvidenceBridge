from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.api_evidence import EvidenceNormalizationRequest
from app.schemas.evidence import Evidence
from app.services.evidence_service import EvidenceService

router = APIRouter(prefix="/api/v1/evidence", tags=["Evidence"])


def get_evidence_service() -> EvidenceService:
    return EvidenceService()


@router.post("/normalize", response_model=list[Evidence])
async def normalize_evidence(
    request: EvidenceNormalizationRequest,
    service: EvidenceService = Depends(get_evidence_service),
) -> list[Evidence]:
    """
    Converts raw research execution results into normalized domain Evidence objects,
    preserving traceability to the original claims.
    """
    try:
        return service.normalize_research_results(
            execution_result=request.execution_result,
            original_claims=request.original_claims,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to normalize evidence due to an internal service error.",
        )
