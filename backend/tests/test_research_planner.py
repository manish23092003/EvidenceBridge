import uuid
from datetime import datetime

from app.config import get_settings
from app.schemas.claim import Claim, ClaimSource
from app.schemas.research_planning import ResearchPurpose
from app.services.research_planner import ResearchPlannerService


def create_claim(field: str, value: str) -> Claim:
    return Claim(
        id=str(uuid.uuid4()),
        verification_id="ver-123",
        field=field,
        value=value,
        source=ClaimSource.DOCUMENT,
        created_at=datetime.utcnow(),
    )


def test_supplier_name_produces_identity():
    planner = ResearchPlannerService()
    c = create_claim("supplier_name", "ABC Industrial Solutions")
    queries = planner.plan([c])

    assert len(queries) == 1
    assert queries[0].purpose == ResearchPurpose.IDENTITY
    assert queries[0].query == '"ABC Industrial Solutions"'
    assert c.id in queries[0].claim_ids


def test_website_produces_website_query():
    planner = ResearchPlannerService()
    c1 = create_claim("supplier_name", "ABC")
    c2 = create_claim("website", "www.abc.com")
    queries = planner.plan([c1, c2])

    assert len(queries) == 2
    website_q = next(q for q in queries if q.purpose == ResearchPurpose.WEBSITE)
    assert website_q.query == '"ABC" official website'
    assert c2.id in website_q.claim_ids


def test_address_produces_supplier_address():
    planner = ResearchPlannerService()
    c1 = create_claim("supplier_name", "ABC")
    c2 = create_claim("address", "Bengaluru")
    queries = planner.plan([c1, c2])

    address_q = next(q for q in queries if q.purpose == ResearchPurpose.ADDRESS)
    assert address_q.query == '"ABC" "Bengaluru"'


def test_gst_produces_supplier_gst():
    planner = ResearchPlannerService()
    c1 = create_claim("supplier_name", "ABC")
    c2 = create_claim("gst_number", "29ABCDE1234F1Z5")
    queries = planner.plan([c1, c2])

    gst_q = next(q for q in queries if q.purpose == ResearchPurpose.REGISTRATION)
    assert gst_q.query == '"ABC" "29ABCDE1234F1Z5"'


def test_product_produces_supplier_product():
    planner = ResearchPlannerService()
    c1 = create_claim("supplier_name", "ABC")
    c2 = create_claim("product_or_service", "CNC machine")
    queries = planner.plan([c1, c2])

    prod_q = next(q for q in queries if q.purpose == ResearchPurpose.PRODUCT)
    assert prod_q.query == '"ABC" "CNC machine"'


def test_phone_email_produces_contact():
    planner = ResearchPlannerService()
    c1 = create_claim("supplier_name", "ABC")
    c2 = create_claim("phone", "9876543210")
    c3 = create_claim("email", "info@abc.com")
    queries = planner.plan([c1, c2, c3])

    contact_qs = [q for q in queries if q.purpose == ResearchPurpose.CONTACT]
    assert len(contact_qs) == 2
    queries_str = {q.query for q in contact_qs}
    assert '"ABC" "9876543210"' in queries_str
    assert '"ABC" "info@abc.com"' in queries_str


def test_procurement_only_fields():
    planner = ResearchPlannerService()
    fields = [
        "purchase_amount",
        "currency",
        "payment_terms",
        "delivery_terms",
        "warranty_terms",
        "quote_number",
        "quote_date",
    ]
    claims = [create_claim(f, "val") for f in fields]

    queries = planner.plan(claims)
    assert len(queries) == 0


def test_missing_supplier_name():
    planner = ResearchPlannerService()
    c1 = create_claim("address", "Bengaluru")
    c2 = create_claim("gst_number", "123")
    c3 = create_claim(
        "product_or_service", "generic product"
    )  # Should be ignored without supplier
    queries = planner.plan([c1, c2, c3])

    assert len(queries) == 2
    queries_str = {q.query for q in queries}
    assert '"Bengaluru"' in queries_str
    assert '"123"' in queries_str


def test_empty_values():
    planner = ResearchPlannerService()
    c1 = create_claim("supplier_name", "   ")
    c2 = create_claim("address", "")
    queries = planner.plan([c1, c2])
    assert len(queries) == 0


def test_deduplication():
    planner = ResearchPlannerService()
    c1 = create_claim("supplier_name", "ABC")
    c2 = create_claim("supplier_name", "ABC")
    queries = planner.plan([c1, c2])

    assert len(queries) == 1
    assert len(queries[0].claim_ids) == 2
    assert c1.id in queries[0].claim_ids
    assert c2.id in queries[0].claim_ids


def test_query_limit_and_priority(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "research_max_queries", 2)
    planner = ResearchPlannerService()

    claims = [
        create_claim("phone", "123"),  # CONTACT (Priority 6)
        create_claim("address", "BLR"),  # ADDRESS (Priority 4)
        create_claim("website", "abc.com"),  # WEBSITE (Priority 2)
        create_claim("supplier_name", "ABC"),  # IDENTITY (Priority 1)
    ]

    queries = planner.plan(claims)

    assert len(queries) == 2
    assert queries[0].purpose == ResearchPurpose.IDENTITY
    assert queries[1].purpose == ResearchPurpose.WEBSITE


def test_determinism():
    planner = ResearchPlannerService()
    claims = [
        create_claim("phone", "123"),
        create_claim("address", "BLR"),
        create_claim("supplier_name", "ABC"),
        create_claim("gst_number", "GST1"),
    ]

    q1 = planner.plan(claims)
    q2 = planner.plan(claims)

    assert [q.query for q in q1] == [q.query for q in q2]
