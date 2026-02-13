# YouTube Shorts Workflow Guide

Complete guide for creating, analyzing, and optimizing YouTube Shorts using the Video Generation Toolkit.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Features](#features)
5. [Workflows](#workflows)
6. [API Reference](#api-reference)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

---

## Overview

The YouTube Shorts workflow provides comprehensive tools for:

- **Creating Shorts from existing videos** - Automatically segment longer videos into optimal Shorts
- **Downloading and analyzing YouTube videos** - Extract videos and analyze for Shorts potential
- **Optimizing for Shorts format** - Convert to vertical 9:16 aspect ratio with proper encoding
- **Adding branding and effects** - Watermarks, logos, and visual enhancements
- **Batch processing** - Process multiple videos efficiently

## Installation

### Requirements

- Python 3.8+
- FFmpeg (for video processing)
- yt-dlp (for YouTube downloads)

### Install

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install specific packages
pip install yt-dlp moviepy opencv-python
```

### Verify Installation

```bash
# Check FFmpeg
ffmpeg -version

# Check yt-dlp
yt-dlp --version
```

---

## Quick Start

### 1. Basic Shorts Creation

```python
from agents.youtube_shorts_agent import YouTubeShortsAgent

config = {
    'video_generation': {'output_directory': 'output/shorts'},
    'workflow': {'temp_directory': 'temp'}
}

agent = YouTubeShortsAgent(config)

# Create a Short from local video
short = agent.create_short(
    'my_video.mp4',
    start_time=0,
    duration=60
)

print(f"Short created: {short}")
```

### 2. Download and Create Shorts

```python
# Download from YouTube
video_path = agent.download_video('https://youtube.com/watch?v=...')

# Create multiple Shorts automatically
shorts = agent.create_shorts_from_video(video_path)

print(f"Created {len(shorts)} Shorts")
```

### 3. Using the CLI Example

```bash
python examples/create_shorts.py
```

---

## Features

### Video Analysis

Comprehensive video analysis to determine optimal Shorts segments:

```python
from agents.video_analysis_agent import VideoAnalysisAgent

analysis_agent = VideoAnalysisAgent(config)
analysis = analysis_agent.analyze_comprehensive('video.mp4')

print(f"Duration: {analysis['metadata']['duration']}s")
print(f"Resolution: {analysis['technical']['width']}x{analysis['technical']['height']}")
print(f"Quality: {analysis['quality']['overall_score']}")

# Get recommendations
for rec in analysis['recommendations']:
    print(f"  • {rec}")
```

### Automatic Segmentation

The agent intelligently suggests segments based on:

- Video duration
- Scene changes
- Optimal Shorts length (up to 60 seconds)
- Minimum segment length (10 seconds)

```python
# Analyze and get suggested segments
analysis = agent.analyze_video('video.mp4')
segments = analysis['suggested_segments']

for seg in segments:
    print(f"Segment: {seg['start']:.1f}s - {seg['end']:.1f}s")
```

### Format Optimization

Automatically optimize for YouTube Shorts format:

```python
# Convert to vertical format (9:16)
optimized = agent.optimize_for_shorts('video.mp4')
```

**Optimization includes:**
- Vertical aspect ratio (1080x1920)
- Proper encoding (H.264)
- Optimized bitrate for mobile
- Audio normalization

### Branding

Add branding elements to your Shorts:

```python
branded = agent.add_shorts_branding(
    'short.mp4',
    logo_path='logo.png',
    watermark_text='@YourChannel'
)
```

---

## Workflows

### Workflow 1: YouTube Video to Shorts

Complete workflow for converting YouTube videos to Shorts:

```python
from agents.youtube_shorts_agent import YouTubeShortsAgent
from agents.video_analysis_agent import VideoAnalysisAgent

# Initialize agents
shorts_agent = YouTubeShortsAgent(config)
analysis_agent = VideoAnalysisAgent(config)

# Step 1: Download
url = 'https://youtube.com/watch?v=...'
video_path = shorts_agent.download_video(url)

# Step 2: Analyze
analysis = analysis_agent.analyze_comprehensive(video_path)

# Step 3: Create Shorts
shorts = shorts_agent.create_shorts_from_video(
    video_path,
    auto_analyze=True
)

# Step 4: Optimize each Short
for i, short in enumerate(shorts):
    optimized = shorts_agent.optimize_for_shorts(short)
    print(f"Optimized Short {i+1}: {optimized}")
```

### Workflow 2: Local Video Processing

Process local video files:

```python
# Analyze video first
analysis = analysis_agent.analyze_comprehensive('my_video.mp4')

# Check if it's suitable for Shorts
duration = analysis['metadata']['duration']
if duration <= 60:
    # Entire video can be one Short
    short = shorts_agent.optimize_for_shorts('my_video.mp4')
else:
    # Create multiple Shorts
    shorts = shorts_agent.create_shorts_from_video(
        'my_video.mp4',
        num_shorts=3  # Create 3 Shorts
    )
```

### Workflow 3: Batch Processing

Process multiple videos:

```python
video_files = ['video1.mp4', 'video2.mp4', 'video3.mp4']

all_shorts = []
for video in video_files:
    shorts = shorts_agent.create_shorts_from_video(video)
    all_shorts.extend(shorts)

print(f"Total Shorts created: {len(all_shorts)}")
```

---

## API Reference

### YouTubeShortsAgent

#### `__init__(config: Dict)`

Initialize the agent with configuration.

#### `download_video(url: str) -> str`

Download video from YouTube URL.

**Parameters:**
- `url`: YouTube video URL

**Returns:**
- Path to downloaded video file

#### `analyze_video(video_path: str) -> Dict`

Analyze video and suggest Shorts segments.

**Returns:**
```python
{
    'duration': float,
    'width': int,
    'height': int,
    'fps': float,
    'aspect_ratio': float,
    'is_vertical': bool,
    'suggested_segments': [
        {'start': float, 'end': float, 'duration': float},
        ...
    ]
}
```

#### `create_short(video_path: str, start_time: float, duration: float, add_captions: bool, optimize_audio: bool) -> str`

Create a single Short from video.

**Parameters:**
- `video_path`: Path to source video
- `start_time`: Start time in seconds
- `duration`: Duration in seconds (max 60)
- `add_captions`: Add automatic captions (future)
- `optimize_audio`: Optimize audio settings

**Returns:**
- Path to created Short

#### `create_shorts_from_video(video_path: str, num_shorts: int, auto_analyze: bool) -> List[str]`

Create multiple Shorts from a video.

**Returns:**
- List of paths to created Shorts

#### `optimize_for_shorts(video_path: str) -> str`

Optimize video for Shorts format.

**Returns:**
- Path to optimized video

#### `add_shorts_branding(video_path: str, logo_path: str, watermark_text: str) -> str`

Add branding elements.

**Returns:**
- Path to branded video

### VideoAnalysisAgent

#### `analyze_comprehensive(video_path: str) -> Dict`

Perform comprehensive video analysis.

**Returns:**
```python
{
    'metadata': {...},
    'technical': {...},
    'scenes': [...],
    'audio': {...},
    'quality': {...},
    'recommendations': [...]
}
```

---

## Best Practices

### 1. Video Selection

**Good for Shorts:**
- High energy content
- Clear focal point
- Good lighting and audio
- Engaging first 3 seconds
- Duration 15-60 seconds

**Avoid:**
- Long, slow-paced content
- Poor audio quality
- Horizontal-only content that doesn't crop well
- Copyright issues

### 2. Segment Selection

When creating Shorts from longer videos:

- **Use the hook**: Start with the most engaging part
- **Complete ideas**: Each Short should tell a complete story
- **Test segments**: Create variations and test performance
- **Add context**: Use text overlays to provide context

### 3. Optimization

**Technical:**
- Always use vertical format (9:16)
- Target 1080x1920 resolution
- Use 30fps minimum
- Optimize file size (under 50MB)

**Creative:**
- Add captions for accessibility
- Use bold, readable text
- Include call-to-action
- Add background music

### 4. Batch Processing

For efficiency:

```python
# Process in batches
batch_size = 5
video_list = get_video_list()

for i in range(0, len(video_list), batch_size):
    batch = video_list[i:i+batch_size]
    for video in batch:
        process_video(video)
```

---

## Examples

### Example 1: Simple Short Creation

```python
from agents.youtube_shorts_agent import YouTubeShortsAgent

config = {
    'video_generation': {'output_directory': 'output/shorts'},
    'workflow': {'temp_directory': 'temp'}
}

agent = YouTubeShortsAgent(config)

# Create a 30-second Short
short = agent.create_short(
    'input_video.mp4',
    start_time=10,    # Start at 10 seconds
    duration=30,      # 30-second Short
    add_captions=False,
    optimize_audio=True
)

print(f"Created Short: {short}")
```

### Example 2: Automatic Segmentation

```python
# Let the agent decide the best segments
shorts = agent.create_shorts_from_video(
    'long_video.mp4',
    auto_analyze=True
)

for i, short in enumerate(shorts):
    print(f"Short {i+1}: {short}")
```

### Example 3: Full Pipeline with Branding

```python
# Download
video = agent.download_video('https://youtube.com/watch?v=abc123')

# Create Shorts
shorts = agent.create_shorts_from_video(video)

# Add branding to each
branded_shorts = []
for short in shorts:
    # Optimize
    optimized = agent.optimize_for_shorts(short)
    
    # Add branding
    branded = agent.add_shorts_branding(
        optimized,
        logo_path='my_logo.png',
        watermark_text='@MyChannel'
    )
    
    branded_shorts.append(branded)

print(f"Created {len(branded_shorts)} branded Shorts")
```

### Example 4: Quality Check Before Creation

```python
from agents.video_analysis_agent import VideoAnalysisAgent

analysis_agent = VideoAnalysisAgent(config)

# Analyze first
analysis = analysis_agent.analyze_comprehensive('video.mp4')

# Check quality
quality_score = analysis['quality']['overall_score']

if quality_score in ['Excellent', 'Good']:
    print("Video quality is good, proceeding...")
    shorts = shorts_agent.create_shorts_from_video('video.mp4')
else:
    print(f"Video quality is {quality_score}")
    print("Recommendations:")
    for rec in analysis['recommendations']:
        print(f"  • {rec}")
```

---

## Troubleshooting

### Common Issues

**Issue: Download fails**
```
Solution: Check URL, internet connection, and yt-dlp installation
```

**Issue: Poor quality Shorts**
```
Solution: Check source video quality, adjust encoding settings
```

**Issue: Audio out of sync**
```
Solution: Use optimize_audio=True or adjust audio settings manually
```

### Performance Tips

1. **Use temp directory**: Set a fast temp directory (SSD)
2. **Batch processing**: Process multiple videos together
3. **Preset selection**: Use faster encoding presets for drafts
4. **Resolution**: Test with lower resolution first

---

## Additional Resources

- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [YouTube Shorts Specifications](https://support.google.com/youtube/answer/10059070)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)

---

**Last Updated**: 2024-02-13
