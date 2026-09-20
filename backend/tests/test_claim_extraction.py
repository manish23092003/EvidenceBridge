from datetime import datetime
from typing import Type

import pytest
from pydantic import ValidationError

from app.config import get_settings
from app.schemas.claim import ClaimSource
from app.schemas.claim_extraction import ClaimExtractionResult, ExtractedClaim
from app.services.claim_extraction_service import (
    ClaimExtractionInputError,
    ClaimExtractionProviderError,
    ClaimExtractionService,
    ClaimExtractionValidationError,
)


class MockLLMProvider:
    def __init__(self, result: ClaimExtractionResult | Exception):
        self.result = result
        self.calls = []

    def extract_structured(
        self, text: str, response_model: Type, system_instruction: str
    ):
        self.calls.append({"text": text})
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def test_valid_extraction_multiple_claims():
    mock_result = ClaimExtractionResult(
        claims=[
            ExtractedClaim(field="supplier_name", value="ABC Industrial Solutions"),
            ExtractedClaim(field="address", value="Bengaluru"),
            ExtractedClaim(field="product_or_service", value="CNC component"),
            ExtractedClaim(field="purchase_amount", value="₹180000"),
            ExtractedClaim(field="payment_terms", value="50% advance"),
        ]
    )
    provider = MockLLMProvider(mock_result)
    service = ClaimExtractionService(provider)

    claims = service.extract_claims(
        (
            "ABC Industrial Solutions in Bengaluru quoted ₹180000 for CNC "
            "component with 50% advance."
        ),
        "ver-123",
    )

    assert len(claims) == 5
    assert claims[0].field == "supplier_name"
    assert claims[0].value == "ABC Industrial Solutions"
    assert claims[1].field == "address"
    assert claims[2].field == "product_or_service"

    # Check currency preservation
    assert claims[3].field == "purchase_amount"
    assert claims[3].value == "₹180000"

    # Check payment terms preservation
    assert claims[4].field == "payment_terms"
    assert claims[4].value == "50% advance"

    # Check UUID and source ownership
    assert claims[0].id is not None
    assert claims[0].verification_id == "ver-123"
    assert claims[0].source == ClaimSource.DOCUMENT
    assert isinstance(claims[0].created_at, datetime)


def test_missing_values_and_no_guessing():
    # Only supplier_name extracted
    mock_result = ClaimExtractionResult(
        claims=[ExtractedClaim(field="supplier_name", value="ABC Industrial Solutions")]
    )
    provider = MockLLMProvider(mock_result)
    service = ClaimExtractionService(provider)

    claims = service.extract_claims("Supplier is ABC Industrial Solutions", "ver-123")

    # Assert no other fields were magically generated
    assert len(claims) == 1
    assert claims[0].field == "supplier_name"
    fields_present = [c.field for c in claims]
    assert "website" not in fields_present
    assert "address" not in fields_present
    assert "gst_number" not in fields_present


def test_empty_input():
    provider = MockLLMProvider(ClaimExtractionResult(claims=[]))
    service = ClaimExtractionService(provider)

    with pytest.raises(ClaimExtractionInputError, match="cannot be empty"):
        service.extract_claims("", "ver-123")

    with pytest.raises(ClaimExtractionInputError, match="cannot be empty"):
        service.extract_claims("   \n  ", "ver-123")


def test_oversized_input(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "claim_extraction_max_chars", 10)

    provider = MockLLMProvider(ClaimExtractionResult(claims=[]))
    service = ClaimExtractionService(provider)

    with pytest.raises(
        ClaimExtractionInputError, match="exceeds maximum allowed length"
    ):
        service.extract_claims("This is longer than 10 chars", "ver-123")

    assert len(provider.calls) == 0


def test_provider_failure():
    provider = MockLLMProvider(RuntimeError("API Timeout"))
    service = ClaimExtractionService(provider)

    with pytest.raises(ClaimExtractionProviderError, match="API Timeout"):
        service.extract_claims("Valid text", "ver-123")


def test_invalid_structured_output():
    # Simulate a validation error from Pydantic inside the provider or service
    # By making the provider throw ValidationError natively.
    from pydantic import BaseModel

    class BadModel(BaseModel):
        val: int

    try:
        BadModel.model_validate({"val": "not_an_int"})
    except ValidationError as e:
        real_error = e

    provider = MockLLMProvider(real_error)
    service = ClaimExtractionService(provider)

    with pytest.raises(
        ClaimExtractionValidationError, match="Failed to validate LLM output"
    ):
        service.extract_claims("Valid text", "ver-123")
