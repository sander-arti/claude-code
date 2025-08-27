"""Main research agent implementation using Pydantic AI."""

import logging

from pydantic_ai import Agent

from .config import AgentConfig
from .models import ResearchResponse
from .tools import brave_search

logger = logging.getLogger(__name__)


# Module-level agent instance following Pydantic AI best practices
research_agent = Agent(
    model="test",  # Default test model, will be overridden by config
    deps_type=AgentConfig,
    output_type=ResearchResponse,
    system_prompt="""You are an expert research assistant that helps users conduct comprehensive topic research.

Your role is to:
1. Use the brave_search tool to gather relevant information about research topics
2. Analyze search results critically and synthesize key insights
3. Provide structured, factual research summaries
4. Suggest meaningful follow-up research questions
5. Always cite sources and maintain accuracy

Guidelines:
- Always search for information before providing analysis
- Synthesize information from multiple sources when possible
- Focus on factual, verifiable information
- Identify key themes and important insights
- Suggest specific, actionable follow-up questions
- Be objective and balanced in your analysis
- If search results are limited, acknowledge this limitation
""",
    tools=[brave_search],
)


async def research_topic(query: str, config: AgentConfig) -> ResearchResponse:
    """Conduct comprehensive research on a given topic.

    Args:
        query: The research topic or question to investigate
        config: Agent configuration with API keys and settings

    Returns:
        Structured research response with findings and sources

    Raises:
        ValidationError: If the query is invalid
        RuntimeError: If research fails due to API or model errors
    """
    logger.info(f"Starting research for query: {query}")

    try:
        # Configure agent with proper model based on config
        model_string = f"{config.model_provider}:{config.model_name}"

        # Run the agent with the research query
        result = await research_agent.run(
            query,
            model=model_string,
            deps=config,
        )

        if config.debug:
            logger.info(f"Research completed successfully for query: {query}")

        return result.data

    except Exception as e:
        error_msg = f"Research failed for query '{query}': {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def create_research_agent(config: AgentConfig) -> Agent[AgentConfig, ResearchResponse]:
    """Create a configured research agent instance.

    Args:
        config: Agent configuration

    Returns:
        Configured Agent instance ready for research tasks
    """
    model_string = f"{config.model_provider}:{config.model_name}"

    # Create agent with dynamic configuration
    agent = Agent(
        model=model_string,
        deps_type=AgentConfig,
        output_type=ResearchResponse,
        system_prompt="""You are an expert research assistant specializing in comprehensive topic analysis.

When conducting research:
1. Always use the brave_search tool first to gather current information
2. Analyze search results to identify key themes and insights
3. Synthesize information from multiple sources
4. Provide factual, well-structured summaries
5. Generate meaningful follow-up research questions
6. Always cite your sources

Your responses should be:
- Factual and evidence-based
- Well-organized and clear
- Comprehensive yet concise
- Balanced and objective
- Properly sourced

Focus on providing value through synthesis and analysis, not just information retrieval.""",
        tools=[brave_search],
    )

    return agent


class ResearchSession:
    """Research session handler for maintaining conversation context.

    Provides conversation memory and context management for follow-up queries.
    """

    def __init__(self, config: AgentConfig):
        """Initialize research session with configuration.

        Args:
            config: Agent configuration for API keys and settings
        """
        self.config = config
        self.agent = create_research_agent(config)
        self.research_history: list[ResearchResponse] = []

    async def research(self, query: str) -> ResearchResponse:
        """Conduct research with session context.

        Args:
            query: Research topic or follow-up question

        Returns:
            Research response with context from session history
        """
        # Add context from previous research if available
        context_prompt = query
        if self.research_history:
            previous_topics = [r.query for r in self.research_history[-3:]]  # Last 3 queries
            context_prompt = f"""Previous research context: {", ".join(previous_topics)}

Current query: {query}

Please provide research on the current query, and consider connections to previous research topics where relevant."""

        result = await self.agent.run(
            context_prompt,
            deps=self.config,
        )

        # Store result in session history
        self.research_history.append(result.data)

        return result.data

    def get_research_summary(self) -> str:
        """Get a summary of all research conducted in this session.

        Returns:
            Summary text of research session
        """
        if not self.research_history:
            return "No research conducted in this session."

        topics = [r.query for r in self.research_history]
        return f"Research session summary: Investigated {len(topics)} topics: {', '.join(topics)}"
