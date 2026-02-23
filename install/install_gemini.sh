#!/bin/bash

# Installation script for Google Gemini AI
# Supports Gemini Pro, Gemini Pro Vision, and multimodal capabilities

set -e

echo "================================"
echo "Google Gemini AI Installer"
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

print_status "Installing Google Generative AI SDK..."

# Install Google AI SDK
pip install --upgrade google-generativeai
pip install --upgrade google-cloud-aiplatform

print_status "Google AI SDK installed successfully"

# Create helper scripts for Gemini
mkdir -p scripts/gemini_tools

cat > scripts/gemini_tools/gemini_client.py << 'EOF'
"""
Google Gemini AI Client
Supports text, vision, and multimodal generation
"""

import os
import google.generativeai as genai
from typing import Optional, List, Dict
from datetime import datetime

class GeminiClient:
    def __init__(self, api_key: str = None):
        api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key not found")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini Pro"""
        response = self.model.generate_content(prompt, **kwargs)
        return response.text
    
    def analyze_image(self, image_path: str, prompt: str = "Describe this image") -> str:
        """Analyze image using Gemini Pro Vision"""
        import PIL.Image
        
        img = PIL.Image.open(image_path)
        response = self.vision_model.generate_content([prompt, img])
        return response.text
    
    def enhance_prompt(self, basic_prompt: str) -> str:
        """Use Gemini to enhance a basic prompt"""
        enhancement_prompt = f"""
        Enhance the following creative prompt for AI image/video generation.
        Make it more detailed, specific, and production-ready.
        Include technical details like lighting, camera angles, mood, and style.
        
        Basic prompt: {basic_prompt}
        
        Enhanced prompt:
        """
        
        return self.generate_text(enhancement_prompt)
    
    def break_down_scene(self, scene_description: str, num_frames: int = 4) -> List[str]:
        """Break down a scene into frame-by-frame descriptions"""
        prompt = f"""
        Break down the following scene into {num_frames} detailed frame descriptions
        for video generation. Each frame should be a complete, standalone description.
        
        Scene: {scene_description}
        
        Provide {num_frames} frame descriptions:
        """
        
        response = self.generate_text(prompt)
        
        # Parse response into frames
        frames = [line.strip() for line in response.split('\n') if line.strip()]
        return frames[:num_frames]
    
    def generate_video_script(self, topic: str, duration: int = 60) -> Dict:
        """Generate a video script with scenes and narration"""
        prompt = f"""
        Create a {duration}-second video script about: {topic}
        
        Include:
        1. Scene descriptions for video generation
        2. Narration/voiceover text
        3. Timing for each scene
        4. Visual elements and transitions
        
        Format as structured data.
        """
        
        response = self.generate_text(prompt)
        
        return {
            'topic': topic,
            'duration': duration,
            'script': response,
            'timestamp': datetime.now().isoformat()
        }
    
    def research_topic(self, topic: str) -> str:
        """Research a topic for content creation"""
        prompt = f"""
        Research and provide key information about: {topic}
        
        Include:
        - Main concepts and ideas
        - Visual elements to feature
        - Interesting facts or angles
        - Suggested style and mood
        
        Keep it concise and focused on video/image creation.
        """
        
        return self.generate_text(prompt)

if __name__ == '__main__':
    print("Google Gemini AI Client")
    print("Usage: from gemini_tools.gemini_client import GeminiClient")
EOF

cat > scripts/gemini_tools/__init__.py << 'EOF'
"""Gemini Tools Package"""
from .gemini_client import GeminiClient

__all__ = ['GeminiClient']
EOF

print_status "Created Gemini helper scripts"

# Create configuration section
print_status "Configuration instructions:"
echo ""
echo "1. Get your Google AI API key from: https://makersuite.google.com/app/apikey"
echo "2. Add to config/config.yaml:"
echo ""
echo "  gemini:"
echo "    api_key: \"your-api-key-here\""
echo "    model: \"gemini-pro\""
echo "    vision_model: \"gemini-pro-vision\""
echo ""
echo "3. Or set environment variable:"
echo "   export GOOGLE_API_KEY='your-api-key-here'"
echo ""

print_status "Testing Gemini SDK installation..."
python3 << 'PYEOF'
try:
    import google.generativeai as genai
    print(f"✓ Google Generative AI SDK installed")
except ImportError as e:
    print(f"✗ Error: {e}")
    exit(1)
PYEOF

echo ""
print_status "================================"
print_status "Gemini Installation Complete!"
print_status "================================"
echo ""
print_status "Available capabilities:"
echo "  - Text generation (Gemini Pro)"
echo "  - Vision analysis (Gemini Pro Vision)"
echo "  - Prompt enhancement"
echo "  - Scene breakdown"
echo "  - Script generation"
echo ""
print_status "Next steps:"
echo "  1. Set your GOOGLE_API_KEY"
echo "  2. Test Gemini:"
echo "     python examples/gemini_demo.py"
echo ""
