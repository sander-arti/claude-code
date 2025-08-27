#!/usr/bin/env python3
"""Conversation memory example demonstrating follow-up research with context."""

import asyncio
import logging

from research_agent import ResearchSession
from research_agent.config import get_settings


async def main():
    """Run conversation memory example with follow-up questions."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    try:
        # Load configuration
        config = get_settings()
        print("🧠 Research Agent - Conversation Memory Example")
        print("=" * 50)

        # Create research session for maintaining context
        session = ResearchSession(config)

        # Research sequence demonstrating conversation memory
        research_sequence = [
            "artificial intelligence trends 2024",
            "What are the ethical concerns with AI?",
            "How do these concerns apply to generative AI specifically?",
            "What regulations are being proposed for AI safety?",
        ]

        print("🔄 Conducting sequential research with conversation context...")
        print("=" * 60)

        for i, query in enumerate(research_sequence, 1):
            print(f"\n🔍 Research {i}/4: {query}")
            print("-" * 40)

            # Conduct research with session context
            result = await session.research(query)

            # Display concise results
            print(f"📝 Summary: {result.summary[:150]}...")
            print(f"🔑 Key Findings: {len(result.key_findings)} insights")
            print(f"📚 Sources: {len(result.sources)} references")
            print(f"🤔 Follow-ups: {len(result.follow_up_suggestions)} suggestions")

            # Show some key findings
            if result.key_findings:
                print("💡 Top Insights:")
                for finding in result.key_findings[:2]:  # Show first 2
                    print(f"   • {finding[:80]}...")

        # Display session summary
        print("\n" + "=" * 60)
        print("📊 Research Session Summary")
        print("=" * 60)
        print(session.get_research_summary())

        # Show how context builds over time
        print("\n🔗 Conversation Context Evolution:")
        for i, research in enumerate(session.research_history, 1):
            print(f"   {i}. {research.query}")

        print(
            f"\n✅ Completed {len(session.research_history)} research queries with maintained context"
        )

        # Example of how follow-up questions can reference previous research
        print("\n" + "=" * 60)
        print("💬 Example Follow-up Query:")
        print("=" * 60)

        followup_query = (
            "Based on our previous discussion, what are the most promising AI safety solutions?"
        )
        print(f"Query: {followup_query}")

        result = await session.research(followup_query)
        print(f"📝 AI Response: {result.summary[:200]}...")

        print(f"\n🎯 Total research queries in session: {len(session.research_history)}")

    except Exception as e:
        print(f"❌ Error in conversation example: {e}")
        print("\n💡 Make sure you have set the required environment variables:")
        print("   - BRAVE_API_KEY: Your Brave Search API key")
        print("   - OPENAI_API_KEY: Your OpenAI API key")
        return 1

    return 0


async def interactive_research_session():
    """Interactive research session for manual testing."""
    config = get_settings()
    session = ResearchSession(config)

    print("🧠 Interactive Research Session")
    print("=" * 40)
    print("Type your research questions. Type 'quit' to exit.")
    print("The agent will remember previous context for follow-up questions.")
    print("-" * 40)

    while True:
        try:
            query = input("\n🔍 Research query: ").strip()

            if query.lower() in ["quit", "exit", "q"]:
                break

            if not query:
                continue

            print("🔄 Researching...")
            result = await session.research(query)

            print(f"\n📝 Summary:\n{result.summary}")

            if result.key_findings:
                print("\n🔑 Key Findings:")
                for i, finding in enumerate(result.key_findings, 1):
                    print(f"  {i}. {finding}")

            if result.follow_up_suggestions:
                print("\n🤔 Suggested follow-ups:")
                for i, suggestion in enumerate(result.follow_up_suggestions, 1):
                    print(f"  {i}. {suggestion}")

            print(f"\n📊 Session: {len(session.research_history)} queries completed")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

    print(f"\n✅ Session completed with {len(session.research_history)} research queries")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_research_session())
    else:
        exit_code = asyncio.run(main())
        exit(exit_code)
