import json
import uuid
from typing import List

from app.providers.llm import LLMProvider
from app.schemas.claim import Claim
from app.schemas.evidence import Evidence
from app.schemas.evidence_comparison import ComparisonEvaluation
from app.schemas.finding import Finding, FindingStatus, utc_now

COMPARISON_SYSTEM_PROMPT = """You are a rigorous, objective data comparison engine. 
Your task is to compare a supplier's explicitly stated 'Claim' against a provided 
set of 'Evidence' items gathered from the web.

You must output a structured evaluation matching the ComparisonEvaluation schema.

RULES:
1. ONLY evaluate based on the provided evidence. DO NOT use external 
   knowledge. DO NOT invent facts.
2. The 'status' must be one of:
   - CONSISTENT: The evidence clearly and directly supports the claim.
   - MISMATCH: The evidence clearly contradicts the claim.
   - NEEDS_VERIFICATION: The evidence is ambiguous, partial, or does not 
     clearly prove or disprove the claim.
   - NOT_FOUND: No relevant evidence was provided to evaluate the claim.
3. The 'explanation' must be concise and reference the evidence.
4. The 'evidence_ids' MUST ONLY contain IDs from the provided evidence 
   list. DO NOT invent IDs.
5. You MUST NEVER declare a supplier "trustworthy", "fraudulent", or 
   "legitimate". You are ONLY evaluating the specific field provided.
6. The 'evidence_value' should be a short quote or value extracted directly 
   from the evidence that supports the conclusion.
"""


class EvidenceComparisonService:
    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    def generate_findings(
        self, claims: List[Claim], evidence_list: List[Evidence]
    ) -> List[Finding]:
        findings: List[Finding] = []

        for claim in claims:
            # 1. Gather all evidence associated with this claim
            associated_evidence = [
                e for e in evidence_list if claim.id and claim.id in e.claim_ids
            ]

            # 2. Handle NOT_FOUND locally without calling LLM
            if not associated_evidence:
                findings.append(
                    Finding(
                        id=str(uuid.uuid4()),
                        verification_id=claim.verification_id,
                        field=claim.field,
                        status=FindingStatus.NOT_FOUND,
                        claim_value=claim.value,
                        evidence_value=None,
                        explanation="No evidence was found for this claim.",
                        evidence_ids=[],
                        created_at=utc_now(),
                    )
                )
                continue

            # 3. Call LLM for comparison
            prompt = self._build_prompt(claim, associated_evidence)

            # Use structured extraction with the generic ComparisonEvaluation schema
            try:
                evaluation = self.llm_provider.extract_structured(
                    text=prompt,
                    response_model=ComparisonEvaluation,
                    system_instruction=COMPARISON_SYSTEM_PROMPT,
                )

                # Sanitize evidence IDs to guarantee no hallucinations leak through
                valid_evidence_ids = [e.id for e in associated_evidence]
                safe_evidence_ids = [
                    eid for eid in evaluation.evidence_ids if eid in valid_evidence_ids
                ]

                findings.append(
                    Finding(
                        id=str(uuid.uuid4()),
                        verification_id=claim.verification_id,
                        field=claim.field,
                        status=evaluation.status,
                        claim_value=claim.value,
                        evidence_value=evaluation.evidence_value,
                        explanation=evaluation.explanation,
                        evidence_ids=safe_evidence_ids,
                        created_at=utc_now(),
                    )
                )
            except Exception:
                # If LLM fails, degrade gracefully to NEEDS_VERIFICATION
                valid_evidence_ids = [e.id for e in associated_evidence]
                findings.append(
                    Finding(
                        id=str(uuid.uuid4()),
                        verification_id=claim.verification_id,
                        field=claim.field,
                        status=FindingStatus.NEEDS_VERIFICATION,
                        claim_value=claim.value,
                        evidence_value=None,
                        explanation=(
                            "Failed to automatically compare evidence. "
                            "Manual verification required."
                        ),
                        evidence_ids=valid_evidence_ids,
                        created_at=utc_now(),
                    )
                )

        return findings

    def _build_prompt(self, claim: Claim, associated_evidence: List[Evidence]) -> str:
        evidence_dicts = [
            {"id": e.id, "source_title": e.source_title, "snippet_or_content": e.value}
            for e in associated_evidence
        ]

        return f"""
Claim Details:
- Field: {claim.field}
- Value: {claim.value}

Provided Evidence:
{json.dumps(evidence_dicts, indent=2)}

Please evaluate the claim against the provided evidence.
"""
