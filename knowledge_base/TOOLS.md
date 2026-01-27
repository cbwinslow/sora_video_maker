# Available Tools & Utilities

## Overview

This document describes all tools and utilities available in the Video Generation Toolkit.

---

## Core Tools

### 1. Video Processing Tools

Located in: `scripts/video_utils.py`

#### get_video_info(video_path)
Get comprehensive video information using ffprobe.

**Parameters**:
- `video_path` (str): Path to video file

**Returns**: Dict with video metadata

**Example**:
```python
from scripts.video_utils import get_video_info

info = get_video_info('video.mp4')
print(f"Duration: {info['format']['duration']}s")
print(f"Resolution: {info['streams'][0]['width']}x{info['streams'][0]['height']}")
```

---

#### resize_video(input_path, output_path, width, height)
Resize video to specified dimensions.

**Parameters**:
- `input_path` (str): Input video path
- `output_path` (str): Output video path
- `width` (int): Target width
- `height` (int): Target height

**Returns**: bool (success/failure)

**Example**:
```python
from scripts.video_utils import resize_video

success = resize_video('input.mp4', 'output.mp4', 1920, 1080)
```

---

#### concatenate_videos(video_paths, output_path)
Concatenate multiple videos into one.

**Parameters**:
- `video_paths` (List[str]): List of video paths to concatenate
- `output_path` (str): Output video path

**Returns**: bool (success/failure)

**Example**:
```python
from scripts.video_utils import concatenate_videos

videos = ['intro.mp4', 'main.mp4', 'outro.mp4']
concatenate_videos(videos, 'final.mp4')
```

---

#### add_audio_to_video(video_path, audio_path, output_path)
Add or replace audio track in video.

**Parameters**:
- `video_path` (str): Input video path
- `audio_path` (str): Audio file path
- `output_path` (str): Output video path

**Returns**: bool (success/failure)

**Example**:
```python
from scripts.video_utils import add_audio_to_video

add_audio_to_video('video.mp4', 'music.mp3', 'output.mp4')
```

---

#### extract_frames(video_path, output_dir, fps)
Extract frames from video at specified fps.

**Parameters**:
- `video_path` (str): Input video path
- `output_dir` (str): Directory for output frames
- `fps` (int): Frames per second to extract

**Returns**: bool (success/failure)

**Example**:
```python
from scripts.video_utils import extract_frames

extract_frames('video.mp4', 'frames/', fps=1)  # 1 frame per second
```

---

#### create_video_from_images(image_dir, output_path, fps)
Create video from sequence of images.

**Parameters**:
- `image_dir` (str): Directory containing images
- `output_path` (str): Output video path
- `fps` (int): Frames per second

**Returns**: bool (success/failure)

**Example**:
```python
from scripts.video_utils import create_video_from_images

create_video_from_images('frames/', 'output.mp4', fps=30)
```

---

#### add_text_overlay(video_path, output_path, text, position)
Add text overlay to video.

**Parameters**:
- `video_path` (str): Input video path
- `output_path` (str): Output video path
- `text` (str): Text to overlay
- `position` (str): Position ('top', 'bottom', 'center')

**Returns**: bool (success/failure)

**Example**:
```python
from scripts.video_utils import add_text_overlay

add_text_overlay('input.mp4', 'output.mp4', 'Subscribe!', 'bottom')
```

---

### 2. API Integration Tools

Located in: `scripts/api_integrations.py`

#### OpenRouterAPI
Client for OpenRouter free models.

**Example**:
```python
from scripts.api_integrations import OpenRouterAPI

api = OpenRouterAPI(api_key='your_key')
text = await api.generate_text("Write a video script", model="llama-2-70b-chat")
```

---

#### OllamaAPI
Client for local Ollama inference.

**Example**:
```python
from scripts.api_integrations import OllamaAPI

api = OllamaAPI()
models = await api.list_models()
text = await api.generate_text("Hello", model="llama2")
```

---

#### ComfyUIAPI
Client for ComfyUI interface.

**Example**:
```python
from scripts.api_integrations import ComfyUIAPI

api = ComfyUIAPI(host="127.0.0.1", port=8188)
prompt_id = await api.queue_prompt(workflow_dict)
history = await api.get_history(prompt_id)
```

---

#### SoraAPI
Client for Sora API (when available).

**Example**:
```python
from scripts.api_integrations import SoraAPI

api = SoraAPI(api_key='your_key')
video = await api.generate_video("Beautiful landscape", duration=10)
```

---

## Command-Line Tools

### Main Orchestrator

```bash
# Research only
python main.py --research-only

# Full workflow with generation
python main.py --generate

# Custom config
python main.py --config custom_config.yaml
```

---

### Quick Start Script

```bash
# Interactive menu
bash quickstart.sh

# Options:
# 1. Research trending topics only
# 2. Run basic workflow example
# 3. Run full workflow (research + generate)
# 4. Start ComfyUI server
# 5. Start Ollama server
```

---

### Test Connections

```bash
# Test all API connections
python examples/test_connections.py

# Tests:
# - Ollama connection
# - ComfyUI connection
# - FFmpeg installation
# - Python packages
```

---

### Example Workflows

```bash
# Basic workflow
python examples/basic_workflow.py

# Scheduled workflow (once)
python examples/scheduled_workflow.py --once

# Scheduled workflow (continuous)
python examples/scheduled_workflow.py --schedule
```

---

### Crew Execution

```bash
# Full production crew
python crews/video_production_crew.py

# Direct Python usage
python -c "
import asyncio
from crews.video_production_crew import VideoProductionCrew
import yaml

with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

crew = VideoProductionCrew(config)
result = asyncio.run(crew.execute_full_production())
print(result)
"
```

---

## Utility Scripts

### Installation Scripts

```bash
# Install everything
bash install/install_all.sh

# Install specific components
bash install/install_comfyui.sh
bash install/install_ollama.sh
bash install/install_additional_tools.sh
```

---

### Agent Tools

#### Trending Topics Agent
```python
from agents.trending_topics_agent import TrendingTopicsAgent

agent = TrendingTopicsAgent(config)
trends = await agent.research()
agent.save_trends(trends, 'output/trends.json')
```

#### Deep Research Agent
```python
from agents.deep_research_agent import DeepResearchAgent

agent = DeepResearchAgent(config)
research = await agent.research_topic('AI Technology')
agent.save_research(research)
```

#### Video Generation Agent
```python
from agents.video_generation_agent import VideoGenerationOrchestrator

agent = VideoGenerationOrchestrator(config)
result = await agent.generate_video(topic_data)
agent.save_metadata(result)
```

#### Video Editing Agent
```python
from agents.video_editing_agent import VideoEditingAgent

agent = VideoEditingAgent(config)

# Apply edits
edits = {'color_grade': 'vibrant', 'trim': {'start': 0, 'duration': 60}}
edited = agent.edit_video(video_path, edits)

# Create short form
short = agent.create_short_form(video_path, duration=60)
```

#### Multi-Platform Upload Agent
```python
from agents.multiplatform_upload_agent import MultiPlatformUploadAgent

agent = MultiPlatformUploadAgent(config)

# Optimize for platform
optimized = agent.optimize_for_platform(video_path, 'tiktok')

# Generate metadata
metadata = agent.generate_platform_specific_metadata(base_metadata, 'youtube_shorts')

# Upload
results = await agent.upload_to_all_platforms(video_path, metadata)

# Get stats
stats = agent.get_upload_stats()
```

---

## Configuration Tools

### Config Management

```python
import yaml

# Load config
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

# Modify config
config['video_generation']['default_resolution'] = '1920x1080'

# Save config
with open('config/config.yaml', 'w') as f:
    yaml.dump(config, f)
```

---

### Environment Variables

```bash
# Set API keys via environment
export OPENAI_API_KEY="your_key"
export OPENROUTER_API_KEY="your_key"
export TIKTOK_API_KEY="your_key"

# Load in Python
import os
api_key = os.getenv('OPENAI_API_KEY')
```

---

## Monitoring Tools

### Log Viewer

```bash
# View main log
tail -f logs/video_toolkit.log

# View errors only
grep ERROR logs/video_toolkit.log

# View upload log
cat logs/multi_platform_upload.json | jq .

# View research results
cat output/trends/trends_latest.json | jq .
```

---

### Performance Monitoring

```python
# Check upload statistics
import json

with open('logs/multi_platform_upload.json') as f:
    logs = json.load(f)

platforms = {}
for log in logs:
    platform = log['platform']
    if platform not in platforms:
        platforms[platform] = {'success': 0, 'failed': 0}
    
    if log['status'] == 'success':
        platforms[platform]['success'] += 1
    else:
        platforms[platform]['failed'] += 1

print(platforms)
```

---

## Development Tools

### Testing

```bash
# Test specific agent
python agents/trending_topics_agent.py
python agents/deep_research_agent.py
python agents/video_editing_agent.py

# Test API integrations
python scripts/api_integrations.py

# Test video utilities
python scripts/video_utils.py
```

---

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use Python debugger
import pdb; pdb.set_trace()

# Trace execution
import sys
import trace

tracer = trace.Trace(count=False, trace=True)
tracer.run('main()')
```

---

## Third-Party Tools Integration

### FFmpeg
```bash
# Check version
ffmpeg -version

# Manual video processing
ffmpeg -i input.mp4 -vf scale=1920:1080 output.mp4

# Convert format
ffmpeg -i input.mov -c:v libx264 output.mp4
```

### Ollama
```bash
# List models
ollama list

# Pull model
ollama pull llama2

# Run model directly
ollama run llama2 "Your prompt"

# Check service
curl http://localhost:11434/api/tags
```

### ComfyUI
```bash
# Start server
cd ComfyUI
python main.py

# Custom port
python main.py --port 8189

# Access UI
open http://127.0.0.1:8188
```

---

## Tool Chains

### Complete Video Creation Chain

```python
# 1. Research
trends = await trending_agent.research()

# 2. Deep research
research = await deep_research_agent.research_topic(trends[0]['title'])

# 3. Generate
result = await generation_agent.generate_video({'title': trends[0]['title']})

# 4. Edit
edited = editing_agent.edit_video(result['video_path'], edits)

# 5. Create short form
short = editing_agent.create_short_form(edited, 60)

# 6. Upload
uploads = await upload_agent.upload_to_all_platforms(short, metadata)
```

---

## Troubleshooting Tools

### Diagnostic Script

```bash
# Create diagnostic report
python -c "
import subprocess
import sys

print('=== System Diagnostics ===')
print(f'Python: {sys.version}')
print(f'FFmpeg: {subprocess.run([\"ffmpeg\", \"-version\"], capture_output=True, text=True).stdout.split()[2]}')

# Check services
print('\\n=== Services ===')
print('Ollama:', 'Running' if subprocess.run(['pgrep', 'ollama'], capture_output=True).returncode == 0 else 'Not running')
print('ComfyUI:', 'Check http://127.0.0.1:8188')

# Check disk space
print('\\n=== Disk Space ===')
subprocess.run(['df', '-h', '.'])
"
```

---

**Document Version**: 1.0
**Last Updated**: 2024-01-27
