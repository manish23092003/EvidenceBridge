import uuid
from typing import Dict

from app.schemas.claim import Claim
from app.schemas.evidence import Evidence, EvidenceSourceType, utc_now
from app.schemas.research_execution import (
    ResearchExecutionResult,
    ResearchExecutionStatus,
)


class EvidenceService:
    def normalize_research_results(
        self, execution_result: ResearchExecutionResult, original_claims: list[Claim]
    ) -> list[Evidence]:
        """
        Converts successful web research results into normalized Evidence objects.
        Requires original_claims to map the verification_id and field correctly.
        """
        evidence_list: list[Evidence] = []

        # Build lookup for claims to easily find verification_id and field
        claim_lookup: Dict[str, Claim] = {c.id: c for c in original_claims if c.id}

        # Track seen evidence to avoid duplicates
        # uniqueness key: (source_url, tuple(sorted(claim_ids)))
        seen = set()

        for query_item in execution_result.queries:
            if query_item.status != ResearchExecutionStatus.SUCCESS:
                continue

            if not query_item.results:
                continue

            # If no claim IDs are associated, we can't reliably trace this evidence
            if not query_item.claim_ids:
                continue

            # Extract verification_id and field from the primary claim
            primary_claim_id = query_item.claim_ids[0]
            primary_claim = claim_lookup.get(primary_claim_id)
            if not primary_claim:
                continue

            verification_id = primary_claim.verification_id

            # If multiple claims, we can just use the purpose or
            # the primary claim's field.
            # The prompt example shows field="address" which matches the claim.
            field = primary_claim.field

            sorted_claim_ids = tuple(sorted(query_item.claim_ids))

            for res in query_item.results:
                # Prefer full content if available, fallback to snippet
                value = getattr(res, "content", None) or res.snippet
                value = value.strip() if value else ""

                if not value:
                    continue

                # Deduplication key
                url = res.url or ""
                uniq_key = (url, sorted_claim_ids)
                if uniq_key in seen:
                    continue

                seen.add(uniq_key)

                evidence = Evidence(
                    id=str(uuid.uuid4()),
                    verification_id=verification_id,
                    field=field,
                    value=value,
                    source_url=res.url,
                    source_title=res.title,
                    snippet=res.snippet,
                    source_type=EvidenceSourceType.WEB,
                    claim_ids=list(query_item.claim_ids),
                    created_at=utc_now(),
                )
                evidence_list.append(evidence)

        return evidence_list
