"""Tests for Brave API integration tools."""

from unittest.mock import Mock

import httpx
import pytest
import re
from pydantic_ai import RunContext

from ..config import AgentConfig
from ..tools import _extract_search_sources, _format_search_results, brave_search


class TestBraveSearch:
    """Test Brave API integration functionality."""

    @pytest.fixture
    def mock_config(self) -> AgentConfig:
        """Provide test configuration."""
        return AgentConfig(
            brave_api_key="test_api_key",
            openai_api_key="test_openai_key",
            max_search_results=5,
            debug=False,
        )

    @pytest.fixture
    def mock_context(self, mock_config: AgentConfig) -> Mock:
        """Mock RunContext for testing."""
        context = Mock(spec=RunContext)
        context.deps = mock_config
        return context

    @pytest.mark.asyncio
    async def test_brave_search_success(self, mock_context: Mock, httpx_mock):
        """Test successful Brave API search."""
        # Mock successful API response
        mock_response = {
            "web": {
                "results": [
                    {
                        "title": "Python Programming Guide",
                        "url": "https://python.org/guide",
                        "description": "Learn Python programming basics",
                    },
                    {
                        "title": "Advanced Python Techniques",
                        "url": "https://advanced-python.com",
                        "description": "Advanced concepts in Python development",
                    },
                ]
            }
        }

        httpx_mock.add_response(
            url=re.compile(r"https://api\.search\.brave\.com/res/v1/web/search.*"),
            json=mock_response,
            status_code=200,
        )

        result = await brave_search(mock_context, "Python programming")

        # Verify result contains formatted search results
        assert "Python Programming Guide" in result
        assert "https://python.org/guide" in result
        assert "Learn Python programming basics" in result
        assert "Advanced Python Techniques" in result
        assert "Result 1:" in result
        assert "Result 2:" in result

    @pytest.mark.asyncio
    async def test_brave_search_empty_query(self, mock_context: Mock):
        """Test that empty queries raise ValueError."""
        with pytest.raises(ValueError, match="Search query cannot be empty"):
            await brave_search(mock_context, "")

        with pytest.raises(ValueError, match="Search query cannot be empty"):
            await brave_search(mock_context, "   ")

    @pytest.mark.asyncio
    async def test_brave_search_no_results(self, mock_context: Mock, httpx_mock):
        """Test handling when no search results are returned."""
        # Mock API response with no results
        mock_response = {"web": {"results": []}}

        httpx_mock.add_response(
            url=re.compile(r"https://api\.search\.brave\.com/res/v1/web/search.*"),
            json=mock_response,
            status_code=200,
        )

        result = await brave_search(mock_context, "very obscure query")

        assert "No search results found" in result
        assert "very obscure query" in result

    @pytest.mark.asyncio
    async def test_brave_search_http_error(self, mock_context: Mock, httpx_mock):
        """Test handling of HTTP errors from Brave API."""
        # Mock API error response
        httpx_mock.add_response(
            url=re.compile(r"https://api\.search\.brave\.com/res/v1/web/search.*"),
            status_code=429,  # Rate limited
            text="Rate limit exceeded",
        )

        result = await brave_search(mock_context, "test query")

        assert "Search failed due to API error" in result

    @pytest.mark.asyncio
    async def test_brave_search_network_error(self, mock_context: Mock, httpx_mock):
        """Test handling of network errors."""
        # Mock network error
        httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

        result = await brave_search(mock_context, "test query")

        assert "Search failed due to network error" in result

    @pytest.mark.asyncio
    async def test_brave_search_request_parameters(self, mock_context: Mock, httpx_mock):
        """Test that correct parameters are sent to Brave API."""
        mock_response = {"web": {"results": []}}

        httpx_mock.add_response(
            url=re.compile(r"https://api\.search\.brave\.com/res/v1/web/search.*"),
            json=mock_response,
            status_code=200,
        )

        await brave_search(mock_context, "Python programming")

        # Verify request was made with correct parameters
        requests = httpx_mock.get_requests()
        assert len(requests) > 0, "No requests were made"
        request = requests[0]

        # Check headers
        assert request.headers["Accept"] == "application/json"
        assert request.headers["X-Subscription-Token"] == "test_api_key"
        assert "User-Agent" in request.headers

        # Check query parameters
        params = dict(request.url.params)
        assert params["q"] == "Python programming"
        assert params["count"] == "5"  # From mock_config.max_search_results
        assert params["search_lang"] == "en"
        assert params["country"] == "us"

    @pytest.mark.asyncio
    async def test_brave_search_debug_logging(self, mock_config: AgentConfig, httpx_mock):
        """Test debug logging functionality."""
        # Enable debug mode
        mock_config.debug = True

        context = Mock(spec=RunContext)
        context.deps = mock_config

        mock_response = {"web": {"results": []}}
        httpx_mock.add_response(
            url=re.compile(r"https://api\.search\.brave\.com/res/v1/web/search.*"),
            json=mock_response,
            status_code=200,
        )

        # This should not raise any errors and should complete successfully
        result = await brave_search(context, "test query")
        assert "No search results found" in result


class TestFormatSearchResults:
    """Test search results formatting functionality."""

    def test_format_search_results_normal_case(self):
        """Test formatting with normal search results."""
        results = [
            {
                "title": "First Result",
                "url": "https://first.com",
                "description": "First description",
            },
            {
                "title": "Second Result",
                "url": "https://second.com",
                "description": "Second description",
            },
        ]

        formatted = _format_search_results(results, max_results=2)

        assert "Result 1:" in formatted
        assert "Result 2:" in formatted
        assert "First Result" in formatted
        assert "https://first.com" in formatted
        assert "First description" in formatted
        assert "Second Result" in formatted
        assert "=" * 50 in formatted  # Separator

    def test_format_search_results_missing_fields(self):
        """Test formatting with missing fields in results."""
        results = [
            {
                "title": "Complete Result",
                "url": "https://complete.com",
                "description": "Complete description",
            },
            {
                # Missing title and description
                "url": "https://incomplete.com"
            },
            {},  # Empty result
        ]

        formatted = _format_search_results(results, max_results=3)

        assert "Complete Result" in formatted
        assert "No title" in formatted
        assert "No description" in formatted
        assert "https://incomplete.com" in formatted

    def test_format_search_results_max_limit(self):
        """Test that max_results is respected."""
        results = [
            {"title": f"Result {i}", "url": f"https://result{i}.com", "description": f"Desc {i}"}
            for i in range(10)
        ]

        formatted = _format_search_results(results, max_results=3)

        # Should only contain first 3 results
        assert "Result 1:" in formatted
        assert "Result 2:" in formatted
        assert "Result 3:" in formatted
        assert "Result 4:" not in formatted

    def test_format_search_results_empty_list(self):
        """Test formatting with empty results list."""
        formatted = _format_search_results([], max_results=5)

        assert formatted == "No valid search results could be processed."

    def test_format_search_results_invalid_data(self):
        """Test handling of invalid result data."""
        results = [
            None,  # Invalid result
            {"title": "Valid Result", "url": "https://valid.com", "description": "Valid desc"},
            {"invalid": "structure"},  # Invalid structure
        ]

        formatted = _format_search_results(results, max_results=3)

        # Should only process the valid result
        assert "Valid Result" in formatted
        # Note: None results are skipped, so the valid result becomes Result 2
        assert "Result 2:" in formatted


class TestExtractSearchSources:
    """Test source extraction functionality."""

    def test_extract_search_sources_valid_format(self):
        """Test extracting sources from properly formatted results."""
        formatted_results = """Result 1:
Title: Python Guide
URL: https://python.org
Description: Official Python documentation
==================================================

Result 2:
Title: Python Tutorial
URL: https://tutorial.python.org
Description: Learn Python programming
=================================================="""

        sources = _extract_search_sources(formatted_results)

        assert len(sources) == 2
        assert sources[0]["title"] == "Python Guide"
        assert sources[0]["url"] == "https://python.org"
        assert sources[0]["snippet"] == "Official Python documentation"
        assert sources[1]["title"] == "Python Tutorial"
        assert sources[1]["url"] == "https://tutorial.python.org"

    def test_extract_search_sources_malformed_input(self):
        """Test handling of malformed input."""
        # Test with incomplete sections
        malformed_input = "Result 1:\nTitle: Incomplete"

        sources = _extract_search_sources(malformed_input)

        # Should handle gracefully, possibly returning empty list or partial data
        assert isinstance(sources, list)

    def test_extract_search_sources_empty_input(self):
        """Test with empty input."""
        sources = _extract_search_sources("")

        assert sources == []

    def test_extract_search_sources_no_separators(self):
        """Test input without proper separators."""
        input_without_separators = "Just some text without proper formatting"

        sources = _extract_search_sources(input_without_separators)

        assert isinstance(sources, list)
        # Might be empty or contain partial data depending on implementation
