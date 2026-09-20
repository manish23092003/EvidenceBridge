from typing import Protocol, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(Protocol):
    def extract_structured(
        self,
        text: str,
        response_model: Type[T],
        system_instruction: str,
    ) -> T:
        """
        Extracts structured data from the provided text using the given
        system instructions.
        """
        ...
