from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Minimal health-check endpoint.
    """
    return HealthResponse(status="ok")
