from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.schemas.evidence import Evidence
from app.schemas.finding import Finding, FindingStatus
from app.schemas.supplier import Supplier


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VerificationReportSummary(BaseModel):
    total: int
    consistent: int
    mismatches: int
    needs_verification: int
    not_found: int
    summary_text: str


class ReportEvidenceReference(BaseModel):
    id: str
    source_url: str | None = None
    source_title: str | None = None


class ReportFinding(BaseModel):
    field: str
    status: FindingStatus
    claim_value: str | None = None
    explanation: str
    evidence_ids: list[str] = Field(default_factory=list)
    sources: list[ReportEvidenceReference] = Field(default_factory=list)


class VerificationReport(BaseModel):
    verification_id: str
    supplier_name: str
    purchase_amount: float | None = None
    currency: str | None = None
    summary: VerificationReportSummary
    findings: list[ReportFinding] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)


class ReportRequest(BaseModel):
    verification_id: str
    supplier: Supplier
    purchase_amount: float | None = None
    currency: str | None = None
    findings: list[Finding]
    evidence: list[Evidence]
