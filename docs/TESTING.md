# Testing Guide

This guide covers how to run and write tests for the Sora Video Maker project.

## Table of Contents

- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -r requirements.txt
```

### Running All Tests

```bash
pytest
```

### Running Specific Test Types

Run only unit tests:
```bash
pytest -m unit
```

Run only integration tests:
```bash
pytest -m integration
```

Run tests for a specific component:
```bash
pytest tests/unit/test_trending_topics_agent.py
```

### Running with Coverage

```bash
pytest --cov=agents --cov=scripts --cov=crews --cov=main --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests for individual components
│   ├── __init__.py
│   ├── test_trending_topics_agent.py
│   ├── test_video_generation_agent.py
│   ├── test_video_editing_agent.py
│   ├── test_video_utils.py
│   ├── test_seo_optimizer.py
│   └── test_content_moderator.py
└── integration/             # Integration tests for workflows
    ├── __init__.py
    └── test_workflow_orchestrator.py
```

## Writing Tests

### Unit Test Example

```python
import pytest
from agents.trending_topics_agent import TrendingTopicsAgent


@pytest.mark.unit
@pytest.mark.agent
class TestTrendingTopicsAgent:
    """Test suite for TrendingTopicsAgent"""
    
    def test_init(self, mock_config):
        """Test agent initialization"""
        agent = TrendingTopicsAgent(mock_config)
        
        assert agent.config == mock_config
        assert agent.sources == mock_config['research']['sources']
    
    @pytest.mark.asyncio
    async def test_fetch_reddit_trends(self, mock_config, mock_aiohttp_session):
        """Test Reddit API call"""
        agent = TrendingTopicsAgent(mock_config)
        
        trends = await agent.fetch_reddit_trends()
        
        assert isinstance(trends, list)
        assert len(trends) > 0
```

### Using Fixtures

Fixtures are defined in `tests/conftest.py` and can be used in any test:

```python
def test_with_fixtures(mock_config, temp_dir, sample_topic):
    """Test using multiple fixtures"""
    # mock_config provides a complete mock configuration
    # temp_dir provides a temporary directory
    # sample_topic provides sample data
    
    agent = SomeAgent(mock_config)
    # ... test code
```

### Mocking External Dependencies

```python
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_with_mocks(mock_config):
    """Test with mocked external calls"""
    agent = TrendingTopicsAgent(mock_config)
    
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'data': 'test'})
        
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        result = await agent.fetch_reddit_trends()
        assert result is not None
```

## Test Markers

Tests can be marked with custom markers defined in `pytest.ini`:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.api` - Tests requiring external API access
- `@pytest.mark.video` - Tests involving video processing
- `@pytest.mark.agent` - Tests for agent modules
- `@pytest.mark.crew` - Tests for crew modules
- `@pytest.mark.script` - Tests for script utilities

### Running Tests by Marker

```bash
pytest -m "unit and agent"       # Unit tests for agents only
pytest -m "not slow"             # Skip slow tests
pytest -m "integration or api"   # Integration or API tests
```

## Test Coverage

### Coverage Requirements

The project aims for:
- Overall coverage: 70%+
- Critical modules (agents, crews): 80%+
- Utility modules (scripts): 70%+

### Checking Coverage

Generate HTML coverage report:
```bash
pytest --cov=. --cov-report=html
```

Generate terminal coverage report:
```bash
pytest --cov=. --cov-report=term-missing
```

### Coverage Configuration

Coverage settings are in `pytest.ini`:

```ini
[pytest]
addopts = 
    --cov=agents
    --cov=scripts
    --cov=crews
    --cov=main
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
```

## Continuous Integration

Tests are automatically run on:
- Every pull request
- Every push to main branch
- Scheduled daily runs

### CI Configuration

See `.github/workflows/tests.yml` for CI configuration.

### Local CI Simulation

Run tests exactly as CI does:

```bash
# Install dependencies
pip install -r requirements.txt

# Run linting (if configured)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Run tests with coverage
pytest --cov=. --cov-report=xml --cov-fail-under=70

# Check test results
echo $?  # Should be 0 for success
```

## Troubleshooting

### Common Issues

**Issue: Tests fail with import errors**
```bash
# Solution: Install package in development mode
pip install -e .
```

**Issue: Async tests fail**
```bash
# Solution: Ensure pytest-asyncio is installed
pip install pytest-asyncio
```

**Issue: Mock not working**
```bash
# Solution: Check import paths in mocks match actual imports
# Use full module paths in patch decorators
```

### Debugging Tests

Run tests with verbose output:
```bash
pytest -vv
```

Run tests with output capture disabled:
```bash
pytest -s
```

Run specific test with debugging:
```bash
pytest tests/unit/test_trending_topics_agent.py::TestTrendingTopicsAgent::test_init -vv -s
```

### Test Data

Test data and fixtures should be:
- Minimal - only what's needed for the test
- Isolated - don't depend on external state
- Reproducible - same input = same output
- Clean - properly cleaned up after test

## Best Practices

1. **One assertion per test** (when possible)
2. **Use descriptive test names** that explain what is being tested
3. **Arrange-Act-Assert** pattern
4. **Mock external dependencies** (API calls, file system, etc.)
5. **Use fixtures** for common setup code
6. **Test edge cases** and error conditions
7. **Keep tests fast** - unit tests should run in milliseconds
8. **Clean up resources** - use fixtures with teardown or context managers

## Example Test File Template

```python
"""
Unit tests for ModuleName
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from module.path import ClassToTest


@pytest.mark.unit
@pytest.mark.category  # agent, script, crew, etc.
class TestClassName:
    """Test suite for ClassName"""
    
    def test_init(self, mock_config):
        """Test initialization"""
        obj = ClassToTest(mock_config)
        assert obj.config == mock_config
    
    @pytest.mark.asyncio
    async def test_async_method(self, mock_config):
        """Test async method"""
        obj = ClassToTest(mock_config)
        result = await obj.async_method()
        assert result is not None
    
    def test_method_with_mock(self, mock_config):
        """Test with mocked dependency"""
        obj = ClassToTest(mock_config)
        
        with patch('module.path.dependency') as mock_dep:
            mock_dep.return_value = 'mocked'
            result = obj.method_that_uses_dependency()
            assert result == 'expected'
    
    def test_error_handling(self, mock_config):
        """Test error handling"""
        obj = ClassToTest(mock_config)
        
        with pytest.raises(ValueError):
            obj.method_that_should_raise()


@pytest.mark.unit
@pytest.mark.category
class TestClassNameEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_input(self, mock_config):
        """Test with empty input"""
        obj = ClassToTest(mock_config)
        result = obj.process("")
        assert result is not None
    
    def test_invalid_input(self, mock_config):
        """Test with invalid input"""
        obj = ClassToTest(mock_config)
        with pytest.raises(ValueError):
            obj.process(None)
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
