#!/usr/bin/env python3
"""Structured output example demonstrating Pydantic models and validation."""

import asyncio
import json
import logging
from datetime import datetime

from research_agent import research_topic
from research_agent.config import get_settings
from research_agent.models import ResearchQuery, ResearchResponse


def demonstrate_input_validation():
    """Demonstrate input validation with ResearchQuery model."""
    print("🔍 Input Validation Examples")
    print("=" * 40)

    # Valid query
    try:
        valid_query = ResearchQuery(
            query="machine learning applications in healthcare",
            max_results=15,
            include_snippets=True,
        )
        print("✅ Valid query created:")
        print(f"   Query: {valid_query.query}")
        print(f"   Max results: {valid_query.max_results}")
        print(f"   Include snippets: {valid_query.include_snippets}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test validation errors
    validation_tests = [
        ("Empty query", {"query": ""}),
        ("Whitespace query", {"query": "   \n\t   "}),
        ("Too long query", {"query": "a" * 501}),
        ("Invalid max_results (too low)", {"query": "test", "max_results": 0}),
        ("Invalid max_results (too high)", {"query": "test", "max_results": 25}),
    ]

    print("\n🚫 Validation Error Examples:")
    for test_name, params in validation_tests:
        try:
            ResearchQuery(**params)
            print(f"❌ {test_name}: Should have failed!")
        except Exception as e:
            print(f"✅ {test_name}: {str(e)[:60]}...")


def demonstrate_output_structure(response: ResearchResponse):
    """Demonstrate structured output analysis."""
    print("📊 Structured Output Analysis")
    print("=" * 40)

    # Model validation
    print("✅ Response passed Pydantic validation")
    print(f"🔍 Query: {response.query}")
    print(f"📄 Summary length: {len(response.summary)} characters")
    print(f"🔑 Key findings: {len(response.key_findings)} items")
    print(f"📚 Sources: {len(response.sources)} items")
    print(f"🤔 Follow-ups: {len(response.follow_up_suggestions)} items")
    print(f"⏰ Timestamp: {response.timestamp}")

    # Data type verification
    print("\n📋 Data Type Verification:")
    print(f"   query: {type(response.query).__name__}")
    print(f"   summary: {type(response.summary).__name__}")
    print(f"   key_findings: {type(response.key_findings).__name__}")
    print(f"   sources: {type(response.sources).__name__}")
    print(f"   follow_up_suggestions: {type(response.follow_up_suggestions).__name__}")
    print(f"   timestamp: {type(response.timestamp).__name__}")

    # Source structure analysis
    if response.sources:
        print("\n📚 Source Structure Analysis:")
        for i, source in enumerate(response.sources[:2], 1):  # Show first 2
            print(f"   Source {i}:")
            print(f"     title: {type(source.title).__name__} - {len(source.title)} chars")
            print(f"     url: {type(source.url).__name__} - {source.url[:30]}...")
            print(f"     snippet: {type(source.snippet).__name__} - {len(source.snippet)} chars")
            print(f"     relevance_score: {type(source.relevance_score).__name__}")


def export_to_json(response: ResearchResponse, filename: str = None):
    """Demonstrate JSON serialization of structured response."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_export_{timestamp}.json"

    try:
        # Convert to JSON using Pydantic's built-in serialization
        json_data = response.model_dump(mode="json")

        # Pretty print JSON structure
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

        print("💾 JSON Export Preview:")
        print("=" * 40)
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)

        # Save to file (optional)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_str)

        print(f"\n✅ Exported to: {filename}")
        print(f"📊 File size: {len(json_str)} bytes")

    except Exception as e:
        print(f"❌ Export error: {e}")


def analyze_response_quality(response: ResearchResponse):
    """Analyze the quality and completeness of research response."""
    print("🎯 Response Quality Analysis")
    print("=" * 40)

    quality_checks = []

    # Summary quality
    if len(response.summary) >= 100:
        quality_checks.append("✅ Summary is comprehensive (≥100 chars)")
    else:
        quality_checks.append("⚠️  Summary might be too brief (<100 chars)")

    # Key findings quality
    if len(response.key_findings) >= 3:
        quality_checks.append(f"✅ Good number of key findings ({len(response.key_findings)})")
    else:
        quality_checks.append(f"⚠️  Limited key findings ({len(response.key_findings)})")

    # Source diversity
    if response.sources:
        unique_domains = set()
        for source in response.sources:
            try:
                from urllib.parse import urlparse

                domain = urlparse(source.url).netloc
                unique_domains.add(domain)
            except Exception:
                pass

        if len(unique_domains) >= 3:
            quality_checks.append(f"✅ Diverse sources ({len(unique_domains)} domains)")
        else:
            quality_checks.append(f"⚠️  Limited source diversity ({len(unique_domains)} domains)")
    else:
        quality_checks.append("❌ No sources found")

    # Follow-up quality
    if response.follow_up_suggestions:
        quality_checks.append(
            f"✅ Follow-up suggestions provided ({len(response.follow_up_suggestions)})"
        )
    else:
        quality_checks.append("⚠️  No follow-up suggestions")

    for check in quality_checks:
        print(f"   {check}")

    # Overall score
    passed_checks = sum(1 for check in quality_checks if check.startswith("✅"))
    total_checks = len(quality_checks)
    score = (passed_checks / total_checks) * 100

    print(f"\n📊 Overall Quality Score: {score:.1f}% ({passed_checks}/{total_checks})")


async def main():
    """Run structured output demonstration."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    try:
        config = get_settings()
        print("🏗️  Research Agent - Structured Output Example")
        print("=" * 50)

        # Demonstrate input validation
        demonstrate_input_validation()

        # Conduct research with valid input
        print(f"\n{'=' * 50}")
        print("🔄 Conducting Research with Structured Output")
        print("=" * 50)

        query = "blockchain technology applications in supply chain management"
        print(f"Research Query: {query}")

        # Create validated query object
        research_query = ResearchQuery(query=query, max_results=8, include_snippets=True)

        print(f"✅ Query validated: {research_query.query}")
        print("-" * 50)

        # Conduct research
        result = await research_topic(research_query.query, config)

        print(f"\n{'=' * 50}")
        # Analyze structured output
        demonstrate_output_structure(result)

        print(f"\n{'=' * 50}")
        # Analyze response quality
        analyze_response_quality(result)

        print(f"\n{'=' * 50}")
        # Export to JSON
        export_to_json(result)

        print(f"\n{'=' * 50}")
        print("📋 Complete Structured Response:")
        print("=" * 50)

        # Display full structured response
        print(f"🔍 Query: {result.query}")
        print(f"\n📝 Summary:\n{result.summary}")

        print("\n🔑 Key Findings:")
        for i, finding in enumerate(result.key_findings, 1):
            print(f"   {i}. {finding}")

        print("\n📚 Sources:")
        for i, source in enumerate(result.sources, 1):
            print(f"   {i}. {source.title}")
            print(f"      URL: {source.url}")
            print(f"      Snippet: {source.snippet[:100]}...")

        print("\n🤔 Follow-up Suggestions:")
        for i, suggestion in enumerate(result.follow_up_suggestions, 1):
            print(f"   {i}. {suggestion}")

        print(f"\n⏰ Research Timestamp: {result.timestamp}")

    except Exception as e:
        print(f"❌ Error in structured output example: {e}")
        print("\n💡 Ensure environment variables are set:")
        print("   - BRAVE_API_KEY: Your Brave Search API key")
        print("   - OPENAI_API_KEY: Your OpenAI API key")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
