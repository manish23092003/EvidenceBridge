import pytest
from pydantic import ValidationError

from app.schemas import (
    Claim,
    ClaimSource,
    Evidence,
    EvidenceSourceType,
    Finding,
    FindingStatus,
    Supplier,
    VerificationRequest,
    VerificationStatus,
)


def test_supplier_valid_required_data():
    supplier = Supplier(id="sup-1", name="Test Supplier")
    assert supplier.id == "sup-1"
    assert supplier.name == "Test Supplier"
    assert supplier.website is None
    assert supplier.created_at is not None


def test_supplier_missing_required_name():
    with pytest.raises(ValidationError):
        Supplier(id="sup-1")


def test_supplier_valid_optional_fields():
    supplier = Supplier(
        id="sup-2",
        name="Tech Corp",
        website="https://techcorp.example.com",
        location="Bengaluru",
        email="contact@techcorp.example.com",
        phone="+919876543210",
        product_or_service="IT Services",
    )
    assert supplier.website == "https://techcorp.example.com"
    assert supplier.email == "contact@techcorp.example.com"


def test_verification_request_default_status():
    req = VerificationRequest(id="ver-1", supplier_id="sup-1", purchase_amount=100.0)
    assert req.status == VerificationStatus.PENDING
    assert req.currency == "INR"
    assert req.created_at is not None


def test_verification_request_non_negative_amount():
    req = VerificationRequest(id="ver-2", supplier_id="sup-1", purchase_amount=0.0)
    assert req.purchase_amount == 0.0


def test_verification_request_reject_negative_amount():
    with pytest.raises(ValidationError):
        VerificationRequest(id="ver-3", supplier_id="sup-1", purchase_amount=-50.0)


def test_claim_valid_source_enum():
    claim = Claim(
        id="claim-1",
        verification_id="ver-1",
        field="website",
        value="example.com",
        source=ClaimSource.DOCUMENT,
    )
    assert claim.source == ClaimSource.DOCUMENT


def test_claim_required_fields():
    with pytest.raises(ValidationError):
        Claim(
            id="claim-2", verification_id="ver-1", field="phone"
        )  # missing value and source


def test_evidence_optional_source_url():
    evidence = Evidence(
        id="ev-1",
        verification_id="ver-1",
        field="location",
        value="Bengaluru",
        source_type=EvidenceSourceType.WEB,
    )
    assert evidence.source_url is None


def test_evidence_valid_source_type():
    evidence = Evidence(
        id="ev-2",
        verification_id="ver-1",
        field="product",
        value="Steel pipes",
        source_type=EvidenceSourceType.USER_PROVIDED,
    )
    assert evidence.source_type == EvidenceSourceType.USER_PROVIDED


def test_finding_valid_status():
    finding = Finding(
        id="find-1",
        verification_id="ver-1",
        field="website",
        status=FindingStatus.CONSISTENT,
        explanation="The website exactly matches the document.",
    )
    assert finding.status == FindingStatus.CONSISTENT


def test_finding_required_explanation():
    with pytest.raises(ValidationError):
        Finding(
            id="find-2",
            verification_id="ver-1",
            field="website",
            status=FindingStatus.MISMATCH,
        )  # missing explanation


def test_finding_evidence_id_list():
    finding = Finding(
        id="find-3",
        verification_id="ver-1",
        field="website",
        status=FindingStatus.NEEDS_VERIFICATION,
        explanation="Evidence is ambiguous.",
        evidence_ids=["ev-1", "ev-2"],
    )
    assert finding.evidence_ids == ["ev-1", "ev-2"]


def test_schema_serialization():
    supplier = Supplier(id="s-1", name="Export Inc", email="export@inc.com")
    data = supplier.model_dump()
    assert data["id"] == "s-1"
    assert data["name"] == "Export Inc"
    assert data["email"] == "export@inc.com"
