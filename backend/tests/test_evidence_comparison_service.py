from unittest.mock import MagicMock

from app.schemas.claim import Claim, ClaimSource
from app.schemas.evidence import Evidence, EvidenceSourceType
from app.schemas.evidence_comparison import ComparisonEvaluation
from app.schemas.finding import FindingStatus
from app.services.evidence_comparison_service import EvidenceComparisonService


def create_claim(claim_id, field="supplier_name", value="ABC"):
    return Claim(
        id=claim_id,
        verification_id="ver-123",
        field=field,
        value=value,
        source=ClaimSource.DOCUMENT,
        created_at="2026-09-01T00:00:00Z",
    )


def create_evidence(evidence_id, claim_ids, value="Found ABC"):
    return Evidence(
        id=evidence_id,
        verification_id="ver-123",
        field="supplier_name",
        value=value,
        source_url="http://abc.com",
        source_type=EvidenceSourceType.WEB,
        claim_ids=claim_ids,
        created_at="2026-09-01T00:00:00Z",
    )


def test_no_evidence_returns_not_found():
    llm = MagicMock()
    service = EvidenceComparisonService(llm)

    claims = [create_claim("c1")]
    # No evidence matches claim c1
    evidence_list = [create_evidence("e1", ["c2"])]

    findings = service.generate_findings(claims, evidence_list)

    assert len(findings) == 1
    assert findings[0].status == FindingStatus.NOT_FOUND
    assert findings[0].explanation == "No evidence was found for this claim."
    assert findings[0].evidence_ids == []
    llm.extract_structured.assert_not_called()


def test_llm_evaluation_success():
    llm = MagicMock()
    service = EvidenceComparisonService(llm)

    claims = [create_claim("c1")]
    evidence_list = [create_evidence("e1", ["c1"])]

    llm.extract_structured.return_value = ComparisonEvaluation(
        status=FindingStatus.CONSISTENT,
        explanation="The evidence confirms the name.",
        evidence_ids=["e1"],
        evidence_value="ABC",
    )

    findings = service.generate_findings(claims, evidence_list)

    assert len(findings) == 1
    assert findings[0].status == FindingStatus.CONSISTENT
    assert findings[0].explanation == "The evidence confirms the name."
    assert findings[0].evidence_ids == ["e1"]
    assert findings[0].claim_value == "ABC"
    assert findings[0].evidence_value == "ABC"


def test_llm_hallucinated_evidence_id_is_sanitized():
    llm = MagicMock()
    service = EvidenceComparisonService(llm)

    claims = [create_claim("c1")]
    evidence_list = [create_evidence("e1", ["c1"])]

    llm.extract_structured.return_value = ComparisonEvaluation(
        status=FindingStatus.CONSISTENT,
        explanation="...",
        evidence_ids=["e1", "hallucinated-id-123"],
    )

    findings = service.generate_findings(claims, evidence_list)

    assert len(findings) == 1
    # Ensure hallucinated ID is stripped
    assert findings[0].evidence_ids == ["e1"]


def test_llm_failure_degrades_gracefully():
    llm = MagicMock()
    service = EvidenceComparisonService(llm)

    claims = [create_claim("c1")]
    evidence_list = [create_evidence("e1", ["c1"])]

    llm.extract_structured.side_effect = Exception("API Error")

    findings = service.generate_findings(claims, evidence_list)

    assert len(findings) == 1
    assert findings[0].status == FindingStatus.NEEDS_VERIFICATION
    assert "Manual verification required" in findings[0].explanation
    # Evidence is preserved so the user can verify it manually
    assert findings[0].evidence_ids == ["e1"]
