#!/bin/bash

# ComfyUI Installation Script
set -e

echo "Installing ComfyUI..."

# Clone ComfyUI if not already present
if [ ! -d "ComfyUI" ]; then
    git clone https://github.com/comfyanonymous/ComfyUI.git
    cd ComfyUI
    
    # Install ComfyUI dependencies
    pip install -r requirements.txt
    
    # Install custom nodes
    cd custom_nodes
    
    # ComfyUI Manager for easy node management
    if [ ! -d "ComfyUI-Manager" ]; then
        git clone https://github.com/ltdrdata/ComfyUI-Manager.git
    fi
    
    # Video Helper Suite for video processing
    if [ ! -d "ComfyUI-VideoHelperSuite" ]; then
        git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
        cd ComfyUI-VideoHelperSuite
        pip install -r requirements.txt
        cd ..
    fi
    
    # AnimateDiff for video generation
    if [ ! -d "ComfyUI-AnimateDiff-Evolved" ]; then
        git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
    fi
    
    cd ../..
    
    echo "ComfyUI installed successfully!"
else
    echo "ComfyUI already installed. Updating..."
    cd ComfyUI
    git pull
    cd ..
fi

# Create symlink to workflows
mkdir -p ComfyUI/user/default/workflows
ln -sf $(pwd)/workflows/* ComfyUI/user/default/workflows/ 2>/dev/null || true

echo "ComfyUI setup complete!"
