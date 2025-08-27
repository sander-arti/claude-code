# 🔍 Research Agent with Pydantic AI and Brave API

A powerful research agent built with Pydantic AI that provides comprehensive topic research using the Brave Search API. Features structured responses, conversation memory, and robust error handling.

## ✨ Features

- 🔍 **AI-Powered Research**: Intelligent topic analysis and synthesis
- 🌐 **Brave Search Integration**: Access to fresh, independent search results  
- 📊 **Structured Output**: Consistent, validated responses using Pydantic models
- 💬 **Conversation Memory**: Context-aware follow-up research capabilities
- 🛡️ **Robust Error Handling**: Graceful handling of API failures and rate limits
- ✅ **Comprehensive Testing**: Full test coverage with TestModel and FunctionModel
- 🔧 **Environment Configuration**: Secure, flexible configuration management

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies using UV
uv sync

# Or install in development mode with all dev dependencies
uv sync --dev
```

### 2. Environment Setup

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# BRAVE_API_KEY=your_brave_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Get API Keys

**Brave Search API:**
- Sign up at [https://brave.com/search/api/](https://brave.com/search/api/)
- Note: Credit card required even for free tier (anti-fraud measure)
- Free tier: 2,000 queries/month, 1 query/second

**OpenAI API:**
- Get your key from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Ensure you have access to GPT-4 or your preferred model

### 4. Basic Usage

```python
import asyncio
from research_agent import research_topic
from research_agent.config import get_settings

async def main():
    config = get_settings()
    result = await research_topic("sustainable energy solutions 2024", config)
    
    print(f"Summary: {result.summary}")
    print(f"Key Findings: {result.key_findings}")
    print(f"Sources: {len(result.sources)} references found")

asyncio.run(main())
```

## 📋 Examples

### Basic Research
```bash
# Run basic research example
uv run python src/examples/basic_research.py
```

### Conversation Memory
```bash
# Demonstrate follow-up research with context
uv run python src/examples/conversation_memory.py

# Interactive research session
uv run python src/examples/conversation_memory.py --interactive
```

### Structured Output
```bash
# Show structured output and validation
uv run python src/examples/structured_output.py
```

## 🏗️ Architecture

### Core Components

```
src/research_agent/
├── agent.py          # Main research agent and session management
├── config.py         # Environment configuration with pydantic-settings
├── models.py         # Pydantic models for validation and structure
├── tools.py          # Brave API integration tools
└── tests/           # Comprehensive test suite
    ├── test_agent.py
    ├── test_models.py
    └── test_tools.py
```

### Data Models

**ResearchQuery**: Input validation
```python
query: str = Field(..., min_length=1, max_length=500)
max_results: int = Field(default=10, ge=1, le=20)
include_snippets: bool = Field(default=True)
```

**ResearchResponse**: Structured output
```python
query: str
summary: str
key_findings: List[str]
sources: List[SearchResult]
follow_up_suggestions: List[str]
timestamp: datetime
```

**SearchResult**: Source information
```python
title: str
url: str
snippet: str
relevance_score: Optional[float]
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest src/research_agent/tests/test_agent.py -v
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Fix linting issues automatically  
uv run ruff check --fix .

# Type checking
uv run mypy src/
```

### Environment Configuration

The agent uses pydantic-settings for configuration management:

```python
from research_agent.config import get_settings

config = get_settings()  # Loads from environment variables
print(config.brave_api_key)  # Securely access API keys
```

## 🔧 Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BRAVE_API_KEY` | Brave Search API key | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes* |
| `MODEL_PROVIDER` | Model provider (openai, anthropic) | openai | No |
| `MODEL_NAME` | Specific model to use | gpt-4 | No |
| `MAX_SEARCH_RESULTS` | Max search results (1-20) | 10 | No |
| `SEARCH_LANGUAGE` | Search language code | en | No |
| `SEARCH_COUNTRY` | Search country code | us | No |
| `MAX_RETRIES` | Max retry attempts | 3 | No |
| `TIMEOUT_SECONDS` | Request timeout | 30 | No |
| `DEBUG` | Enable debug logging | false | No |

*Required if using OpenAI models

## 📊 Usage Patterns

### Simple Research
```python
from research_agent import research_topic
from research_agent.config import get_settings

config = get_settings()
result = await research_topic("artificial intelligence trends", config)
```

### Session-based Research (with memory)
```python
from research_agent import ResearchSession
from research_agent.config import get_settings

config = get_settings()
session = ResearchSession(config)

# First query
result1 = await session.research("climate change impacts")

# Follow-up with context
result2 = await session.research("What solutions are being proposed?")

# Get session summary
print(session.get_research_summary())
```

### Custom Agent Configuration
```python
from research_agent.agent import create_research_agent
from research_agent.config import AgentConfig

config = AgentConfig(
    brave_api_key="your-key",
    model_provider="anthropic",
    model_name="claude-3-opus",
    max_search_results=15
)

agent = create_research_agent(config)
result = await agent.run("research query", deps=config)
```

## 🚨 Error Handling

The agent handles various error conditions gracefully:

- **API Rate Limits**: Respects Brave API rate limiting
- **Network Errors**: Retries with exponential backoff
- **Invalid Queries**: Validation errors with helpful messages
- **Empty Results**: Informative responses when no results found
- **Model Errors**: Structured error reporting

## 🔒 Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive configuration
3. **Rotate API keys** regularly
4. **Monitor API usage** to prevent unexpected charges
5. **Use different keys** for development and production

## 📈 Rate Limits & Quotas

### Brave Search API
- **Free Tier**: 2,000 queries/month, 1 query/second
- **Base AI**: 20M queries/month, up to 20 queries/second  
- **Pro AI**: Unlimited queries, up to 50 queries/second

### Best Practices
- Monitor usage with `DEBUG=true`
- Adjust `MAX_SEARCH_RESULTS` based on your tier
- Implement caching for repeated queries
- Use `TIMEOUT_SECONDS` to prevent hanging requests

## 🧪 Testing

The project includes comprehensive tests using Pydantic AI's testing utilities:

- **TestModel**: For fast, deterministic testing
- **FunctionModel**: For custom response simulation
- **Mocked APIs**: HTTP requests mocked with httpx-mock
- **Validation Tests**: Pydantic model validation coverage
- **Integration Tests**: End-to-end workflow testing

## 📚 API Reference

### Core Functions

**research_topic(query: str, config: AgentConfig) -> ResearchResponse**
- Conducts research on a single topic
- Returns structured response with findings and sources

**ResearchSession.research(query: str) -> ResearchResponse**  
- Session-based research with conversation memory
- Maintains context for follow-up questions

**create_research_agent(config: AgentConfig) -> Agent**
- Creates configured agent instance
- Allows custom model and tool configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes following the code style guidelines
4. Add tests for new functionality
5. Run the validation suite: `uv run ruff check . && uv run mypy src/ && uv run pytest`
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋 Support

- **Documentation**: Check the examples in `src/examples/`
- **Issues**: Report bugs and request features on GitHub
- **API Docs**: [Brave Search API](https://brave.com/search/api/), [Pydantic AI](https://ai.pydantic.dev/)

---

Built with ❤️ using [Pydantic AI](https://ai.pydantic.dev/) and [Brave Search API](https://brave.com/search/api/)