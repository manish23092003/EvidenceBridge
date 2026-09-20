from typing import Type, TypeVar

# Import google-genai SDK
from google import genai
from google.genai import types
from pydantic import BaseModel

from app.config import get_settings
from app.providers.llm import LLMProvider

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model

        # Initialize lazily to prevent validation errors during dependency injection
        self._client: genai.Client | None = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if self.api_key:
                self._client = genai.Client(api_key=self.api_key)
            else:
                self._client = genai.Client()
        return self._client

    def extract_structured(
        self,
        text: str,
        response_model: Type[T],
        system_instruction: str,
    ) -> T:
        """
        Calls Gemini to extract structured output using JSON schema constraint.
        """
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_model,
            temperature=0.0,  # Zero temperature for deterministic extraction
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=text,
            config=config,
        )

        # genai SDK when response_schema is set, might return parsed JSON string
        # We can validate it with Pydantic
        if not response.text:
            raise RuntimeError("Gemini returned empty structured output.")

        return response_model.model_validate_json(response.text)
