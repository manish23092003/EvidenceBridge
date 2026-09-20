from fastapi import APIRouter, Depends

from app.providers.anakin import AnakinProvider
from app.providers.web_research import WebResearchProvider
from app.schemas.research_execution import ResearchExecutionResult, ResearchRequest
from app.services.research_planner import ResearchPlannerService
from app.services.research_service import ResearchService

router = APIRouter(prefix="/api/v1/research", tags=["Research"])


# Dependency injection factories
def get_research_planner() -> ResearchPlannerService:
    return ResearchPlannerService()


def get_web_research_provider() -> WebResearchProvider:
    return AnakinProvider()


def get_research_service(
    planner: ResearchPlannerService = Depends(get_research_planner),
    provider: WebResearchProvider = Depends(get_web_research_provider),
) -> ResearchService:
    return ResearchService(planner=planner, provider=provider)


@router.post("", response_model=ResearchExecutionResult)
async def execute_research(
    request: ResearchRequest, service: ResearchService = Depends(get_research_service)
) -> ResearchExecutionResult:
    """
    Accepts extracted domain Claims, builds a research plan, executes it using
    the web provider, and returns execution results with traceability to the claims.
    """
    return service.execute_research(request.claims)
