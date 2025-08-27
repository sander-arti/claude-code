"""Pydantic models for research agent requests and responses."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator


class ResearchQuery(BaseModel):
    """Model for research query input with validation.

    Validates user queries and search parameters to ensure valid API calls.
    """

    query: str = Field(
        ..., min_length=1, max_length=500, description="The research topic or question"
    )
    max_results: int = Field(
        default=10, ge=1, le=20, description="Maximum number of search results"
    )
    include_snippets: bool = Field(default=True, description="Include result snippets in response")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and clean the research query."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Query cannot be empty or only whitespace")
        return cleaned


class SearchResult(BaseModel):
    """Model for individual search results from Brave API.

    Represents a single search result with metadata and content.
    """

    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="URL of the search result")
    snippet: str = Field(..., description="Content snippet from the result")
    relevance_score: float | None = Field(
        None, ge=0.0, le=1.0, description="Relevance score if available"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Basic URL validation."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class ResearchResponse(BaseModel):
    """Structured response model for research results.

    Contains analyzed research findings with sources and suggestions.
    """

    query: str = Field(..., description="Original research query")
    summary: str = Field(..., min_length=10, description="AI-generated summary of findings")
    key_findings: list[str] = Field(
        default_factory=list, min_length=1, description="Key insights extracted from search results"
    )
    sources: list[SearchResult] = Field(
        default_factory=list, description="Source search results used for analysis"
    )
    follow_up_suggestions: list[str] = Field(
        default_factory=list, max_length=5, description="Suggested follow-up research questions"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the research was conducted",
    )

    @field_validator("key_findings")
    @classmethod
    def validate_findings(cls, v: list[str]) -> list[str]:
        """Ensure findings are meaningful."""
        if not v:
            raise ValueError("At least one key finding is required")

        cleaned_findings = []
        for finding in v:
            cleaned = finding.strip()
            if cleaned and len(cleaned) >= 10:
                cleaned_findings.append(cleaned)

        if not cleaned_findings:
            raise ValueError("All findings must be at least 10 characters long")

        return cleaned_findings

    model_config = {
        "use_enum_values": True,
        "populate_by_name": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
        },
    }


class BraveSearchResponse(BaseModel):
    """Model for raw Brave API search response.

    Internal model for parsing Brave API responses before processing.
    """

    title: str = ""
    url: str = ""
    description: str = ""

    model_config = {
        "extra": "ignore",  # Ignore extra fields from API
    }
