"""Tests for research agent functionality using Pydantic AI test models."""

from unittest.mock import Mock, patch

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

from ..agent import ResearchSession, create_research_agent, research_agent, research_topic
from ..config import AgentConfig
from ..models import ResearchResponse


class TestResearchAgent:
    """Test the main research agent functionality."""

    @pytest.fixture
    def mock_config(self) -> AgentConfig:
        """Provide test configuration."""
        return AgentConfig(
            brave_api_key="test_brave_key",
            openai_api_key="test_openai_key",
            model_provider="test",
            model_name="test-model",
            max_search_results=5,
            debug=False,
        )

    @pytest.mark.asyncio
    async def test_research_topic_with_test_model(self, mock_config: AgentConfig):
        """Test research functionality using TestModel."""
        # Mock the brave_search tool to return test data
        with patch("src.research_agent.tools.brave_search") as mock_search:
            mock_search.return_value = """Result 1:
Title: Python Programming Guide
URL: https://python.org/guide
Description: Comprehensive Python programming guide
==================================================

Result 2:
Title: Python Best Practices
URL: https://python-practices.com
Description: Best practices for Python development
=================================================="""

            # Use TestModel for deterministic testing
            test_model = TestModel()

            # Override the global agent with TestModel
            test_agent = Agent(
                model=test_model,
                deps_type=AgentConfig,
                output_type=ResearchResponse,
                system_prompt=research_agent.system_prompt,
                tools=research_agent.tools,
            )

            # Use the test agent instead of the production agent
            with patch("research_agent.agent.research_agent", test_agent):
                result = await research_topic("Python programming", mock_config)

            # TestModel generates valid structured data
            assert isinstance(result, ResearchResponse)
            assert result.query
            assert result.summary
            assert isinstance(result.key_findings, list)
            assert isinstance(result.sources, list)
            assert isinstance(result.follow_up_suggestions, list)

    @pytest.mark.asyncio
    async def test_research_topic_with_function_model(self, mock_config: AgentConfig):
        """Test research functionality using FunctionModel for more control."""

        def custom_research_function(messages):
            """Custom function to simulate AI research response."""
            # Extract the user query from messages
            user_message = next((msg for msg in messages if msg.role == "user"), None)
            query_text = user_message.content if user_message else "unknown query"

            return ResearchResponse(
                query=query_text,
                summary=f"Research summary for: {query_text}",
                key_findings=[
                    "Key insight 1 from search results",
                    "Important finding 2 based on analysis",
                    "Critical discovery 3 from multiple sources",
                ],
                sources=[],  # Would be populated by brave_search tool
                follow_up_suggestions=["Explore related topic A", "Investigate aspect B further"],
            )

        # Create FunctionModel with custom function
        function_model = FunctionModel(custom_research_function)

        # Mock the brave_search tool
        with patch("src.research_agent.tools.brave_search") as mock_search:
            mock_search.return_value = "Mocked search results"

            # Override the global agent with FunctionModel
            test_agent = Agent(
                model=function_model,
                deps_type=AgentConfig,
                output_type=ResearchResponse,
                system_prompt=research_agent.system_prompt,
                tools=research_agent.tools,
            )

            with patch("research_agent.agent.research_agent", test_agent):
                result = await research_topic("Machine learning basics", mock_config)

            # Verify the custom response
            assert isinstance(result, ResearchResponse)
            assert "Machine learning basics" in result.query
            assert "Research summary for:" in result.summary
            assert len(result.key_findings) == 3
            assert "Key insight 1" in result.key_findings[0]
            assert len(result.follow_up_suggestions) == 2

    @pytest.mark.asyncio
    async def test_research_topic_error_handling(self, mock_config: AgentConfig):
        """Test error handling in research_topic function."""
        # Simulate an error during agent execution
        with patch("research_agent.agent.research_agent.run", side_effect=Exception("Model error")):
            with pytest.raises(RuntimeError, match="Research failed for query"):
                await research_topic("test query", mock_config)

    def test_create_research_agent(self, mock_config: AgentConfig):
        """Test research agent creation with custom config."""
        agent = create_research_agent(mock_config)

        assert isinstance(agent, Agent)
        assert agent.deps_type == AgentConfig
        assert agent.output_type == ResearchResponse
        # Tools should be attached
        assert len(agent.tools) > 0


class TestResearchSession:
    """Test research session functionality for conversation context."""

    @pytest.fixture
    def mock_config(self) -> AgentConfig:
        """Provide test configuration."""
        return AgentConfig(
            brave_api_key="test_brave_key",
            openai_api_key="test_openai_key",
            model_provider="test",
            model_name="test-model",
            debug=False,
        )

    def test_research_session_initialization(self, mock_config: AgentConfig):
        """Test research session initialization."""
        session = ResearchSession(mock_config)

        assert session.config == mock_config
        assert isinstance(session.agent, Agent)
        assert session.research_history == []

    @pytest.mark.asyncio
    async def test_research_session_single_query(self, mock_config: AgentConfig):
        """Test single research query in session."""
        session = ResearchSession(mock_config)

        # Mock the agent's run method
        mock_result = Mock()
        mock_result.data = ResearchResponse(
            query="Python basics",
            summary="Python is a programming language",
            key_findings=["Python is beginner-friendly"],
            sources=[],
            follow_up_suggestions=["Learn Python syntax"],
        )

        with patch.object(session.agent, "run", return_value=mock_result):
            result = await session.research("Python basics")

            assert isinstance(result, ResearchResponse)
            assert result.query == "Python basics"
            assert len(session.research_history) == 1

    @pytest.mark.asyncio
    async def test_research_session_context_building(self, mock_config: AgentConfig):
        """Test that session builds context from previous research."""
        session = ResearchSession(mock_config)

        # Add some history
        previous_research = [
            ResearchResponse(
                query="Python basics",
                summary="Python intro",
                key_findings=["Python is easy"],
                sources=[],
                follow_up_suggestions=[],
            ),
            ResearchResponse(
                query="Python frameworks",
                summary="Web frameworks",
                key_findings=["Django is popular"],
                sources=[],
                follow_up_suggestions=[],
            ),
        ]
        session.research_history = previous_research

        # Mock agent run to capture the context prompt
        captured_prompt = None

        def mock_run(prompt, deps):
            nonlocal captured_prompt
            captured_prompt = prompt
            mock_result = Mock()
            mock_result.data = ResearchResponse(
                query="Python testing",
                summary="Testing info",
                key_findings=["Testing is important"],
                sources=[],
                follow_up_suggestions=[],
            )
            return mock_result

        with patch.object(session.agent, "run", side_effect=mock_run):
            await session.research("Python testing")

            # Verify context was included in the prompt
            assert captured_prompt is not None
            assert "Previous research context:" in captured_prompt
            assert "Python basics" in captured_prompt
            assert "Python frameworks" in captured_prompt
            assert "Python testing" in captured_prompt

    def test_research_session_summary_empty(self, mock_config: AgentConfig):
        """Test session summary with no research."""
        session = ResearchSession(mock_config)

        summary = session.get_research_summary()

        assert "No research conducted" in summary

    def test_research_session_summary_with_history(self, mock_config: AgentConfig):
        """Test session summary with research history."""
        session = ResearchSession(mock_config)

        # Add research history
        session.research_history = [
            ResearchResponse(
                query="Topic A",
                summary="Summary A",
                key_findings=["Finding A"],
                sources=[],
                follow_up_suggestions=[],
            ),
            ResearchResponse(
                query="Topic B",
                summary="Summary B",
                key_findings=["Finding B"],
                sources=[],
                follow_up_suggestions=[],
            ),
        ]

        summary = session.get_research_summary()

        assert "Research session summary:" in summary
        assert "2 topics" in summary
        assert "Topic A" in summary
        assert "Topic B" in summary


class TestAgentIntegration:
    """Integration tests for agent functionality."""

    @pytest.fixture
    def mock_config(self) -> AgentConfig:
        """Provide test configuration."""
        return AgentConfig(
            brave_api_key="test_brave_key",
            openai_api_key="test_openai_key",
            model_provider="test",
            model_name="test-model",
            max_search_results=3,
            debug=True,
        )

    @pytest.mark.asyncio
    async def test_end_to_end_research_flow(self, mock_config: AgentConfig):
        """Test complete research flow from query to structured response."""

        # Mock brave_search to return realistic data
        with patch("src.research_agent.tools.brave_search") as mock_search:
            mock_search.return_value = """Result 1:
Title: Artificial Intelligence Overview
URL: https://ai-overview.com
Description: Comprehensive guide to AI concepts and applications
==================================================

Result 2:
Title: Machine Learning Basics
URL: https://ml-basics.org
Description: Introduction to machine learning algorithms
==================================================

Result 3:
Title: Deep Learning Fundamentals
URL: https://deeplearning.edu
Description: Neural networks and deep learning principles
=================================================="""

            # Use TestModel for predictable results
            test_model = TestModel()

            # Create agent with TestModel
            test_agent = Agent(
                model=test_model,
                deps_type=AgentConfig,
                output_type=ResearchResponse,
                system_prompt=research_agent.system_prompt,
                tools=research_agent.tools,
            )

            # Run the research
            with patch("research_agent.agent.research_agent", test_agent):
                result = await research_topic("artificial intelligence", mock_config)

            # Verify comprehensive response
            assert isinstance(result, ResearchResponse)
            assert result.query  # Should contain the query
            assert result.summary  # Should have AI-generated summary
            assert len(result.key_findings) > 0  # Should extract key insights
            assert isinstance(result.sources, list)  # Should have sources
            assert isinstance(result.follow_up_suggestions, list)  # Should suggest follow-ups
            assert result.timestamp  # Should have timestamp

            # Verify tool was called with correct query
            mock_search.assert_called_once()
            call_args = mock_search.call_args
            assert "artificial intelligence" in call_args[0][1]  # Second argument is query
