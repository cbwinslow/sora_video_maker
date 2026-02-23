#!/bin/bash

# Installation script for OpenAI image and video generation tools
# Includes support for DALL-E 3, GPT-4 Vision, and future Sora API

set -e

echo "================================"
echo "OpenAI Media Tools Installer"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check Python availability
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

print_status "Installing OpenAI Python SDK..."

# Install/upgrade OpenAI SDK
pip install --upgrade openai

print_status "OpenAI SDK installed successfully"

# Create helper script for OpenAI media generation
mkdir -p scripts/openai_tools

cat > scripts/openai_tools/image_generation.py << 'EOF'
"""
OpenAI Image Generation Helper
Supports DALL-E 3 and DALL-E 2
"""

import os
from openai import OpenAI
import requests
from datetime import datetime

class OpenAIImageGenerator:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    
    def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1
    ):
        """Generate image using DALL-E"""
        response = self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n
        )
        
        return response.data
    
    def save_image(self, image_url: str, output_dir: str = "output/images"):
        """Download and save generated image"""
        os.makedirs(output_dir, exist_ok=True)
        
        response = requests.get(image_url)
        if response.status_code == 200:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(output_dir, f"dalle_{timestamp}.png")
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            return filename
        return None

if __name__ == '__main__':
    print("OpenAI Image Generation Helper")
    print("Usage: from openai_tools.image_generation import OpenAIImageGenerator")
EOF

cat > scripts/openai_tools/video_generation.py << 'EOF'
"""
OpenAI Video Generation Helper
Placeholder for future Sora API integration
"""

import os
from openai import OpenAI

class OpenAIVideoGenerator:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    
    def generate_video(self, prompt: str, duration: int = 5):
        """
        Generate video using Sora (when API becomes available)
        
        Note: Sora API is not yet publicly available.
        This is a placeholder for future implementation.
        """
        # TODO: Implement when Sora API is released
        raise NotImplementedError(
            "Sora API is not yet publicly available. "
            "Check https://openai.com/sora for updates."
        )

if __name__ == '__main__':
    print("OpenAI Video Generation Helper")
    print("Note: Sora API not yet available")
EOF

cat > scripts/openai_tools/__init__.py << 'EOF'
"""OpenAI Tools Package"""
from .image_generation import OpenAIImageGenerator
# from .video_generation import OpenAIVideoGenerator  # Uncomment when Sora is available

__all__ = ['OpenAIImageGenerator']
EOF

print_status "Created OpenAI helper scripts"

# Create configuration section for OpenAI
print_status "Configuration instructions:"
echo ""
echo "1. Get your OpenAI API key from: https://platform.openai.com/api-keys"
echo "2. Add to config/config.yaml:"
echo ""
echo "  openai:"
echo "    api_key: \"your-api-key-here\""
echo "    image_model: \"dall-e-3\"  # or dall-e-2"
echo "    image_size: \"1024x1024\""
echo "    image_quality: \"standard\"  # or hd"
echo ""
echo "3. Or set environment variable:"
echo "   export OPENAI_API_KEY='your-api-key-here'"
echo ""

print_status "Testing OpenAI SDK installation..."
python3 << 'PYEOF'
try:
    import openai
    print(f"✓ OpenAI SDK version: {openai.__version__}")
except ImportError as e:
    print(f"✗ Error: {e}")
    exit(1)
PYEOF

echo ""
print_status "================================"
print_status "OpenAI Tools Installation Complete!"
print_status "================================"
echo ""
print_warning "Note: Sora video generation API is not yet publicly available"
print_status "DALL-E 3 image generation is ready to use"
echo ""
print_status "Next steps:"
echo "  1. Set your OPENAI_API_KEY"
echo "  2. Test image generation:"
echo "     python examples/openai_image_demo.py"
echo ""
