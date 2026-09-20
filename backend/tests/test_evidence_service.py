from datetime import timezone

from app.schemas.claim import Claim, ClaimSource
from app.schemas.evidence import EvidenceSourceType
from app.schemas.research import SearchResultItem
from app.schemas.research_execution import (
    ResearchExecutionItem,
    ResearchExecutionResult,
    ResearchExecutionStatus,
)
from app.schemas.research_planning import ResearchPurpose
from app.services.evidence_service import EvidenceService


def create_claim(claim_id, field="supplier_name", value="ABC"):
    return Claim(
        id=claim_id,
        verification_id="ver-123",
        field=field,
        value=value,
        source=ClaimSource.DOCUMENT,
        created_at="2026-09-01T00:00:00Z",
    )


def test_successful_result_to_evidence():
    claims = [create_claim("c1", "address", "Bengaluru")]
    exec_result = ResearchExecutionResult(
        queries=[
            ResearchExecutionItem(
                query="ABC Bengaluru",
                purpose=ResearchPurpose.ADDRESS,
                claim_ids=["c1"],
                status=ResearchExecutionStatus.SUCCESS,
                results=[
                    SearchResultItem(
                        url="http://abc.com",
                        title="ABC Site",
                        snippet="Located in Bengaluru",
                    )
                ],
            )
        ]
    )

    service = EvidenceService()
    evidence_list = service.normalize_research_results(exec_result, claims)

    assert len(evidence_list) == 1
    ev = evidence_list[0]
    assert ev.id is not None
    assert ev.verification_id == "ver-123"
    assert ev.field == "address"
    assert ev.value == "Located in Bengaluru"
    assert ev.source_url == "http://abc.com"
    assert ev.source_title == "ABC Site"
    assert ev.snippet == "Located in Bengaluru"
    assert ev.source_type == EvidenceSourceType.WEB
    assert ev.claim_ids == ["c1"]
    assert ev.created_at.tzinfo == timezone.utc


def test_multiple_claims_preserved():
    claims = [create_claim("c1"), create_claim("c2")]
    exec_result = ResearchExecutionResult(
        queries=[
            ResearchExecutionItem(
                query="ABC",
                purpose=ResearchPurpose.IDENTITY,
                claim_ids=["c1", "c2"],
                status=ResearchExecutionStatus.SUCCESS,
                results=[
                    SearchResultItem(url="http://abc.com", title="ABC", snippet="snip")
                ],
            )
        ]
    )

    service = EvidenceService()
    evidence_list = service.normalize_research_results(exec_result, claims)

    assert len(evidence_list) == 1
    assert set(evidence_list[0].claim_ids) == {"c1", "c2"}


def test_no_results_and_failed_research():
    claims = [create_claim("c1")]
    exec_result = ResearchExecutionResult(
        queries=[
            ResearchExecutionItem(
                query="ABC",
                purpose=ResearchPurpose.IDENTITY,
                claim_ids=["c1"],
                status=ResearchExecutionStatus.NO_RESULTS,
                results=[],
            ),
            ResearchExecutionItem(
                query="DEF",
                purpose=ResearchPurpose.IDENTITY,
                claim_ids=["c1"],
                status=ResearchExecutionStatus.FAILED,
                results=[],
                error="Timeout",
            ),
        ]
    )

    service = EvidenceService()
    evidence_list = service.normalize_research_results(exec_result, claims)

    assert len(evidence_list) == 0


def test_content_plus_snippet():
    claims = [create_claim("c1")]
    exec_result = ResearchExecutionResult(
        queries=[
            ResearchExecutionItem(
                query="ABC",
                purpose=ResearchPurpose.IDENTITY,
                claim_ids=["c1"],
                status=ResearchExecutionStatus.SUCCESS,
                results=[
                    SearchResultItem(
                        url="http://abc.com",
                        title="ABC",
                        snippet="Short snip",
                        content="Longer detailed content about ABC",
                    )
                ],
            )
        ]
    )

    service = EvidenceService()
    evidence_list = service.normalize_research_results(exec_result, claims)

    assert len(evidence_list) == 1
    assert evidence_list[0].value == "Longer detailed content about ABC"
    assert evidence_list[0].snippet == "Short snip"


def test_missing_usable_content():
    claims = [create_claim("c1")]
    exec_result = ResearchExecutionResult(
        queries=[
            ResearchExecutionItem(
                query="ABC",
                purpose=ResearchPurpose.IDENTITY,
                claim_ids=["c1"],
                status=ResearchExecutionStatus.SUCCESS,
                results=[
                    SearchResultItem(
                        url="http://abc.com", title="ABC", snippet="   ", content=""
                    )
                ],
            )
        ]
    )

    service = EvidenceService()
    evidence_list = service.normalize_research_results(exec_result, claims)

    assert len(evidence_list) == 0


def test_duplicate_result_deduplication():
    claims = [create_claim("c1")]
    exec_result = ResearchExecutionResult(
        queries=[
            ResearchExecutionItem(
                query="ABC",
                purpose=ResearchPurpose.IDENTITY,
                claim_ids=["c1"],
                status=ResearchExecutionStatus.SUCCESS,
                results=[
                    SearchResultItem(
                        url="http://abc.com", title="ABC", snippet="Snip 1"
                    ),
                    # Duplicate URL for the same claims
                    SearchResultItem(
                        url="http://abc.com", title="ABC", snippet="Snip 1"
                    ),
                ],
            )
        ]
    )

    service = EvidenceService()
    evidence_list = service.normalize_research_results(exec_result, claims)

    assert len(evidence_list) == 1
