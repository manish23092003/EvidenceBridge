from app.config import get_settings
from app.schemas.claim import Claim
from app.schemas.research_planning import ResearchPurpose, ResearchQuery


class ResearchPlannerService:
    def __init__(self) -> None:
        self.settings = get_settings()

        # Fields that should not produce web searches on their own
        self.excluded_fields = {
            "purchase_amount",
            "currency",
            "payment_terms",
            "delivery_terms",
            "warranty_terms",
            "quote_number",
            "quote_date",
        }

    def _normalize_value(self, value: str) -> str:
        return value.strip()

    def plan(self, claims: list[Claim]) -> list[ResearchQuery]:
        if not claims:
            return []

        # Find the primary supplier name
        supplier_name = None
        for c in claims:
            if c.field == "supplier_name" and c.value.strip():
                supplier_name = self._normalize_value(c.value)
                break

        queries_dict: dict[str, ResearchQuery] = {}

        def add_query(query_str: str, purpose: ResearchPurpose, claim_id: str) -> None:
            q = query_str.strip()
            if not q:
                return

            if q in queries_dict:
                # Deduplicate and retain traceability
                if claim_id not in queries_dict[q].claim_ids:
                    queries_dict[q].claim_ids.append(claim_id)
            else:
                queries_dict[q] = ResearchQuery(
                    query=q, purpose=purpose, claim_ids=[claim_id]
                )

        for c in claims:
            if c.id is None:
                continue

            field = c.field
            if field in self.excluded_fields:
                continue

            val = self._normalize_value(c.value)
            if not val:
                continue

            if field == "supplier_name":
                add_query(f'"{val}"', ResearchPurpose.IDENTITY, c.id)

            elif field == "website":
                if supplier_name:
                    add_query(
                        f'"{supplier_name}" official website',
                        ResearchPurpose.WEBSITE,
                        c.id,
                    )
                else:
                    add_query(f'"{val}"', ResearchPurpose.WEBSITE, c.id)

            elif field == "address":
                if supplier_name:
                    add_query(
                        f'"{supplier_name}" "{val}"', ResearchPurpose.ADDRESS, c.id
                    )
                else:
                    add_query(f'"{val}"', ResearchPurpose.ADDRESS, c.id)

            elif field == "gst_number":
                if supplier_name:
                    add_query(
                        f'"{supplier_name}" "{val}"', ResearchPurpose.REGISTRATION, c.id
                    )
                else:
                    add_query(f'"{val}"', ResearchPurpose.REGISTRATION, c.id)

            elif field == "product_or_service":
                if supplier_name:
                    add_query(
                        f'"{supplier_name}" "{val}"', ResearchPurpose.PRODUCT, c.id
                    )
                # If no supplier name, product is too generic to search safely, skip it.

            elif field == "phone" or field == "email":
                if supplier_name:
                    add_query(
                        f'"{supplier_name}" "{val}"', ResearchPurpose.CONTACT, c.id
                    )
                else:
                    add_query(f'"{val}"', ResearchPurpose.CONTACT, c.id)

        # Sort the accumulated queries
        # 1. By Purpose Priority
        # 2. Then alphabetically by query string (for deterministic output
        # within the same priority)
        sorted_queries = sorted(
            queries_dict.values(), key=lambda rq: (rq.purpose.priority(), rq.query)
        )

        return sorted_queries[: self.settings.research_max_queries]
