# AI Agents Guide

Comprehensive guide to all AI agents in the Video Generation Toolkit.

## Table of Contents

1. [Overview](#overview)
2. [Agent Architecture](#agent-architecture)
3. [Available Agents](#available-agents)
4. [Agent Communication](#agent-communication)
5. [Creating Custom Agents](#creating-custom-agents)

---

## Overview

The Video Generation Toolkit uses specialized AI agents to handle different aspects of video creation, from research and generation to editing and upload. Each agent is designed to be:

- **Autonomous**: Can operate independently
- **Specialized**: Focused on specific tasks
- **Collaborative**: Can work with other agents
- **Extensible**: Easy to customize and extend

---

## Agent Architecture

### Base Agent Pattern

All agents follow a consistent pattern:

```python
class Agent:
    def __init__(self, config: Dict):
        """Initialize with configuration"""
        self.config = config
        self.setup_directories()
        self.load_resources()
    
    def execute(self, task: Dict) -> Dict:
        """Main execution method"""
        pass
    
    def validate(self, result: Dict) -> bool:
        """Validate results"""
        pass
```

### Configuration

Agents are configured through `config/config.yaml`:

```yaml
agents:
  youtube_shorts:
    output_directory: "output/shorts"
    max_duration: 60
  
  prompt_enhancement:
    templates_directory: "prompts"
    creativity_level: 0.7
```

---

## Available Agents

### 1. YouTube Shorts Agent

**Purpose**: Create, optimize, and manage YouTube Shorts

**Capabilities**:
- Download videos from YouTube
- Analyze videos for Shorts potential
- Create Shorts from longer videos
- Optimize for vertical format
- Add branding elements

**Usage**:
```python
from agents.youtube_shorts_agent import YouTubeShortsAgent

agent = YouTubeShortsAgent(config)

# Create Shorts from video
shorts = agent.create_shorts_from_video('video.mp4')
```

**Documentation**: See [YouTube Shorts Guide](YOUTUBE_SHORTS.md)

---

### 2. Video Analysis Agent

**Purpose**: Analyze videos to extract metadata and insights

**Capabilities**:
- Extract metadata (duration, resolution, bitrate)
- Analyze technical quality
- Detect scenes and keyframes
- Analyze audio
- Provide recommendations

**Usage**:
```python
from agents.video_analysis_agent import VideoAnalysisAgent

agent = VideoAnalysisAgent(config)

# Comprehensive analysis
analysis = agent.analyze_comprehensive('video.mp4')
print(f"Quality: {analysis['quality']['overall_score']}")
```

**Key Methods**:
- `analyze_comprehensive()` - Full analysis
- `get_metadata()` - Basic metadata
- `detect_scenes()` - Scene detection
- `assess_quality()` - Quality assessment

---

### 3. Inpainting Agent

**Purpose**: Modify images using AI inpainting

**Capabilities**:
- Inpaint regions of images
- Remove objects
- Replace objects
- Enhance specific regions
- Batch processing
- Generate variations

**Usage**:
```python
from agents.inpainting_agent import InpaintingAgent

agent = InpaintingAgent(config)

# Remove object
result = agent.remove_object('image.png', 'mask.png')

# Replace object
result = agent.replace_object(
    'image.png',
    'mask.png',
    'a red sports car'
)
```

**Key Methods**:
- `inpaint_image()` - Basic inpainting
- `remove_object()` - Object removal
- `replace_object()` - Object replacement
- `enhance_region()` - Regional enhancement
- `batch_inpaint()` - Batch processing

---

### 4. Prompt Enhancement Agent

**Purpose**: Enhance simple prompts into detailed, production-ready prompts

**Capabilities**:
- Enhance basic prompts with technical details
- Break down scenes into frames
- Apply style templates
- Generate negative prompts
- Research topics (future)

**Usage**:
```python
from agents.prompt_enhancement_agent import PromptEnhancementAgent

agent = PromptEnhancementAgent(config)

# Enhance prompt
result = agent.enhance_prompt(
    "a cat in a garden",
    style='cinematic',
    creativity=0.8
)

print(f"Enhanced: {result['enhanced']}")
print(f"Negative: {result['negative']}")
```

**Key Methods**:
- `enhance_prompt()` - Enhance simple prompts
- `break_down_scene()` - Scene to frames
- `research_prompt()` - Research topics

**Style Options**:
- `cinematic` - Film-quality prompts
- `artistic` - Artistic style
- `realistic` - Photorealistic
- `animation` - Animation style

---

### 5. Video Generation Agent

**Purpose**: Orchestrate video generation workflow

**Capabilities**:
- Coordinate with multiple AI platforms
- Manage generation queue
- Handle retries and errors
- Optimize settings

**Usage**:
```python
from agents.video_generation_agent import VideoGenerationOrchestrator

agent = VideoGenerationOrchestrator(config)

# Generate video
result = await agent.generate_video({
    'prompt': 'cinematic scene of...',
    'duration': 10,
    'style': 'cinematic'
})
```

---

### 6. Video Editing Agent

**Purpose**: Automated video editing and enhancement

**Capabilities**:
- Trim and cut videos
- Add transitions
- Color grading
- Add music and effects
- Generate subtitles
- Create short-form content

**Usage**:
```python
from agents.video_editing_agent import VideoEditingAgent

agent = VideoEditingAgent(config)

# Edit video
edited = agent.edit_video('video.mp4', {
    'trim': {'start': 0, 'duration': 30},
    'color_grade': 'vibrant',
    'add_music': {'path': 'music.mp3', 'volume': 0.3}
})
```

---

### 7. Trending Topics Agent

**Purpose**: Research trending content opportunities

**Capabilities**:
- Monitor social media trends
- Analyze YouTube trends
- Track Google Trends
- Identify viral content patterns
- Generate content ideas

**Usage**:
```python
from agents.trending_topics_agent import TrendingTopicsAgent

agent = TrendingTopicsAgent(config)

# Research trends
trends = await agent.research()

for trend in trends[:5]:
    print(f"Topic: {trend['topic']}")
    print(f"Score: {trend['score']}")
```

---

### 8. Deep Research Agent

**Purpose**: In-depth research and content planning

**Capabilities**:
- Web search and analysis
- Fact-checking
- Competitor analysis
- Content outline generation

---

### 9. Multi-platform Upload Agent

**Purpose**: Upload content to multiple platforms

**Capabilities**:
- YouTube upload
- TikTok upload (future)
- Instagram Reels (future)
- Metadata generation
- Scheduling

---

## Agent Communication

### Direct Communication

Agents can call each other directly:

```python
# Analysis agent feeds into Shorts agent
analysis_agent = VideoAnalysisAgent(config)
shorts_agent = YouTubeShortsAgent(config)

# Analyze
analysis = analysis_agent.analyze_comprehensive('video.mp4')

# Use analysis results
if analysis['quality']['overall_score'] == 'Excellent':
    shorts = shorts_agent.create_shorts_from_video('video.mp4')
```

### Pipeline Pattern

Create processing pipelines:

```python
class VideoPipeline:
    def __init__(self, config):
        self.analysis = VideoAnalysisAgent(config)
        self.shorts = YouTubeShortsAgent(config)
        self.editing = VideoEditingAgent(config)
    
    def process(self, video_path):
        # Step 1: Analyze
        analysis = self.analysis.analyze_comprehensive(video_path)
        
        # Step 2: Create Shorts
        shorts = self.shorts.create_shorts_from_video(video_path)
        
        # Step 3: Enhance each Short
        enhanced = []
        for short in shorts:
            edited = self.editing.edit_video(short, {
                'color_grade': 'vibrant',
                'add_music': {'path': 'music.mp3'}
            })
            enhanced.append(edited)
        
        return enhanced

# Use pipeline
pipeline = VideoPipeline(config)
results = pipeline.process('video.mp4')
```

### Event-Driven Communication

Agents can emit events:

```python
class Agent:
    def __init__(self, config):
        self.listeners = []
    
    def on_complete(self, callback):
        self.listeners.append(callback)
    
    def emit(self, event, data):
        for listener in self.listeners:
            listener(event, data)

# Usage
shorts_agent = YouTubeShortsAgent(config)
editing_agent = VideoEditingAgent(config)

# Listen for completion
shorts_agent.on_complete(
    lambda event, data: editing_agent.edit_video(data['path'])
)
```

---

## Creating Custom Agents

### Basic Template

```python
"""
Custom Agent Template
"""

import os
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomAgent:
    """Custom agent for specific task"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = config.get('output_directory', 'output')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def execute(self, task: Dict) -> Dict:
        """Main execution method"""
        logger.info(f"Executing task: {task}")
        
        try:
            # Your logic here
            result = self._process(task)
            
            return {
                'success': True,
                'result': result
            }
        
        except Exception as e:
            logger.error(f"Error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process(self, task: Dict):
        """Internal processing"""
        # Implement your logic
        pass
    
    def validate(self, result: Dict) -> bool:
        """Validate results"""
        return result.get('success', False)


def main():
    """Example usage"""
    config = {'output_directory': 'output/custom'}
    agent = CustomAgent(config)
    
    result = agent.execute({'action': 'test'})
    print(f"Success: {result['success']}")


if __name__ == '__main__':
    main()
```

### Best Practices

1. **Single Responsibility**: Each agent should do one thing well
2. **Configuration**: Use config for all settings
3. **Logging**: Log all important actions
4. **Error Handling**: Handle errors gracefully
5. **Testing**: Write comprehensive tests
6. **Documentation**: Document all methods

### Testing Custom Agents

```python
"""
Tests for Custom Agent
"""

import pytest
from agents.custom_agent import CustomAgent


@pytest.fixture
def config():
    return {'output_directory': 'test_output'}


@pytest.fixture
def agent(config):
    return CustomAgent(config)


class TestCustomAgent:
    def test_init(self, agent, config):
        assert agent.config == config
    
    def test_execute_success(self, agent):
        result = agent.execute({'action': 'test'})
        assert result['success'] is True
    
    def test_execute_failure(self, agent):
        result = agent.execute({'action': 'invalid'})
        assert result['success'] is False
```

---

## Agent Coordination Patterns

### Sequential Processing

```python
def sequential_workflow(video_path):
    # Step 1
    analysis = analysis_agent.analyze(video_path)
    
    # Step 2
    shorts = shorts_agent.create_shorts(video_path, analysis)
    
    # Step 3
    enhanced = [editing_agent.enhance(s) for s in shorts]
    
    return enhanced
```

### Parallel Processing

```python
import asyncio

async def parallel_workflow(videos):
    tasks = [
        shorts_agent.create_shorts_async(video)
        for video in videos
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

### Conditional Processing

```python
def conditional_workflow(video_path):
    analysis = analysis_agent.analyze(video_path)
    
    if analysis['quality']['score'] > 80:
        # High quality - create multiple shorts
        return shorts_agent.create_multiple(video_path, count=5)
    else:
        # Lower quality - enhance first
        enhanced = editing_agent.enhance(video_path)
        return shorts_agent.create_single(enhanced)
```

---

## Monitoring and Debugging

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agents.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Performance Tracking

```python
import time

class Agent:
    def execute(self, task):
        start = time.time()
        
        result = self._process(task)
        
        duration = time.time() - start
        logger.info(f"Execution took {duration:.2f}s")
        
        return result
```

---

**Last Updated**: 2024-02-13
