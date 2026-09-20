from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    app_name: str = "EvidenceBridge"

    # PDF Processing Settings
    pdf_max_size_mb: int = 10
    pdf_max_pages: int = 20

    # Claim Extraction Settings
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    claim_extraction_max_chars: int = 50000

    environment: str = "development"
    log_level: str = "info"

    # Anakin Configuration
    anakin_api_key: str = ""
    anakin_search_limit: int = 5
    anakin_timeout_seconds: int = 30

    # Research Planner Settings
    research_max_queries: int = 5

    database_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()


def get_settings() -> Settings:
    return settings
