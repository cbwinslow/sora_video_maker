# Video Generation Toolkit - Complete Documentation

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Components](#components)
- [API Integrations](#api-integrations)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)

## Overview

The Video Generation Toolkit is a comprehensive automation platform for creating, managing, and distributing AI-generated videos. It integrates multiple video generation platforms, research agents, and upload automation to create a complete end-to-end workflow.

## Features

### Core Features
- **Automated Trending Topic Research**: Discovers viral content opportunities from Reddit, YouTube, Google Trends, and more
- **Multi-Platform Video Generation**: Integrates Sora, ComfyUI, OpenRouter, Ollama, and other platforms
- **Video Processing Utilities**: Resize, concatenate, add audio, extract frames, and more
- **Automated Upload**: Schedule and upload videos to YouTube and other platforms
- **ComfyUI Workflows**: Pre-configured workflows for text-to-image and video generation
- **Flexible Architecture**: Modular design allows easy customization and extension

### Supported Platforms

#### Video Generation
- **Sora** (OpenAI) - When API becomes available
- **ComfyUI** - Local Stable Diffusion and AnimateDiff
- **OpenRouter** - Access to free AI models
- **Ollama** - Local LLM for script generation
- Extensible to other platforms

#### Content Research
- Reddit trending posts
- YouTube trending videos
- Google Trends
- Extensible to Twitter, TikTok, etc.

#### Upload Platforms
- YouTube (with scheduling)
- Extensible to TikTok, Instagram, etc.

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/cbwinslow/sora_video_maker.git
cd sora_video_maker

# Run the master installer
bash install/install_all.sh
```

### Manual Installation

#### 1. System Dependencies

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git curl wget ffmpeg
```

**macOS:**
```bash
brew install python3 git curl wget ffmpeg
```

#### 2. Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 3. ComfyUI

```bash
bash install/install_comfyui.sh
```

This installs:
- ComfyUI core
- ComfyUI Manager
- Video Helper Suite
- AnimateDiff Evolved

#### 4. Ollama

```bash
bash install/install_ollama.sh
```

This installs Ollama and pulls useful models (llama2, mistral, codellama).

#### 5. Additional Tools

```bash
bash install/install_additional_tools.sh
```

## Configuration

### Initial Setup

1. Copy the template configuration:
```bash
cp config/config.template.yaml config/config.yaml
```

2. Edit `config/config.yaml` with your API keys and preferences.

### Configuration Options

```yaml
# API Keys
api_keys:
  openai: "YOUR_OPENAI_API_KEY"
  openrouter: "YOUR_OPENROUTER_API_KEY"
  anthropic: "YOUR_ANTHROPIC_API_KEY"
  huggingface: "YOUR_HUGGINGFACE_TOKEN"

# Video Generation Settings
video_generation:
  default_resolution: "1920x1080"
  default_fps: 30
  default_duration: 10
  output_format: "mp4"
  output_directory: "output/videos"

# Research Settings
research:
  sources:
    - "reddit"
    - "youtube"
    - "google_trends"
  update_interval: 3600
  topics_to_track: 10

# Upload Settings
upload:
  enabled: false
  schedule: "daily"
  platforms:
    - "youtube"
  max_videos_per_day: 5

# Workflow Settings
workflow:
  auto_generate: false
  auto_upload: false
  temp_directory: "temp"
  keep_temp_files: false
```

## Usage

### Basic Usage

#### 1. Test Your Setup

```bash
python examples/test_connections.py
```

This tests all API connections and verifies your installation.

#### 2. Run Research Only

```bash
python main.py --research-only
```

Discovers trending topics without generating videos.

#### 3. Run Full Workflow

```bash
# With generation enabled
python main.py --generate

# Or enable auto_generate in config.yaml and run:
python main.py
```

#### 4. Run Example Workflow

```bash
python examples/basic_workflow.py
```

### Advanced Usage

#### Custom Configuration

```bash
python main.py --config /path/to/custom/config.yaml
```

#### Start ComfyUI Server

```bash
cd ComfyUI
python main.py
```

Then access at http://127.0.0.1:8188

#### Start Ollama Server

```bash
ollama serve
```

## Components

### Agents

#### 1. Trending Topics Agent (`agents/trending_topics_agent.py`)

Researches trending topics across multiple platforms.

```python
from agents.trending_topics_agent import TrendingTopicsAgent

agent = TrendingTopicsAgent(config)
trends = await agent.research()
```

**Features:**
- Multi-source aggregation
- Scoring algorithm for video potential
- Async data fetching
- JSON export

#### 2. Video Generation Agent (`agents/video_generation_agent.py`)

Orchestrates video generation from topics.

```python
from agents.video_generation_agent import VideoGenerationOrchestrator

orchestrator = VideoGenerationOrchestrator(config)
result = await orchestrator.generate_video(topic)
```

**Features:**
- Script generation
- Visual prompt creation
- Multi-platform generation
- Video assembly
- Metadata tracking

#### 3. Video Upload Agent (`agents/video_upload_agent.py`)

Handles video uploads to various platforms.

```python
from agents.video_upload_agent import VideoUploadAgent

agent = VideoUploadAgent(config)
results = await agent.upload_video(video_path, metadata)
```

**Features:**
- YouTube upload (OAuth2)
- Metadata generation
- Upload scheduling
- Rate limiting
- Upload logging

### Scripts

#### API Integrations (`scripts/api_integrations.py`)

Client libraries for all supported APIs.

```python
from scripts.api_integrations import OllamaAPI, ComfyUIAPI, OpenRouterAPI

# Ollama
ollama = OllamaAPI()
text = await ollama.generate_text("Write a video script", "llama2")

# ComfyUI
comfyui = ComfyUIAPI()
prompt_id = await comfyui.queue_prompt(workflow)

# OpenRouter
openrouter = OpenRouterAPI(api_key)
content = await openrouter.generate_text("Create a story")
```

#### Video Utilities (`scripts/video_utils.py`)

Video processing functions using FFmpeg.

```python
from scripts.video_utils import *

# Resize video
resize_video(input_path, output_path, 1920, 1080)

# Concatenate videos
concatenate_videos([video1, video2], output_path)

# Add audio
add_audio_to_video(video_path, audio_path, output_path)

# Extract frames
extract_frames(video_path, output_dir, fps=1)

# Create video from images
create_video_from_images(image_dir, output_path, fps=30)

# Add text overlay
add_text_overlay(video_path, output_path, "Hello World", "top")
```

## API Integrations

### OpenAI / Sora

When Sora API becomes available:

```python
from scripts.api_integrations import SoraAPI

sora = SoraAPI(api_key)
video_path = await sora.generate_video(
    prompt="A beautiful landscape",
    duration=10
)
```

### OpenRouter

Access free AI models:

```python
from scripts.api_integrations import OpenRouterAPI

client = OpenRouterAPI(api_key)
response = await client.generate_text(
    prompt="Generate a video script about AI",
    model="meta-llama/llama-2-70b-chat"
)
```

### Ollama

Local LLM inference:

```bash
# Start Ollama
ollama serve

# Pull models
ollama pull llama2
ollama pull mistral
```

```python
from scripts.api_integrations import OllamaAPI

ollama = OllamaAPI()
response = await ollama.generate_text("Hello", "llama2")
```

### ComfyUI

```bash
# Start ComfyUI
cd ComfyUI
python main.py
```

Access at http://127.0.0.1:8188 or use the API:

```python
from scripts.api_integrations import ComfyUIAPI

comfyui = ComfyUIAPI(host="127.0.0.1", port=8188)
prompt_id = await comfyui.queue_prompt(workflow_dict)
```

## Workflows

### ComfyUI Workflows

Pre-configured workflows in `workflows/` directory:

1. **text_to_image.json** - Basic image generation
2. **text_to_video.json** - Video generation with AnimateDiff (to be added)
3. **image_to_video.json** - Image animation (to be added)

### Creating Custom Workflows

1. Design workflow in ComfyUI interface
2. Export as JSON
3. Save to `workflows/` directory
4. Load programmatically or via ComfyUI interface

## Troubleshooting

### Common Issues

#### ComfyUI Not Starting

```bash
# Check if port is in use
lsof -i :8188

# Try different port
cd ComfyUI
python main.py --port 8189
```

#### Ollama Connection Failed

```bash
# Start Ollama service
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

#### FFmpeg Not Found

```bash
# Linux
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

#### Python Dependencies

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

#### Permission Denied on Install Scripts

```bash
chmod +x install/*.sh
```

### Getting Help

1. Check logs in `logs/` directory
2. Run connection tests: `python examples/test_connections.py`
3. Enable debug logging in config:
   ```yaml
   logging:
     level: "DEBUG"
   ```

## Best Practices

### API Keys

- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate keys regularly

### Video Generation

- Start with low-resolution tests
- Monitor API usage and costs
- Keep temp files during development
- Use version control for workflows

### Content Research

- Respect API rate limits
- Cache trending data
- Update research intervals appropriately
- Filter content appropriately

### Uploads

- Start with private uploads
- Review before publishing
- Follow platform guidelines
- Monitor upload quotas

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please submit pull requests or open issues.

## Support

For support and questions, please open an issue on GitHub.
