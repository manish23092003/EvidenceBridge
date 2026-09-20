from unittest.mock import MagicMock

from app.providers.web_research import WebResearchTimeoutError
from app.schemas.claim import Claim, ClaimSource
from app.schemas.research import SearchResult, SearchResultItem
from app.schemas.research_execution import ResearchExecutionStatus
from app.schemas.research_planning import ResearchPurpose, ResearchQuery
from app.services.research_service import ResearchService


def create_mock_claim():
    return Claim(
        id="c1",
        verification_id="v1",
        field="supplier_name",
        value="ABC",
        source=ClaimSource.DOCUMENT,
        created_at="2026-09-01T00:00:00Z",
    )


def test_normal_execution():
    planner = MagicMock()
    provider = MagicMock()

    planner.plan.return_value = [
        ResearchQuery(query='"ABC"', purpose=ResearchPurpose.IDENTITY, claim_ids=["c1"])
    ]

    provider.search.return_value = SearchResult(
        query='"ABC"',
        results=[SearchResultItem(url="http://abc.com", title="ABC", snippet="snip")],
    )

    service = ResearchService(planner, provider)
    result = service.execute_research([create_mock_claim()])

    assert len(result.queries) == 1
    assert result.queries[0].query == '"ABC"'
    assert result.queries[0].status == ResearchExecutionStatus.SUCCESS
    assert len(result.queries[0].results) == 1
    assert result.queries[0].results[0].url == "http://abc.com"
    assert result.queries[0].error is None


def test_no_queries():
    planner = MagicMock()
    provider = MagicMock()
    planner.plan.return_value = []

    service = ResearchService(planner, provider)
    result = service.execute_research([create_mock_claim()])

    assert len(result.queries) == 0
    provider.search.assert_not_called()


def test_empty_anakin_results():
    planner = MagicMock()
    provider = MagicMock()
    planner.plan.return_value = [
        ResearchQuery(query='"ABC"', purpose=ResearchPurpose.IDENTITY, claim_ids=["c1"])
    ]
    provider.search.return_value = SearchResult(query='"ABC"', results=[])

    service = ResearchService(planner, provider)
    result = service.execute_research([create_mock_claim()])

    assert len(result.queries) == 1
    assert result.queries[0].status == ResearchExecutionStatus.NO_RESULTS
    assert len(result.queries[0].results) == 0


def test_provider_failure_continues_execution():
    planner = MagicMock()
    provider = MagicMock()
    planner.plan.return_value = [
        ResearchQuery(
            query='"ABC"', purpose=ResearchPurpose.IDENTITY, claim_ids=["c1"]
        ),
        ResearchQuery(
            query='"DEF"', purpose=ResearchPurpose.IDENTITY, claim_ids=["c2"]
        ),
    ]

    # First fails with timeout, second succeeds
    def mock_search(query):
        if query == '"ABC"':
            raise WebResearchTimeoutError("Timeout error")
        return SearchResult(
            query=query,
            results=[SearchResultItem(url="def.com", title="DEF", snippet="")],
        )

    provider.search.side_effect = mock_search

    service = ResearchService(planner, provider)
    result = service.execute_research([])

    assert len(result.queries) == 2
    assert result.queries[0].status == ResearchExecutionStatus.FAILED
    assert result.queries[0].error == "Timeout error"

    assert result.queries[1].status == ResearchExecutionStatus.SUCCESS
    assert result.queries[1].results[0].url == "def.com"


def test_unexpected_provider_failure():
    planner = MagicMock()
    provider = MagicMock()
    planner.plan.return_value = [
        ResearchQuery(query='"ABC"', purpose=ResearchPurpose.IDENTITY, claim_ids=["c1"])
    ]
    provider.search.side_effect = Exception("System Crash")

    service = ResearchService(planner, provider)
    result = service.execute_research([])

    assert len(result.queries) == 1
    assert result.queries[0].status == ResearchExecutionStatus.FAILED
    assert "unexpected" in result.queries[0].error
    assert "Crash" not in result.queries[0].error  # Do not leak raw errors
