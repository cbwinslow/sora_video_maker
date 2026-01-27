#!/bin/bash

# Video Generation Toolkit - Master Installation Script
# This script installs all necessary components for the video generation toolkit

set -e

echo "================================"
echo "Video Generation Toolkit Installer"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if [ -f /etc/debian_version ]; then
            DISTRO="debian"
        elif [ -f /etc/redhat-release ]; then
            DISTRO="redhat"
        else
            DISTRO="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="windows"
    fi
    print_status "Detected OS: $OS"
}

# Check if running with appropriate permissions
check_permissions() {
    if [ "$EUID" -eq 0 ]; then 
        print_warning "Running as root. This is not recommended."
    fi
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if [ "$OS" = "linux" ]; then
        if [ "$DISTRO" = "debian" ]; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv git curl wget ffmpeg
        elif [ "$DISTRO" = "redhat" ]; then
            sudo yum install -y python3 python3-pip git curl wget ffmpeg
        fi
    elif [ "$OS" = "macos" ]; then
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null; then
            print_status "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python3 git curl wget ffmpeg
    fi
    
    print_status "System dependencies installed."
}

# Create Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created."
    else
        print_warning "Virtual environment already exists."
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    print_status "Python environment ready."
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    source venv/bin/activate
    pip install -r requirements.txt
    
    print_status "Python dependencies installed."
}

# Install ComfyUI
install_comfyui() {
    print_status "Installing ComfyUI..."
    
    bash ./install/install_comfyui.sh
    
    print_status "ComfyUI installed."
}

# Install Ollama
install_ollama() {
    print_status "Installing Ollama..."
    
    bash ./install/install_ollama.sh
    
    print_status "Ollama installed."
}

# Install additional tools
install_additional_tools() {
    print_status "Installing additional tools..."
    
    bash ./install/install_additional_tools.sh
    
    print_status "Additional tools installed."
}

# Setup configuration
setup_config() {
    print_status "Setting up configuration..."
    
    if [ ! -f "config/config.yaml" ]; then
        cp config/config.template.yaml config/config.yaml
        print_status "Configuration file created. Please edit config/config.yaml with your API keys."
    else
        print_warning "Configuration file already exists."
    fi
}

# Main installation flow
main() {
    echo ""
    print_status "Starting installation..."
    echo ""
    
    detect_os
    check_permissions
    
    # Create necessary directories
    mkdir -p logs output temp
    
    # Run installations
    install_system_deps
    setup_python_env
    install_python_deps
    install_comfyui
    install_ollama
    install_additional_tools
    setup_config
    
    echo ""
    print_status "================================"
    print_status "Installation Complete!"
    print_status "================================"
    echo ""
    print_status "Next steps:"
    echo "  1. Edit config/config.yaml with your API keys"
    echo "  2. Activate the virtual environment: source venv/bin/activate"
    echo "  3. Run the example workflow: python examples/basic_workflow.py"
    echo ""
    print_status "For more information, see docs/README.md"
}

# Run main installation
main
