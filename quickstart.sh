#!/bin/bash

# Quick Start Script
# This script helps you get started quickly with the video generation toolkit

set -e

echo "======================================"
echo "Video Generation Toolkit - Quick Start"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run install/install_all.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if config exists
if [ ! -f "config/config.yaml" ]; then
    echo "Creating configuration file..."
    cp config/config.template.yaml config/config.yaml
    echo "✓ Configuration file created at config/config.yaml"
    echo ""
    echo "⚠️  Please edit config/config.yaml and add your API keys before continuing."
    echo ""
    read -p "Press Enter once you've added your API keys..."
fi

# Create necessary directories
mkdir -p output/videos output/trends logs temp

# Test connections
echo ""
echo "Testing connections to services..."
python examples/test_connections.py

echo ""
echo "======================================"
echo "Quick Start Options"
echo "======================================"
echo ""
echo "Choose an option:"
echo "  1. Research trending topics only"
echo "  2. Run basic workflow example"
echo "  3. Run full workflow (research + generate)"
echo "  4. Start ComfyUI server"
echo "  5. Start Ollama server"
echo "  6. Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "Running research phase..."
        python main.py --research-only
        ;;
    2)
        echo ""
        echo "Running basic workflow example..."
        python examples/basic_workflow.py
        ;;
    3)
        echo ""
        echo "Running full workflow..."
        python main.py --generate
        ;;
    4)
        echo ""
        echo "Starting ComfyUI server..."
        if [ -d "ComfyUI" ]; then
            cd ComfyUI
            python main.py
        else
            echo "ComfyUI not found. Run install/install_comfyui.sh first."
        fi
        ;;
    5)
        echo ""
        echo "Starting Ollama server..."
        ollama serve
        ;;
    6)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "Quick start complete!"
echo "======================================"
