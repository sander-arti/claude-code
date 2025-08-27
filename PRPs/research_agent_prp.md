name: "Research Agent with Pydantic AI and Brave API - PRP v1"
description: |
  Comprehensive implementation plan for building a research agent using Pydantic AI 
  that can research topics with the Brave API integration

---

## Goal

Build a simple yet robust research agent using Pydantic AI that can research topics with the Brave API, providing structured responses and comprehensive topic research capabilities.

## Why

- **User Value**: Enables automated research capabilities with AI-powered analysis
- **Integration Benefits**: Leverages Pydantic AI's structured output and tool integration features
- **Problem Solving**: Provides a foundation for building more complex research workflows
- **Learning Platform**: Demonstrates best practices for Pydantic AI agent development

## What

A research agent that:
- Accepts research topics/queries from users
- Uses Brave API to gather web search results
- Processes and analyzes search results using AI
- Returns structured, comprehensive research summaries
- Maintains conversation memory for follow-up questions
- Provides proper error handling and validation

### Success Criteria
- [ ] Agent successfully searches and returns results from Brave API
- [ ] Structured output using Pydantic models for consistent response format  
- [ ] Conversation memory allows for follow-up research questions
- [ ] Comprehensive test coverage with TestModel and FunctionModel
- [ ] Environment-based configuration for API keys
- [ ] Error handling for API failures and invalid queries
- [ ] Documentation and examples for usage

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://ai.pydantic.dev/
  why: Official Pydantic AI documentation for agent patterns and best practices
  
- url: https://ai.pydantic.dev/agents/
  why: Agent creation guide with configuration and provider setup
  
- url: https://ai.pydantic.dev/tools/
  why: Tool integration patterns for external API calls like Brave
  
- url: https://ai.pydantic.dev/testing/
  why: Testing patterns with TestModel and FunctionModel for development
  
- url: https://ai.pydantic.dev/models/
  why: Model provider configuration and environment variable setup

- url: https://brave.com/search/api/
  why: Brave Search API documentation for search endpoints and parameters
  
- docfile: PRPs/ai_docs/pydantic_ai_examples.md
  why: Contains example patterns from the INITIAL.md reference files
```

### Current Codebase tree
```bash
claude-code/
├── CLAUDE.md
├── README.md
├── PRPs/
│   ├── INITIAL.md
│   ├── templates/
│   │   └── prp_base.md
│   └── ai_docs/
└── examples/
    └── INITIAL.md
```

### Desired Codebase tree with files to be added
```bash
claude-code/
├── src/
│   ├── __init__.py
│   ├── research_agent/
│   │   ├── __init__.py
│   │   ├── agent.py              # Main research agent implementation
│   │   ├── models.py             # Pydantic models for requests/responses
│   │   ├── tools.py              # Brave API integration tools
│   │   ├── config.py             # Environment configuration
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_agent.py     # Agent behavior tests
│   │       ├── test_models.py    # Model validation tests
│   │       └── test_tools.py     # Tool integration tests
│   └── examples/
│       ├── basic_research.py     # Simple research example
│       ├── conversation_memory.py # Memory example
│       └── structured_output.py  # Structured response example
├── pyproject.toml                # UV package configuration
├── .env.example                  # Environment variable template
└── README_research_agent.md      # Usage documentation
```

### Known Gotchas of our codebase & Library Quirks
```python
# CRITICAL: Pydantic AI requires specific async/sync patterns
# - Agents can be both sync and async but tools must match agent type
# - Use RunContext for tool access to conversation state

# CRITICAL: Environment configuration patterns
# - Use pydantic-settings for environment variable validation
# - Never hardcode API keys or model strings
# - Follow CLAUDE.md patterns for config management

# CRITICAL: Brave API specifics
# - Rate limiting: 1000 requests per month on free tier
# - Requires X-Subscription-Token header for authentication
# - Returns JSON with specific structure: results[], web{}, etc.

# CRITICAL: Testing with Pydantic AI
# - Use TestModel for development and testing
# - Use FunctionModel for testing tool interactions
# - Never mock Pydantic AI internals - use provided test models
```

## Implementation Blueprint

### Data models and structure

Create core data models ensuring type safety and structured responses:

```python
# Pydantic models for research agent
class ResearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=10, ge=1, le=20)
    include_snippets: bool = Field(default=True)

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    relevance_score: Optional[float] = None

class ResearchResponse(BaseModel):
    query: str
    summary: str
    key_findings: List[str]
    sources: List[SearchResult]
    follow_up_suggestions: List[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

class AgentConfig(BaseSettings):
    brave_api_key: str = Field(..., env="BRAVE_API_KEY")
    model_provider: str = Field(default="openai", env="MODEL_PROVIDER")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    max_search_results: int = Field(default=10, env="MAX_SEARCH_RESULTS")
```

### List of tasks to be completed to fulfill the PRP

```yaml
Task 1:
CREATE pyproject.toml:
  - PATTERN: Follow CLAUDE.md UV package management standards
  - INCLUDE dependencies: pydantic-ai, pydantic-settings, httpx, pytest
  - SET project structure with proper src/ layout

Task 2:
CREATE src/research_agent/config.py:
  - PATTERN: Use pydantic-settings BaseSettings pattern from CLAUDE.md
  - IMPLEMENT environment variable validation for API keys
  - INCLUDE model provider configuration

Task 3:
CREATE src/research_agent/models.py:
  - PATTERN: Follow CLAUDE.md Pydantic v2 model standards
  - IMPLEMENT ResearchQuery, SearchResult, ResearchResponse models
  - ADD field validation and proper typing

Task 4:
CREATE src/research_agent/tools.py:
  - PATTERN: Follow Pydantic AI tool integration patterns
  - IMPLEMENT brave_search tool function with proper error handling
  - ADD rate limiting and API response parsing

Task 5:
CREATE src/research_agent/agent.py:
  - PATTERN: Follow main_agent_reference patterns from examples
  - IMPLEMENT Agent class with conversation memory
  - ADD structured output configuration using ResearchResponse model

Task 6:
CREATE comprehensive test suite:
  - PATTERN: Use TestModel and FunctionModel from Pydantic AI
  - IMPLEMENT test_agent.py with agent behavior tests
  - ADD test_tools.py for Brave API integration testing

Task 7:
CREATE example files:
  - PATTERN: Follow examples structure from INITIAL.md
  - IMPLEMENT basic_research.py, conversation_memory.py examples
  - ADD structured_output.py demonstrating response models

Task 8:
CREATE environment configuration:
  - CREATE .env.example with required API keys
  - ADD configuration documentation
  - ENSURE security best practices from CLAUDE.md
```

### Per task pseudocode

```python
# Task 4 - Brave API Tool Implementation
from pydantic_ai import RunContext
import httpx

async def brave_search(ctx: RunContext[AgentConfig], query: str) -> str:
    """Search Brave API and return formatted results"""
    # PATTERN: Always validate input first
    if not query.strip():
        raise ValueError("Search query cannot be empty")
    
    # GOTCHA: Brave API requires specific headers and rate limiting
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": ctx.deps.brave_api_key
    }
    
    # CRITICAL: Brave API endpoint and parameters
    url = "https://api.search.brave.com/res/v1/web/search"
    params = {
        "q": query,
        "count": ctx.deps.max_search_results,
        "search_lang": "en",
        "country": "us"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # PATTERN: Parse and structure API response
            data = response.json()
            results = data.get("web", {}).get("results", [])
            
            # CRITICAL: Return formatted string for AI processing
            formatted_results = []
            for result in results[:ctx.deps.max_search_results]:
                formatted_results.append(
                    f"Title: {result.get('title', 'No title')}\n"
                    f"URL: {result.get('url', 'No URL')}\n" 
                    f"Description: {result.get('description', 'No description')}\n"
                    f"---"
                )
            
            return "\n".join(formatted_results)
            
        except httpx.HTTPError as e:
            # PATTERN: Structured error handling
            return f"Search failed: {str(e)}"

# Task 5 - Main Agent Implementation  
from pydantic_ai import Agent

research_agent = Agent(
    model='openai:gpt-4',  # Will be overridden by config
    system_prompt="""You are a research assistant that helps users research topics.
    
    When provided with search results, analyze them and provide:
    1. A clear summary of the topic
    2. Key findings from the search results
    3. Follow-up questions for deeper research
    
    Always be factual and cite your sources.""",
    tools=[brave_search],
    result_type=ResearchResponse  # CRITICAL: Structured output
)

async def research_topic(query: str, config: AgentConfig) -> ResearchResponse:
    """Main research function with conversation context"""
    # PATTERN: Use agent.run with dependencies
    result = await research_agent.run(query, deps=config)
    return result.data
```

### Integration Points
```yaml
ENVIRONMENT:
  - file: .env.example
  - pattern: "BRAVE_API_KEY=your_brave_api_key_here"
  - validation: Use pydantic-settings for type checking

CONFIGURATION:  
  - file: src/research_agent/config.py
  - pattern: BaseSettings with Field(..., env="VAR_NAME")
  - caching: Use @lru_cache for settings singleton

TESTING:
  - framework: pytest with async support
  - pattern: TestModel for agent testing, mock httpx for API calls
  - coverage: Aim for 80%+ with focus on critical paths
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
uv run ruff format .                    # Format code
uv run ruff check . --fix               # Fix linting issues  
uv run mypy src/                        # Type checking

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```python
# CREATE comprehensive test suite
@pytest.mark.asyncio
async def test_research_agent_happy_path():
    """Test basic research functionality"""
    config = AgentConfig(
        brave_api_key="test_key",
        model_provider="test"
    )
    
    # Use TestModel for deterministic testing
    agent = Agent(model=TestModel(), tools=[brave_search])
    result = await agent.run("Python programming", deps=config)
    
    assert isinstance(result.data, ResearchResponse)
    assert result.data.query == "Python programming"
    assert len(result.data.sources) > 0

@pytest.mark.asyncio  
async def test_brave_search_tool_integration():
    """Test Brave API tool with mocked responses"""
    with httpx_mock.HTTPXMock() as m:
        # Mock successful Brave API response
        m.add_response(
            url="https://api.search.brave.com/res/v1/web/search",
            json={"web": {"results": [{"title": "Test", "url": "test.com"}]}}
        )
        
        config = AgentConfig(brave_api_key="test")
        result = await brave_search(MockRunContext(config), "test query")
        assert "Title: Test" in result

def test_research_models_validation():
    """Test Pydantic model validation"""
    # Valid query
    query = ResearchQuery(query="Valid research topic")
    assert query.max_results == 10  # default
    
    # Invalid query  
    with pytest.raises(ValidationError):
        ResearchQuery(query="")  # Empty string should fail
```

```bash
# Run and iterate until passing:
uv run pytest src/research_agent/tests/ -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Test with environment variables
export BRAVE_API_KEY="your_actual_api_key"
export OPENAI_API_KEY="your_openai_key"

# Run example script
uv run python src/examples/basic_research.py

# Expected output: Structured research response with sources
# If error: Check logs and API key configuration
```

## Final validation Checklist
- [ ] All tests pass: `uv run pytest src/ -v`
- [ ] No linting errors: `uv run ruff check src/`  
- [ ] No type errors: `uv run mypy src/`
- [ ] Integration test successful with real API keys
- [ ] Examples run without errors
- [ ] Error cases handled gracefully (invalid queries, API failures)
- [ ] Environment configuration documented
- [ ] Security: No hardcoded API keys in code

---

## Anti-Patterns to Avoid
- ❌ Don't hardcode API keys or model names - use environment config
- ❌ Don't skip TestModel usage - it's essential for development  
- ❌ Don't ignore Brave API rate limits - implement proper error handling
- ❌ Don't use sync functions with async agents - maintain consistency
- ❌ Don't mock Pydantic AI internals - use provided testing utilities
- ❌ Don't create overly complex agents - start simple and enhance iteratively
- ❌ Don't ignore conversation context - leverage RunContext properly