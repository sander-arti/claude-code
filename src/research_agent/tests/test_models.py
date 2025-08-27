"""Tests for Pydantic models validation and behavior."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from ..models import BraveSearchResponse, ResearchQuery, ResearchResponse, SearchResult


class TestResearchQuery:
    """Test ResearchQuery model validation."""

    def test_valid_query(self):
        """Test creating a valid research query."""
        query = ResearchQuery(query="Python programming best practices")
        assert query.query == "Python programming best practices"
        assert query.max_results == 10  # default value
        assert query.include_snippets is True  # default value

    def test_query_with_custom_params(self):
        """Test query with custom parameters."""
        query = ResearchQuery(
            query="Machine learning algorithms", max_results=15, include_snippets=False
        )
        assert query.query == "Machine learning algorithms"
        assert query.max_results == 15
        assert query.include_snippets is False

    def test_empty_query_validation(self):
        """Test that empty queries are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ResearchQuery(query="")

        assert "String should have at least 1 character" in str(exc_info.value)

    def test_whitespace_only_query_validation(self):
        """Test that whitespace-only queries are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ResearchQuery(query="   \n\t   ")

        assert "Query cannot be empty or only whitespace" in str(exc_info.value)

    def test_query_length_validation(self):
        """Test query length limits."""
        # Test maximum length
        long_query = "a" * 501
        with pytest.raises(ValidationError):
            ResearchQuery(query=long_query)

        # Test acceptable length
        acceptable_query = "a" * 500
        query = ResearchQuery(query=acceptable_query)
        assert len(query.query) == 500

    def test_max_results_validation(self):
        """Test max_results field validation."""
        # Test minimum boundary
        with pytest.raises(ValidationError):
            ResearchQuery(query="test", max_results=0)

        # Test maximum boundary
        with pytest.raises(ValidationError):
            ResearchQuery(query="test", max_results=21)

        # Test valid boundaries
        query_min = ResearchQuery(query="test", max_results=1)
        assert query_min.max_results == 1

        query_max = ResearchQuery(query="test", max_results=20)
        assert query_max.max_results == 20

    def test_query_cleanup(self):
        """Test that queries are properly cleaned."""
        query = ResearchQuery(query="  Python programming  \n")
        assert query.query == "Python programming"


class TestSearchResult:
    """Test SearchResult model validation."""

    def test_valid_search_result(self):
        """Test creating a valid search result."""
        result = SearchResult(
            title="Python Programming Guide",
            url="https://example.com/python-guide",
            snippet="Learn Python programming with this comprehensive guide.",
        )
        assert result.title == "Python Programming Guide"
        assert result.url == "https://example.com/python-guide"
        assert result.snippet == "Learn Python programming with this comprehensive guide."
        assert result.relevance_score is None

    def test_search_result_with_relevance_score(self):
        """Test search result with relevance score."""
        result = SearchResult(
            title="Test Title", url="https://test.com", snippet="Test snippet", relevance_score=0.85
        )
        assert result.relevance_score == 0.85

    def test_url_validation(self):
        """Test URL validation."""
        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://test.com/path",
            "https://subdomain.example.com/path?query=value",
        ]

        for url in valid_urls:
            result = SearchResult(title="Test", url=url, snippet="Test snippet")
            assert result.url == url

        # Invalid URLs
        invalid_urls = ["ftp://example.com", "example.com", "www.example.com", ""]

        for url in invalid_urls:
            with pytest.raises(ValidationError):
                SearchResult(title="Test", url=url, snippet="Test snippet")

    def test_relevance_score_validation(self):
        """Test relevance score boundary validation."""
        # Valid scores
        for score in [0.0, 0.5, 1.0]:
            result = SearchResult(
                title="Test", url="https://test.com", snippet="Test", relevance_score=score
            )
            assert result.relevance_score == score

        # Invalid scores
        for score in [-0.1, 1.1, -1.0, 2.0]:
            with pytest.raises(ValidationError):
                SearchResult(
                    title="Test", url="https://test.com", snippet="Test", relevance_score=score
                )


class TestResearchResponse:
    """Test ResearchResponse model validation."""

    def test_valid_research_response(self):
        """Test creating a valid research response."""
        response = ResearchResponse(
            query="Python programming",
            summary="Python is a versatile programming language.",
            key_findings=["Python is beginner-friendly", "Great for data science"],
            sources=[
                SearchResult(
                    title="Python Guide",
                    url="https://python.org",
                    snippet="Official Python documentation",
                )
            ],
            follow_up_suggestions=["Learn about Python frameworks", "Explore data libraries"],
        )

        assert response.query == "Python programming"
        assert response.summary == "Python is a versatile programming language."
        assert len(response.key_findings) == 2
        assert len(response.sources) == 1
        assert len(response.follow_up_suggestions) == 2
        assert isinstance(response.timestamp, datetime)

    def test_empty_key_findings_validation(self):
        """Test that empty key_findings are rejected."""
        with pytest.raises(ValidationError):
            ResearchResponse(
                query="test",
                summary="Test summary with enough characters",
                key_findings=[],  # Empty list should fail
                sources=[],
            )

    def test_short_key_findings_validation(self):
        """Test that short key findings are filtered out."""
        with pytest.raises(ValidationError):
            ResearchResponse(
                query="test",
                summary="Test summary with enough characters",
                key_findings=["short"],  # Too short, should fail
                sources=[],
            )

    def test_key_findings_cleanup(self):
        """Test that key findings are properly cleaned."""
        response = ResearchResponse(
            query="test",
            summary="Test summary with enough characters",
            key_findings=[
                "  Valid finding with enough length  ",
                "Another valid finding here",
                "   ",  # Whitespace only - should be removed
                "too short",  # Too short - should be removed
                "This is a valid finding with sufficient length",
            ],
            sources=[],
        )

        # Should only keep valid findings
        assert len(response.key_findings) == 3
        assert "Valid finding with enough length" in response.key_findings
        assert "Another valid finding here" in response.key_findings
        assert "This is a valid finding with sufficient length" in response.key_findings

    def test_follow_up_suggestions_limit(self):
        """Test follow-up suggestions length limit."""
        suggestions = [f"Suggestion {i}" for i in range(10)]  # 10 suggestions

        with pytest.raises(ValidationError):
            ResearchResponse(
                query="test",
                summary="Test summary with enough characters",
                key_findings=["Valid finding with enough length"],
                sources=[],
                follow_up_suggestions=suggestions,  # Too many suggestions
            )

    def test_timestamp_default(self):
        """Test that timestamp defaults to current UTC time."""
        before = datetime.now(UTC)

        response = ResearchResponse(
            query="test",
            summary="Test summary with enough characters",
            key_findings=["Valid finding with enough length"],
            sources=[],
        )

        after = datetime.now(UTC)

        assert before <= response.timestamp <= after
        assert response.timestamp.tzinfo == UTC


class TestBraveSearchResponse:
    """Test BraveSearchResponse model validation."""

    def test_brave_search_response_defaults(self):
        """Test BraveSearchResponse with default values."""
        response = BraveSearchResponse()
        assert response.title == ""
        assert response.url == ""
        assert response.description == ""

    def test_brave_search_response_with_data(self):
        """Test BraveSearchResponse with actual data."""
        response = BraveSearchResponse(
            title="Test Title", url="https://test.com", description="Test description"
        )
        assert response.title == "Test Title"
        assert response.url == "https://test.com"
        assert response.description == "Test description"

    def test_extra_fields_ignored(self):
        """Test that extra fields from API are ignored."""
        data = {
            "title": "Test",
            "url": "https://test.com",
            "description": "Test desc",
            "extra_field": "should be ignored",
            "another_extra": 123,
        }

        response = BraveSearchResponse(**data)
        assert response.title == "Test"
        assert response.url == "https://test.com"
        assert response.description == "Test desc"
        # Extra fields should not be accessible
        assert not hasattr(response, "extra_field")
        assert not hasattr(response, "another_extra")
