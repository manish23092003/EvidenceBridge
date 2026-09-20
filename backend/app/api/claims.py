from fastapi import APIRouter, Depends, HTTPException, status

from app.providers.gemini import GeminiProvider
from app.providers.llm import LLMProvider
from app.schemas.api_claims import ClaimExtractionRequest
from app.schemas.claim import Claim
from app.services.claim_extraction_service import ClaimExtractionService

router = APIRouter(prefix="/api/v1/claims", tags=["Claims"])


def get_llm_provider() -> LLMProvider:
    return GeminiProvider()


def get_claim_extraction_service(
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> ClaimExtractionService:
    return ClaimExtractionService(provider=llm_provider)


@router.post("/extract", response_model=list[Claim])
async def extract_claims(
    request: ClaimExtractionRequest,
    service: ClaimExtractionService = Depends(get_claim_extraction_service),
) -> list[Claim]:
    """
    Extracts structured supplier claims from normalized text using an LLM.
    """
    try:
        return service.extract_claims(
            text=request.text, verification_id=request.verification_id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract claims due to an internal service error.",
        )
