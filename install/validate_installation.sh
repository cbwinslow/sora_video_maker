#!/bin/bash

# Installation Validation Script
# Validates that all components are properly installed

echo "================================"
echo "Installation Validation"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

passed=0
failed=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((passed++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((failed++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "Checking Python Installation..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    check_pass "Python 3 installed (version $python_version)"
else
    check_fail "Python 3 not found"
fi
echo ""

echo "Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    ffmpeg_version=$(ffmpeg -version 2>&1 | head -1 | cut -d' ' -f3)
    check_pass "FFmpeg installed (version $ffmpeg_version)"
else
    check_fail "FFmpeg not found - required for video processing"
fi
echo ""

echo "Checking Python Packages..."
packages=("requests" "aiohttp" "yaml" "PIL" "moviepy" "openai" "anthropic")

for package in "${packages[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        check_pass "Package $package installed"
    else
        check_fail "Package $package not found"
    fi
done
echo ""

echo "Checking Agents..."
agent_files=(
    "agents/youtube_shorts_agent.py"
    "agents/video_analysis_agent.py"
    "agents/inpainting_agent.py"
    "agents/prompt_enhancement_agent.py"
    "agents/video_generation_agent.py"
    "agents/video_editing_agent.py"
)

for agent in "${agent_files[@]}"; do
    if [ -f "$agent" ]; then
        check_pass "Agent: $agent"
    else
        check_fail "Agent missing: $agent"
    fi
done
echo ""

echo "Checking Examples..."
example_files=(
    "examples/create_shorts.py"
    "examples/prompt_enhancement_demo.py"
    "examples/basic_workflow.py"
)

for example in "${example_files[@]}"; do
    if [ -f "$example" ]; then
        check_pass "Example: $example"
    else
        check_fail "Example missing: $example"
    fi
done
echo ""

echo "Checking Documentation..."
doc_files=(
    "docs/README.md"
    "docs/YOUTUBE_SHORTS.md"
    "docs/AI_AGENTS.md"
    "workflows/README.md"
)

for doc in "${doc_files[@]}"; do
    if [ -f "$doc" ]; then
        check_pass "Documentation: $doc"
    else
        check_fail "Documentation missing: $doc"
    fi
done
echo ""

echo "Testing Agents..."
echo "Testing Prompt Enhancement Agent..."
if python3 -c "from agents.prompt_enhancement_agent import PromptEnhancementAgent; agent = PromptEnhancementAgent({}); print('OK')" 2>/dev/null | grep -q "OK"; then
    check_pass "Prompt Enhancement Agent loads successfully"
else
    check_fail "Prompt Enhancement Agent failed to load"
fi

echo "Testing YouTube Shorts Agent..."
if python3 -c "from agents.youtube_shorts_agent import YouTubeShortsAgent; agent = YouTubeShortsAgent({}); print('OK')" 2>/dev/null | grep -q "OK"; then
    check_pass "YouTube Shorts Agent loads successfully"
else
    check_fail "YouTube Shorts Agent failed to load"
fi

echo "Testing Video Analysis Agent..."
if python3 -c "from agents.video_analysis_agent import VideoAnalysisAgent; agent = VideoAnalysisAgent({}); print('OK')" 2>/dev/null | grep -q "OK"; then
    check_pass "Video Analysis Agent loads successfully"
else
    check_fail "Video Analysis Agent failed to load"
fi

echo "Testing Inpainting Agent..."
if python3 -c "from agents.inpainting_agent import InpaintingAgent; agent = InpaintingAgent({}); print('OK')" 2>/dev/null | grep -q "OK"; then
    check_pass "Inpainting Agent loads successfully"
else
    check_fail "Inpainting Agent failed to load"
fi
echo ""

echo "Checking Directories..."
directories=("output" "temp" "prompts" "output/shorts" "output/images")

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "Directory exists: $dir"
    else
        check_warn "Directory not found (will be created): $dir"
        mkdir -p "$dir"
    fi
done
echo ""

echo "================================"
echo "Validation Summary"
echo "================================"
echo -e "${GREEN}Passed: $passed${NC}"
if [ $failed -gt 0 ]; then
    echo -e "${RED}Failed: $failed${NC}"
fi
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Configure API keys in config/config.yaml"
    echo "  2. Try creating Shorts: python examples/create_shorts.py"
    echo "  3. Try prompt enhancement: python examples/prompt_enhancement_demo.py"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the errors above.${NC}"
    echo ""
    echo "To fix missing packages:"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi
