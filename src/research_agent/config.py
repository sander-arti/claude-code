"""Configuration management for the research agent using pydantic-settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class AgentConfig(BaseSettings):
    """Application settings with validation for research agent.

    Uses environment variables for configuration with sensible defaults.
    All API keys and sensitive configuration should be provided via environment.
    """

    # API Configuration
    brave_api_key: str = Field(..., env="BRAVE_API_KEY")
    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")

    # Model Configuration
    model_provider: str = Field(default="openai", env="MODEL_PROVIDER")
    model_name: str = Field(default="gpt-4", env="MODEL_NAME")

    # Search Configuration
    max_search_results: int = Field(default=10, env="MAX_SEARCH_RESULTS", ge=1, le=20)
    search_language: str = Field(default="en", env="SEARCH_LANGUAGE")
    search_country: str = Field(default="us", env="SEARCH_COUNTRY")

    # Agent Configuration
    max_retries: int = Field(default=3, env="MAX_RETRIES", ge=0, le=10)
    timeout_seconds: int = Field(default=30, env="TIMEOUT_SECONDS", ge=1, le=300)

    # Debug Configuration
    debug: bool = Field(default=False, env="DEBUG")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> AgentConfig:
    """Get cached settings instance.

    Returns:
        Cached AgentConfig instance for efficient reuse

    Raises:
        ValidationError: If required environment variables are missing or invalid
    """
    return AgentConfig()
