#!/bin/bash
# Comprehensive test runner for video generation toolkit
#
# Usage: ./run_tests.sh [options]
#
# Options:
#   --all           Run all tests including slow ones
#   --unit          Run only unit tests
#   --integration   Run only integration tests
#   --fast          Run fast tests only (default)
#   --coverage      Run with coverage report
#   --parallel      Run tests in parallel
#   --verbose       Verbose output
#   --help          Show this help

set -e

# Default options
RUN_MODE="fast"
COVERAGE=false
PARALLEL=false
VERBOSE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            RUN_MODE="all"
            shift
            ;;
        --unit)
            RUN_MODE="unit"
            shift
            ;;
        --integration)
            RUN_MODE="integration"
            shift
            ;;
        --fast)
            RUN_MODE="fast"
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            head -n 12 "$0" | tail -n 11
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Print header
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Video Generation Toolkit Test Suite${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}Python not found!${NC}"
    exit 1
fi

echo -e "${YELLOW}Python version:${NC} $(python --version)"

# Check pytest
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${RED}pytest not installed!${NC}"
    echo "Installing test dependencies..."
    pip install -r requirements.txt
fi

# Build pytest command
PYTEST_CMD=(pytest)

# Add verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD+=(-v)
fi

# Add parallel execution
if [ "$PARALLEL" = true ]; then
    PYTEST_CMD+=(-n auto)
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD+=(--cov=agents --cov=scripts --cov=crews --cov=main)
    PYTEST_CMD+=(--cov-report=html --cov-report=term --cov-report=xml)
fi

# Set test selection based on mode
case $RUN_MODE in
    all)
        echo -e "${YELLOW}Running all tests...${NC}"
        TEST_SELECTION=(tests/)
        ;;
    unit)
        echo -e "${YELLOW}Running unit tests...${NC}"
        TEST_SELECTION=(tests/unit/ tests/test_initialization.py -m unit)
        ;;
    integration)
        echo -e "${YELLOW}Running integration tests...${NC}"
        TEST_SELECTION=(tests/integration/ tests/test_agent_communication.py tests/test_system_integration.py -m integration)
        ;;
    fast)
        echo -e "${YELLOW}Running fast tests...${NC}"
        TEST_SELECTION=(tests/ -m "not slow and not api")
        ;;
esac

# Final command (for display)
echo -e "${YELLOW}Command:${NC} ${PYTEST_CMD[@]} ${TEST_SELECTION[@]} --tb=short"
echo ""

# Run tests
if "${PYTEST_CMD[@]}" "${TEST_SELECTION[@]}" --tb=short; then
    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}All tests passed! ✓${NC}"
    echo -e "${GREEN}======================================${NC}"
    
    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${YELLOW}Coverage report generated:${NC}"
        echo "  - HTML: htmlcov/index.html"
        echo "  - XML: coverage.xml"
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}======================================${NC}"
    echo -e "${RED}Some tests failed! ✗${NC}"
    echo -e "${RED}======================================${NC}"
    exit 1
fi
