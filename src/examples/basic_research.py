#!/usr/bin/env python3
"""Basic research example demonstrating simple topic research."""

import asyncio
import logging

from research_agent import research_topic
from research_agent.config import get_settings


async def main():
    """Run basic research example."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    try:
        # Load configuration from environment
        config = get_settings()
        print("🔍 Research Agent - Basic Research Example")
        print("=" * 50)

        # Define research query
        query = "sustainable energy solutions 2024"
        print(f"Research Query: {query}")
        print("-" * 50)

        # Conduct research
        print("🔄 Conducting research...")
        result = await research_topic(query, config)

        # Display results
        print("\n📊 Research Results:")
        print("=" * 50)

        print(f"\n🎯 Query: {result.query}")

        print("\n📝 Summary:")
        print(result.summary)

        print(f"\n🔑 Key Findings ({len(result.key_findings)}):")
        for i, finding in enumerate(result.key_findings, 1):
            print(f"  {i}. {finding}")

        print(f"\n📚 Sources ({len(result.sources)}):")
        for i, source in enumerate(result.sources, 1):
            print(f"  {i}. {source.title}")
            print(f"     URL: {source.url}")
            print(f"     Snippet: {source.snippet[:100]}...")
            if source.relevance_score:
                print(f"     Relevance: {source.relevance_score:.2f}")
            print()

        print(f"🤔 Follow-up Suggestions ({len(result.follow_up_suggestions)}):")
        for i, suggestion in enumerate(result.follow_up_suggestions, 1):
            print(f"  {i}. {suggestion}")

        print(f"\n⏰ Research completed at: {result.timestamp}")

    except Exception as e:
        print(f"❌ Error conducting research: {e}")
        print("\n💡 Make sure you have set the following environment variables:")
        print("   - BRAVE_API_KEY: Your Brave Search API key")
        print("   - OPENAI_API_KEY: Your OpenAI API key (if using OpenAI)")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
