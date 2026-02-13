# Quick Start Guide for Comprehensive Testing

This guide will help you quickly get started with the comprehensive test suite.

## Prerequisites

- Python 3.9, 3.10, or 3.11
- Git
- Linux (for systemd services) or macOS/Windows (for basic tests)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/cbwinslow/sora_video_maker.git
cd sora_video_maker
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Check Installation

```bash
# Check service health
./check_services.sh

# Should show:
# - Python, pip, git installed
# - Directory structure exists
# - Python packages installed
```

## Running Tests

### Quick Test

Run fast tests only:

```bash
./run_tests.sh
```

### With Coverage Report

```bash
./run_tests.sh --coverage

# View coverage report
open htmlcov/index.html  # Or your browser
```

### By Category

```bash
# Only initialization tests
./run_tests.sh --unit

# Only integration tests
./run_tests.sh --integration

# All tests including slow ones
./run_tests.sh --all
```

### Specific Test Files

```bash
# Initialization tests only
pytest tests/test_initialization.py -v

# Agent communication tests
pytest tests/test_agent_communication.py -v

# System integration tests
pytest tests/test_system_integration.py -v
```

## Understanding Test Results

### Passing Tests

```
tests/test_initialization.py::TestDirectoryStructure::test_agents_directory_exists PASSED
```
✅ This test passed successfully

### Failed Tests

```
tests/test_initialization.py::TestAgentInitialization::test_trending_topics_agent_init FAILED
```
❌ This test failed - check the error message

### Skipped Tests

```
tests/test_system_integration.py::TestSystemServices::test_ffmpeg_available SKIPPED
```
⏭️ This test was skipped (usually because dependency not installed)

## Test Categories

### 1. Initialization Tests

Verify all components can be initialized:

```bash
pytest tests/test_initialization.py -v
```

**What it tests:**
- Agent initialization
- Crew setup
- Configuration loading
- Directory structure
- Python environment

### 2. Agent Communication Tests

Test agent-to-agent communication:

```bash
pytest tests/test_agent_communication.py -v
```

**What it tests:**
- Data flow between agents
- Crew coordination
- Error recovery
- Concurrent operations
- State management

### 3. System Integration Tests

Verify system resources:

```bash
pytest tests/test_system_integration.py -v
```

**What it tests:**
- File system access
- Web service connectivity
- System commands (FFmpeg, Git)
- Network configuration
- Resource availability

## Common Scenarios

### Scenario 1: First Time Setup

```bash
# 1. Check what's installed
./check_services.sh

# 2. Run basic tests
./run_tests.sh --fast

# 3. If tests pass, run with coverage
./run_tests.sh --coverage
```

### Scenario 2: After Code Changes

```bash
# 1. Run affected tests
pytest tests/unit/test_[changed_module].py -v

# 2. Run full test suite
./run_tests.sh --all

# 3. Check coverage
./run_tests.sh --coverage
```

### Scenario 3: Before Committing

```bash
# 1. Run all fast tests
./run_tests.sh

# 2. Check code style (if configured)
flake8 agents/ scripts/ crews/ main.py

# 3. Check coverage
./run_tests.sh --coverage

# 4. Ensure >70% coverage
```

### Scenario 4: CI/CD Pipeline

```bash
# Simulate CI locally
pip install -r requirements.txt
pytest --cov=agents --cov=scripts --cov=crews --cov=main \
       --cov-report=xml --cov-fail-under=70
```

## Troubleshooting

### Issue: Tests failing with import errors

**Solution:**
```bash
# Ensure you're in project root
cd /path/to/sora_video_maker

# Install in editable mode
pip install -e .
```

### Issue: Missing dependencies

**Solution:**
```bash
# Check what's missing
./check_services.sh

# Install missing packages
pip install [missing-package]
```

### Issue: Permission errors

**Solution:**
```bash
# Make scripts executable
chmod +x run_tests.sh check_services.sh
```

### Issue: Tests running slow

**Solution:**
```bash
# Skip slow tests
pytest tests/ -m "not slow"

# Or use fast mode
./run_tests.sh --fast
```

### Issue: Coverage too low

**Solution:**
```bash
# See which files need tests
pytest --cov=. --cov-report=term-missing

# Focus on files with low coverage
```

## Test Markers

Use markers to run specific test types:

```bash
# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Only agent tests
pytest -m agent

# Skip slow tests
pytest -m "not slow"

# Skip API tests (no internet needed)
pytest -m "not api"

# Combine markers
pytest -m "unit and agent and not slow"
```

## Continuous Integration

Tests run automatically on:
- Every push to main/develop
- Every pull request
- Manual trigger

View CI results:
1. Go to GitHub repository
2. Click "Actions" tab
3. Select workflow run
4. View test results and logs

## Next Steps

After running tests successfully:

1. **Review Coverage**
   ```bash
   open htmlcov/index.html
   ```
   Look for files with <70% coverage

2. **Check Documentation**
   ```bash
   cat docs/COMPREHENSIVE_TESTING.md
   ```
   Learn about writing new tests

3. **Set Up Services** (Linux)
   ```bash
   cd install/systemd
   sudo ./install_services.sh
   ```

4. **Run Full Workflow**
   ```bash
   python main.py --research-only
   ```

## Getting Help

- **Documentation**: Check `docs/` directory
- **Test Examples**: Look at existing tests
- **Issues**: Check `TASKS.md` for known issues
- **Community**: Open an issue on GitHub

## Quick Reference

```bash
# Essential commands
./check_services.sh           # Check system health
./run_tests.sh                # Run fast tests
./run_tests.sh --coverage     # With coverage
./run_tests.sh --all          # All tests
pytest tests/[file].py -v     # Specific file
pytest -m unit                # By marker

# Common pytest options
-v                            # Verbose
-vv                           # Very verbose
-s                            # Show print output
-x                            # Stop on first failure
--lf                          # Run last failed
--tb=short                    # Short traceback
```

## Success Indicators

You know everything is working when:

1. ✅ `./check_services.sh` shows most checks passing
2. ✅ `./run_tests.sh` completes without errors
3. ✅ Coverage report shows >70% overall
4. ✅ All essential services are running
5. ✅ No critical test failures

## Resources

- [Comprehensive Testing Guide](docs/COMPREHENSIVE_TESTING.md)
- [Agent Documentation](docs/AGENTS.md)
- [Task List](TASKS.md)
- [Systemd Services](install/systemd/README.md)

---

**Ready to Go?**

```bash
# Quick validation
./check_services.sh && ./run_tests.sh && echo "✅ All systems go!"
```

If you see "✅ All systems go!" - you're ready to start developing!
