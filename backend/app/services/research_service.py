from app.providers.web_research import WebResearchError, WebResearchProvider
from app.schemas.claim import Claim
from app.schemas.research_execution import (
    ResearchExecutionItem,
    ResearchExecutionResult,
    ResearchExecutionStatus,
)
from app.services.research_planner import ResearchPlannerService


class ResearchService:
    def __init__(
        self, planner: ResearchPlannerService, provider: WebResearchProvider
    ) -> None:
        self.planner = planner
        self.provider = provider

    def execute_research(self, claims: list[Claim]) -> ResearchExecutionResult:
        queries = self.planner.plan(claims)

        execution_items = []
        for q in queries:
            try:
                search_result = self.provider.search(q.query)
                results = search_result.results

                if not results:
                    status = ResearchExecutionStatus.NO_RESULTS
                else:
                    status = ResearchExecutionStatus.SUCCESS

                execution_items.append(
                    ResearchExecutionItem(
                        query=q.query,
                        purpose=q.purpose,
                        claim_ids=q.claim_ids,
                        status=status,
                        results=results,
                        error=None,
                    )
                )
            except WebResearchError as e:
                # Safe, user-independent message for known web research errors
                execution_items.append(
                    ResearchExecutionItem(
                        query=q.query,
                        purpose=q.purpose,
                        claim_ids=q.claim_ids,
                        status=ResearchExecutionStatus.FAILED,
                        results=[],
                        error=str(e),
                    )
                )
            except Exception:
                # Catch-all for unexpected issues, providing a highly generic safe error
                execution_items.append(
                    ResearchExecutionItem(
                        query=q.query,
                        purpose=q.purpose,
                        claim_ids=q.claim_ids,
                        status=ResearchExecutionStatus.FAILED,
                        results=[],
                        error="An unexpected provider error occurred during research.",
                    )
                )

        return ResearchExecutionResult(queries=execution_items)
