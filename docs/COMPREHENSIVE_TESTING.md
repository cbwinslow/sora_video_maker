# Comprehensive Testing Guide

Complete guide for testing the Video Generation Toolkit with comprehensive agent communication tests.

## Quick Start

```bash
# Run all fast tests
./run_tests.sh

# Run with coverage report
./run_tests.sh --coverage

# Run only unit tests
./run_tests.sh --unit

# Run only integration tests
./run_tests.sh --integration

# Run all tests including slow ones
./run_tests.sh --all --verbose
```

## Test Suite Overview

The comprehensive test suite includes three main categories:

### 1. Initialization Tests (`tests/test_initialization.py`)

Tests 100% initialization coverage for all components:

- **Agent Initialization**: All agent modules can be properly initialized
- **Crew Initialization**: Crew coordination systems work correctly
- **Configuration Loading**: Config files load and validate properly
- **Directory Structure**: All required directories exist and are accessible
- **Python Environment**: Correct Python version and dependencies
- **Error Handling**: Graceful handling of initialization errors

```bash
# Run initialization tests
pytest tests/test_initialization.py -v
```

### 2. Agent Communication Tests (`tests/test_agent_communication.py`)

Comprehensive tests for agent-to-agent communication:

- **Data Flow**: Research → Generation → Upload pipeline
- **Crew Coordination**: Multi-agent orchestration
- **Error Recovery**: Fault tolerance and resilience
- **State Management**: Agent state independence
- **Concurrent Operations**: Parallel agent execution
- **Data Compatibility**: Format compatibility between agents

```bash
# Run communication tests
pytest tests/test_agent_communication.py -v
```

### 3. System Integration Tests (`tests/test_system_integration.py`)

Tests for system resource access:

- **File System Access**: Read/write permissions, directory creation
- **Web Service Access**: API connectivity, HTTP handling
- **System Services**: FFmpeg, Git, Python, Pip availability
- **Network Configuration**: Socket creation, localhost resolution
- **Resource Availability**: Disk space, memory, CPU
- **Systemd Services**: Service detection and status

```bash
# Run system integration tests  
pytest tests/test_system_integration.py -v
```

## Test Organization

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── test_initialization.py         # Initialization tests (NEW)
├── test_agent_communication.py    # Communication tests (NEW)
├── test_system_integration.py     # System integration tests (NEW)
├── unit/                          # Unit tests
│   ├── test_trending_topics_agent.py
│   ├── test_video_generation_agent.py
│   ├── test_video_editing_agent.py
│   ├── test_video_utils.py
│   ├── test_seo_optimizer.py
│   └── test_content_moderator.py
└── integration/                   # Integration tests
    └── test_workflow_orchestrator.py
```

## Test Markers

Tests use pytest markers for categorization:

```bash
# Run by category
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m agent             # Agent-specific tests
pytest -m "not slow"        # Skip slow tests
pytest -m "not api"         # Skip tests requiring external APIs
```

Available markers:
- `unit` - Unit tests for individual components
- `integration` - Integration tests for workflows
- `slow` - Tests that take significant time
- `api` - Tests requiring external API access
- `video` - Tests involving video processing
- `agent` - Tests for agent modules
- `crew` - Tests for crew modules
- `script` - Tests for script utilities

## Running Tests

### Basic Usage

```bash
# All tests with default settings
pytest

# Verbose output
pytest -v

# Very verbose with full output
pytest -vv -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

### By Category

```bash
# Only initialization tests
pytest tests/test_initialization.py

# Only agent communication tests
pytest tests/test_agent_communication.py

# Only system integration tests
pytest tests/test_system_integration.py

# All unit tests
pytest tests/unit/ -m unit

# All integration tests
pytest tests/integration/ -m integration
```

### With Coverage

```bash
# Generate HTML coverage report
pytest --cov=agents --cov=scripts --cov=crews --cov=main \
       --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

## Test Coverage Goals

| Module | Target Coverage | Current Status |
|--------|----------------|----------------|
| Agents | 80%+ | 🔄 In Progress |
| Crews | 80%+ | 🔄 In Progress |
| Scripts | 70%+ | 🔄 In Progress |
| Main | 70%+ | 🔄 In Progress |
| Overall | 70%+ | 🔄 In Progress |

Check current coverage:
```bash
pytest --cov=. --cov-report=term-missing
```

## Continuous Integration

Tests run automatically via GitHub Actions:

- **On every push** to main/develop branches
- **On every pull request**
- **Manual trigger** via workflow_dispatch

See `.github/workflows/test_suite.yml` for configuration.

### CI Test Jobs

1. **Test**: Run test suite on Python 3.9, 3.10, 3.11
2. **Lint**: Code quality checks (flake8, black, isort, pylint)
3. **Security**: Security scanning (bandit, safety)
4. **Documentation**: Documentation completeness check
5. **Integration**: Full integration test suite

## Writing Tests

### Unit Test Template

```python
"""
Unit tests for ModuleName
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch


@pytest.mark.unit
@pytest.mark.agent
class TestClassName:
    """Test suite for ClassName"""
    
    def test_initialization(self, mock_config):
        """Test proper initialization"""
        from module import ClassName
        
        obj = ClassName(mock_config)
        
        assert obj is not None
        assert obj.config == mock_config
    
    @pytest.mark.asyncio
    async def test_async_method(self, mock_config):
        """Test async method"""
        from module import ClassName
        
        obj = ClassName(mock_config)
        result = await obj.async_method()
        
        assert result is not None
```

### Integration Test Template

```python
"""
Integration tests for WorkflowName
"""

import pytest
from unittest.mock import patch


@pytest.mark.integration
class TestWorkflowIntegration:
    """Test complete workflow integration"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, mock_config):
        """Test end-to-end workflow"""
        from workflows import WorkflowOrchestrator
        
        orchestrator = WorkflowOrchestrator(mock_config)
        
        # Mock external dependencies
        with patch('external.api.call', return_value='success'):
            result = await orchestrator.execute()
        
        assert result['status'] == 'success'
```

## Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `mock_config` - Complete mock configuration
- `temp_dir` - Temporary directory for tests
- `sample_topic` - Sample topic data
- `sample_trends` - Sample trending topics
- `mock_video_path` - Mock video file path
- `mock_audio_path` - Mock audio file path
- `mock_image_path` - Mock image file path

Usage:
```python
def test_with_fixtures(mock_config, temp_dir, sample_topic):
    """Test using fixtures"""
    # Fixtures are automatically provided
    agent = Agent(mock_config)
    # ... test code
```

## Debugging Tests

### Run with debugging

```bash
# Enable pdb on failures
pytest --pdb

# Enable pdb on errors  
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb

# Increase verbosity
pytest -vv -s

# Show local variables on failure
pytest -l
```

### Common Issues

**Import errors:**
```bash
# Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

**Async test failures:**
```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio
```

**Mock not working:**
```python
# Use correct import path
from unittest.mock import patch

# Patch where object is used, not where it's defined
@patch('agents.trending_topics_agent.requests.get')
def test_function(mock_get):
    pass
```

## Best Practices

1. **Test Independence**: Each test should be independent
2. **Fast Tests**: Unit tests should run in milliseconds
3. **Clear Names**: Test names should describe what they test
4. **Arrange-Act-Assert**: Follow AAA pattern
5. **Mock External**: Mock all external dependencies
6. **Clean Up**: Always clean up resources
7. **Edge Cases**: Test edge cases and error conditions
8. **Documentation**: Document complex test setups

## Test Data Management

### Creating Test Data

```python
# Use fixtures for reusable data
@pytest.fixture
def sample_data():
    return {
        'key': 'value',
        'nested': {'data': 'here'}
    }

# Use factories for variations
def create_topic(title='Test', score=100):
    return {'title': title, 'score': score}
```

### Temporary Files

```python
def test_file_operations(temp_dir):
    """Test with temporary files"""
    from pathlib import Path
    
    test_file = Path(temp_dir) / 'test.txt'
    test_file.write_text('content')
    
    # Test operations
    assert test_file.exists()
    
    # Cleanup is automatic with temp_dir fixture
```

## Performance Testing

### Timing Tests

```python
import time

def test_performance():
    """Test performance requirements"""
    start = time.time()
    
    # Operation to test
    result = expensive_operation()
    
    duration = time.time() - start
    
    # Should complete in less than 1 second
    assert duration < 1.0
```

### Load Testing

```python
@pytest.mark.slow
def test_load():
    """Test system under load"""
    results = []
    
    for i in range(100):
        result = process_item(i)
        results.append(result)
    
    assert len(results) == 100
    assert all(r['status'] == 'success' for r in results)
```

## Security Testing

Tests include security scanning:

```bash
# Run security checks
bandit -r agents/ scripts/ crews/ main.py

# Check for vulnerable dependencies
safety check
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)
- [pytest-xdist](https://pytest-xdist.readthedocs.io/)

## Getting Help

- Check existing tests for examples
- Review test documentation in code
- Run tests with `-v` for more information
- Check GitHub Actions logs for CI failures
- Review TASKS.md for known issues

## Next Steps

See `TASKS.md` for:
- Remaining test coverage goals
- Planned test improvements
- Known testing issues
- Future enhancements
