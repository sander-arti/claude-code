"""Tool implementations for research agent with Brave API integration."""

import logging

import httpx
from pydantic_ai import RunContext

from .config import AgentConfig
from .models import BraveSearchResponse

logger = logging.getLogger(__name__)


async def brave_search(ctx: RunContext[AgentConfig], query: str) -> str:
    """Search Brave API and return formatted results for AI processing.

    Args:
        ctx: RunContext containing agent configuration and dependencies
        query: Search query string to research

    Returns:
        Formatted string containing search results for AI analysis

    Raises:
        ValueError: If query is empty or invalid
    """
    # Validate input
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")

    cleaned_query = query.strip()
    config = ctx.deps

    if config.debug:
        logger.info(f"Searching Brave API for query: {cleaned_query}")

    # Prepare request headers and parameters
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": config.brave_api_key,
        "User-Agent": "Research-Agent/1.0",
    }

    params = {
        "q": cleaned_query,
        "count": config.max_search_results,
        "search_lang": config.search_language,
        "country": config.search_country,
        "safesearch": "moderate",
        "freshness": "pd",  # Past day for fresh results
    }

    url = "https://api.search.brave.com/res/v1/web/search"

    try:
        async with httpx.AsyncClient(timeout=config.timeout_seconds) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()

            if config.debug:
                logger.info(f"Brave API response status: {response.status_code}")

            # Parse API response
            data = response.json()
            web_results = data.get("web", {}).get("results", [])

            if not web_results:
                return f"No search results found for query: {cleaned_query}"

            # Format results for AI processing
            formatted_results = _format_search_results(web_results, config.max_search_results)

            if config.debug:
                logger.info(f"Formatted {len(web_results)} search results")

            return formatted_results

    except httpx.HTTPStatusError as e:
        error_msg = f"Brave API HTTP error {e.response.status_code}: {e.response.text}"
        logger.error(error_msg)
        return "Search failed due to API error. Please try again later."

    except httpx.RequestError as e:
        error_msg = f"Brave API request error: {str(e)}"
        logger.error(error_msg)
        return "Search failed due to network error. Please check your connection."

    except Exception as e:
        error_msg = f"Unexpected error during search: {str(e)}"
        logger.error(error_msg)
        return "Search encountered an unexpected error. Please try again."


def _format_search_results(results: list[dict], max_results: int) -> str:
    """Format Brave API search results for AI processing.

    Args:
        results: Raw results from Brave API
        max_results: Maximum number of results to include

    Returns:
        Formatted string with search results
    """
    formatted_results = []

    for i, result in enumerate(results[:max_results], 1):
        # Parse result using Pydantic model for validation
        try:
            search_result = BraveSearchResponse(
                title=result.get("title", "No title"),
                url=result.get("url", "No URL"),
                description=result.get("description", "No description"),
            )

            formatted_result = (
                f"Result {i}:\n"
                f"Title: {search_result.title}\n"
                f"URL: {search_result.url}\n"
                f"Description: {search_result.description}\n"
                f"{'=' * 50}"
            )
            formatted_results.append(formatted_result)

        except Exception as e:
            logger.warning(f"Failed to parse search result {i}: {e}")
            continue

    if not formatted_results:
        return "No valid search results could be processed."

    return "\n\n".join(formatted_results)


def _extract_search_sources(formatted_results: str) -> list[dict]:
    """Extract structured source data from formatted search results.

    Args:
        formatted_results: Formatted search results string

    Returns:
        List of source dictionaries for ResearchResponse
    """
    sources = []

    # Simple extraction logic - in production, this could be more sophisticated
    sections = formatted_results.split("=" * 50)

    for section in sections:
        if not section.strip():
            continue

        lines = [line.strip() for line in section.split("\n") if line.strip()]

        if len(lines) >= 3:
            try:
                title = lines[1].replace("Title: ", "") if "Title: " in lines[1] else "Unknown"
                url = lines[2].replace("URL: ", "") if "URL: " in lines[2] else ""
                description = (
                    lines[3].replace("Description: ", "")
                    if len(lines) > 3 and "Description: " in lines[3]
                    else ""
                )

                sources.append(
                    {
                        "title": title,
                        "url": url,
                        "snippet": description,
                        "relevance_score": None,
                    }
                )
            except IndexError:
                continue

    return sources
