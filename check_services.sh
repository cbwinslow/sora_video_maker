#!/bin/bash
# Service Health Check Script
# Checks the status of all required services for video generation toolkit

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Icons
CHECK="✓"
CROSS="✗"
INFO="ℹ"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Video Generation Toolkit             ║${NC}"
echo -e "${BLUE}║  Service Health Check                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check systemd service
check_systemd_service() {
    local service=$1
    local display_name=$2
    
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        echo -e "${GREEN}${CHECK}${NC} $display_name is ${GREEN}running${NC}"
        return 0
    else
        echo -e "${RED}${CROSS}${NC} $display_name is ${RED}not running${NC}"
        return 1
    fi
}

# Function to check process
check_process() {
    local process=$1
    local display_name=$2
    
    if pgrep -x "$process" > /dev/null; then
        echo -e "${GREEN}${CHECK}${NC} $display_name process is ${GREEN}running${NC}"
        return 0
    else
        echo -e "${YELLOW}${INFO}${NC} $display_name process ${YELLOW}not found${NC}"
        return 1
    fi
}

# Function to check URL
check_url() {
    local url=$1
    local display_name=$2
    
    if command_exists curl; then
        if curl -s --connect-timeout 2 "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}${CHECK}${NC} $display_name at $url is ${GREEN}accessible${NC}"
            return 0
        else
            echo -e "${RED}${CROSS}${NC} $display_name at $url is ${RED}not accessible${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}${INFO}${NC} curl not installed, skipping URL check"
        return 1
    fi
}

# Function to check command
check_command() {
    local cmd=$1
    local display_name=$2
    
    if command_exists "$cmd"; then
        local version=$($cmd --version 2>&1 | head -n 1 || echo "unknown")
        echo -e "${GREEN}${CHECK}${NC} $display_name: ${GREEN}installed${NC} ($version)"
        return 0
    else
        echo -e "${RED}${CROSS}${NC} $display_name: ${RED}not installed${NC}"
        return 1
    fi
}

# Function to check Python package
check_python_package() {
    local package=$1
    local display_name=$2
    
    if python -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}${CHECK}${NC} Python package $display_name: ${GREEN}installed${NC}"
        return 0
    else
        echo -e "${RED}${CROSS}${NC} Python package $display_name: ${RED}not installed${NC}"
        return 1
    fi
}

echo -e "${YELLOW}═══ System Services ═══${NC}"

# Check systemd services if on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command_exists systemctl; then
        check_systemd_service "comfyui@$USER" "ComfyUI Service"
        check_systemd_service "ollama@$USER" "Ollama Service"
    else
        echo -e "${YELLOW}${INFO}${NC} systemd not available"
    fi
else
    echo -e "${YELLOW}${INFO}${NC} systemd checks skipped (not on Linux)"
fi

echo ""
echo -e "${YELLOW}═══ Running Processes ═══${NC}"

check_process "python" "Python"
check_process "ollama" "Ollama"

echo ""
echo -e "${YELLOW}═══ Service Endpoints ═══${NC}"

check_url "http://127.0.0.1:8188" "ComfyUI"
check_url "http://127.0.0.1:11434" "Ollama"

echo ""
echo -e "${YELLOW}═══ System Commands ═══${NC}"

check_command "python" "Python"
check_command "pip" "Pip"
check_command "git" "Git"
check_command "ffmpeg" "FFmpeg"
check_command "ffprobe" "FFprobe"
check_command "ollama" "Ollama CLI"

echo ""
echo -e "${YELLOW}═══ Python Packages ═══${NC}"

check_python_package "pytest" "pytest"
check_python_package "aiohttp" "aiohttp"
check_python_package "yaml" "PyYAML"
check_python_package "PIL" "Pillow"
check_python_package "cv2" "OpenCV"

echo ""
echo -e "${YELLOW}═══ File System ═══${NC}"

# Check important directories
directories=(
    "agents"
    "scripts"
    "crews"
    "tests"
    "config"
    "workflows"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}${CHECK}${NC} Directory $dir: ${GREEN}exists${NC}"
    else
        echo -e "${RED}${CROSS}${NC} Directory $dir: ${RED}missing${NC}"
    fi
done

echo ""
echo -e "${YELLOW}═══ Configuration ═══${NC}"

if [ -f "config/config.yaml" ]; then
    echo -e "${GREEN}${CHECK}${NC} Configuration file: ${GREEN}exists${NC}"
elif [ -f "config/config.template.yaml" ]; then
    echo -e "${YELLOW}${INFO}${NC} Configuration file: ${YELLOW}template only${NC}"
    echo -e "   Run: ${BLUE}cp config/config.template.yaml config/config.yaml${NC}"
else
    echo -e "${RED}${CROSS}${NC} Configuration file: ${RED}missing${NC}"
fi

echo ""
echo -e "${YELLOW}═══ Summary ═══${NC}"

# Count checks (simplified)
total=0
passed=0

if systemctl is-active --quiet comfyui@$USER 2>/dev/null; then ((passed++)); fi
((total++))

if systemctl is-active --quiet ollama@$USER 2>/dev/null; then ((passed++)); fi
((total++))

for cmd in python pip git ffmpeg; do
    ((total++))
    if command_exists $cmd; then ((passed++)); fi
done

echo -e "Health Check: ${passed}/${total} checks passed"

if [ $passed -eq $total ]; then
    echo -e "${GREEN}${CHECK} All systems operational${NC}"
    exit 0
elif [ $passed -gt $((total / 2)) ]; then
    echo -e "${YELLOW}${INFO} Some services need attention${NC}"
    exit 1
else
    echo -e "${RED}${CROSS} Multiple services are down${NC}"
    exit 2
fi
