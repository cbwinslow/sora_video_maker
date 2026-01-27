#!/bin/bash

# Ollama Installation Script
set -e

echo "Installing Ollama..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux installation
    curl -fsSL https://ollama.com/install.sh | sh
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS installation
    if command -v brew &> /dev/null; then
        brew install ollama
    else
        echo "Please install Homebrew first or download Ollama from https://ollama.com/download"
        exit 1
    fi
else
    echo "Please download and install Ollama manually from https://ollama.com/download"
    exit 1
fi

echo "Ollama installed successfully!"

# Start Ollama service
echo "Starting Ollama service..."
ollama serve &
sleep 5

# Pull useful models for video generation
echo "Pulling useful models..."
ollama pull llama2
ollama pull codellama
ollama pull mistral

echo "Ollama setup complete!"
