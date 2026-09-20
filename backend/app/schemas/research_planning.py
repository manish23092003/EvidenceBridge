from enum import Enum

from pydantic import BaseModel, Field


class ResearchPurpose(str, Enum):
    IDENTITY = "IDENTITY"
    WEBSITE = "WEBSITE"
    REGISTRATION = "REGISTRATION"
    ADDRESS = "ADDRESS"
    PRODUCT = "PRODUCT"
    CONTACT = "CONTACT"
    GENERAL_PRESENCE = "GENERAL_PRESENCE"

    # Custom sort order to prioritize queries
    def priority(self) -> int:
        priorities = {
            self.IDENTITY: 1,
            self.WEBSITE: 2,
            self.REGISTRATION: 3,
            self.ADDRESS: 4,
            self.PRODUCT: 5,
            self.CONTACT: 6,
            self.GENERAL_PRESENCE: 7,
        }
        return priorities[self]


class ResearchQuery(BaseModel):
    query: str = Field(description="The actual web search query")
    claim_ids: list[str] = Field(
        description="IDs of the claims this query investigates"
    )
    purpose: ResearchPurpose = Field(description="The primary purpose of this query")
