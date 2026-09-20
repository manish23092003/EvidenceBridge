import uuid
from datetime import datetime, timezone

from pydantic import ValidationError

from app.config import get_settings
from app.providers.llm import LLMProvider
from app.schemas.claim import Claim, ClaimSource
from app.schemas.claim_extraction import ClaimExtractionResult


class ClaimExtractionError(Exception):
    pass


class ClaimExtractionInputError(ClaimExtractionError):
    pass


class ClaimExtractionProviderError(ClaimExtractionError):
    pass


class ClaimExtractionValidationError(ClaimExtractionError):
    pass


SYSTEM_INSTRUCTION = """You are a precise data extraction agent.
Your task is to extract supplier details from the provided document text.

You must output a structured list of 'Claim' objects matching the 
expected schema.
SUPPORTED FIELDS TO EXTRACT:
supplier_name, website, address, email, phone, product_or_service, 
purchase_amount, currency, payment_terms, delivery_terms, 
warranty_terms, gst_number, quote_number, quote_date

RULES:
1. Extract ONLY information explicitly stated in the text.
2. NEVER guess or infer missing values.
3. If a supported field is absent from the text, DO NOT create an 
   extraction claim for it.
4. Preserve numbers, currency symbols, company names, addresses, 
   and phone/email details exactly as they appear.
5. Normalize obvious formatting noise (like random line breaks) 
   but preserve the core value.
6. You are an extractor, NOT a verifier. Do not judge legitimacy or 
   infer facts from general knowledge.
7. Return a list of only the fields you found explicitly in the text.
"""


class ClaimExtractionService:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.settings = get_settings()

    def extract_claims(self, text: str, verification_id: str) -> list[Claim]:
        if not text or not text.strip():
            raise ClaimExtractionInputError("Input text cannot be empty.")

        if len(text) > self.settings.claim_extraction_max_chars:
            raise ClaimExtractionInputError(
                f"Input text exceeds maximum allowed length of "
                f"{self.settings.claim_extraction_max_chars} characters."
            )

        try:
            result = self.provider.extract_structured(
                text=text,
                response_model=ClaimExtractionResult,
                system_instruction=SYSTEM_INSTRUCTION,
            )
        except ValidationError as e:
            raise ClaimExtractionValidationError(
                f"Failed to validate LLM output: {str(e)}"
            ) from e
        except Exception as e:
            # Catching general provider issues (e.g. timeout, API errors)
            raise ClaimExtractionProviderError(f"LLM Provider failed: {str(e)}") from e

        claims: list[Claim] = []
        now = datetime.now(timezone.utc)

        for extracted_claim in result.claims:
            claims.append(
                Claim(
                    id=str(uuid.uuid4()),
                    verification_id=verification_id,
                    field=extracted_claim.field,
                    value=extracted_claim.value,
                    source=ClaimSource.DOCUMENT,
                    created_at=now,
                )
            )

        return claims
