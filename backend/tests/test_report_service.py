from app.schemas.evidence import Evidence, EvidenceSourceType
from app.schemas.finding import Finding, FindingStatus
from app.schemas.supplier import Supplier
from app.services.report_service import ReportService


def create_supplier():
    return Supplier(name="ABC Corp", email="test@abc.com")


def create_finding(
    status: FindingStatus, field: str, evidence_ids=None, explanation="Exp"
):
    return Finding(
        id="f1",
        verification_id="ver-123",
        field=field,
        status=status,
        explanation=explanation,
        evidence_ids=evidence_ids or [],
    )


def create_evidence(eid: str):
    return Evidence(
        id=eid,
        verification_id="ver-123",
        field="address",
        value="123 Street",
        source_url="http://example.com",
        source_title="Example Title",
        source_type=EvidenceSourceType.WEB,
        claim_ids=["c1"],
    )


def test_all_consistent():
    service = ReportService()
    findings = [create_finding(FindingStatus.CONSISTENT, "address")]

    report = service.generate_report(
        "ver-1", create_supplier(), 100.0, "USD", findings, []
    )

    assert report.summary.total == 1
    assert report.summary.consistent == 1
    assert len(report.recommended_actions) == 0


def test_mixed_findings():
    service = ReportService()
    findings = [
        create_finding(FindingStatus.CONSISTENT, "name"),
        create_finding(FindingStatus.MISMATCH, "address"),
        create_finding(FindingStatus.NOT_FOUND, "gst_number"),
        create_finding(FindingStatus.NEEDS_VERIFICATION, "product_or_service"),
    ]

    report = service.generate_report(
        "ver-1", create_supplier(), 100.0, "USD", findings, []
    )

    assert report.summary.total == 4
    assert report.summary.consistent == 1
    assert report.summary.mismatches == 1
    assert report.summary.not_found == 1
    assert report.summary.needs_verification == 1

    assert len(report.recommended_actions) == 3
    assert any("registered business address" in a for a in report.recommended_actions)
    assert any("GST certificate" in a for a in report.recommended_actions)
    assert any("product catalogue" in a for a in report.recommended_actions)


def test_evidence_mapping():
    service = ReportService()
    findings = [create_finding(FindingStatus.CONSISTENT, "address", ["e1", "e999"])]
    evidence_list = [create_evidence("e1")]

    report = service.generate_report(
        "ver-1", create_supplier(), 100.0, "USD", findings, evidence_list
    )

    sources = report.findings[0].sources
    assert len(sources) == 1
    assert sources[0].id == "e1"
    assert sources[0].source_url == "http://example.com"
    assert sources[0].source_title == "Example Title"


def test_empty_findings():
    service = ReportService()
    report = service.generate_report("ver-1", create_supplier(), None, None, [], [])

    assert report.summary.total == 0
    assert len(report.findings) == 0
    assert report.purchase_amount is None


def test_explanation_is_preserved():
    service = ReportService()
    findings = [
        create_finding(
            FindingStatus.NEEDS_VERIFICATION, "address", [], "Provider timeout"
        )
    ]

    report = service.generate_report(
        "ver-1", create_supplier(), 100.0, "USD", findings, []
    )

    assert report.findings[0].explanation == "Provider timeout"
