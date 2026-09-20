from app.schemas.evidence import Evidence
from app.schemas.finding import Finding, FindingStatus
from app.schemas.report import (
    ReportEvidenceReference,
    ReportFinding,
    VerificationReport,
    VerificationReportSummary,
)
from app.schemas.supplier import Supplier


class ReportService:
    def generate_report(
        self,
        verification_id: str,
        supplier: Supplier,
        purchase_amount: float | None,
        currency: str | None,
        findings: list[Finding],
        evidence_list: list[Evidence],
    ) -> VerificationReport:
        # 1. Summary logic
        total = len(findings)
        consistent = sum(1 for f in findings if f.status == FindingStatus.CONSISTENT)
        mismatches = sum(1 for f in findings if f.status == FindingStatus.MISMATCH)
        needs_verification = sum(
            1 for f in findings if f.status == FindingStatus.NEEDS_VERIFICATION
        )
        not_found = sum(1 for f in findings if f.status == FindingStatus.NOT_FOUND)

        summary_text = (
            f"{total} supplier claims were evaluated. "
            f"{consistent} were consistent with available evidence, "
            f"{mismatches} showed a mismatch, and "
            f"{needs_verification} require further verification."
        )

        summary = VerificationReportSummary(
            total=total,
            consistent=consistent,
            mismatches=mismatches,
            needs_verification=needs_verification,
            not_found=not_found,
            summary_text=summary_text,
        )

        # 2. Evidence Mapping
        evidence_lookup = {e.id: e for e in evidence_list}

        report_findings = []
        recommended_actions_set = set()

        for f in findings:
            # Map sources safely
            sources = []
            for eid in f.evidence_ids:
                if eid in evidence_lookup:
                    ev = evidence_lookup[eid]
                    sources.append(
                        ReportEvidenceReference(
                            id=ev.id,
                            source_url=ev.source_url,
                            source_title=ev.source_title,
                        )
                    )

            report_findings.append(
                ReportFinding(
                    field=f.field,
                    status=f.status,
                    claim_value=f.claim_value,
                    explanation=f.explanation,
                    evidence_ids=f.evidence_ids,
                    sources=sources,
                )
            )

            # 3. Recommended Actions
            action = self._generate_action(f.field, f.status)
            if action:
                recommended_actions_set.add(action)

        # Deterministic sorting of actions for predictability
        recommended_actions = sorted(list(recommended_actions_set))

        return VerificationReport(
            verification_id=verification_id,
            supplier_name=supplier.name or "Unknown Supplier",
            purchase_amount=purchase_amount,
            currency=currency,
            summary=summary,
            findings=report_findings,
            recommended_actions=recommended_actions,
        )

    def _generate_action(self, field: str, status: FindingStatus) -> str | None:
        if status == FindingStatus.CONSISTENT:
            return None

        if status == FindingStatus.MISMATCH:
            if field == "address":
                return "Ask the supplier to confirm the registered business address."
            if field == "website":
                return "Ask the supplier to confirm the official business website."
            if field == "supplier_name":
                return "Request an official incorporation certificate to verify the legal entity name."
            if field in ["phone", "email"]:
                return "Verify the provided contact details by attempting direct communication."
            return f"Request clarification regarding the mismatch in {field}."

        if status == FindingStatus.NOT_FOUND:
            if field == "gst_number":
                return "Request the supplier's GST certificate."
            if field == "website":
                return "Check if the supplier operates exclusively offline or under a parent company."
            return f"Request documentation to support the claim for {field}."

        if status == FindingStatus.NEEDS_VERIFICATION:
            if field == "product_or_service":
                return "Request a product catalogue or recent customer reference."
            return f"Request additional evidence to verify the {field}."

        return None
