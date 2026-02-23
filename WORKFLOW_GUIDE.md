# Complete Workflow Guide

Comprehensive guide for using all features of the Video Generation Toolkit.

## Table of Contents

1. [Quick Start Workflows](#quick-start-workflows)
2. [YouTube Shorts Production](#youtube-shorts-production)
3. [AI-Powered Prompt Creation](#ai-powered-prompt-creation)
4. [Image Generation and Modification](#image-generation-and-modification)
5. [Video Analysis and Quality Control](#video-analysis-and-quality-control)
6. [Automated Video Production](#automated-video-production)
7. [Integration Examples](#integration-examples)

---

## Quick Start Workflows

### Workflow 1: Create a YouTube Short (Fastest)

```bash
# 1. Download and create Shorts from YouTube video
python examples/create_shorts.py
# Choose option 1, enter YouTube URL

# Output: Multiple optimized Shorts in output/shorts/
```

### Workflow 2: Enhance Your Prompts

```bash
# 2. Make your prompts production-ready
python examples/prompt_enhancement_demo.py
# Choose interactive mode

# Input: "a cat in a garden"
# Output: Full cinematic prompt with technical details
```

### Workflow 3: Generate Images with Enhanced Prompts

```python
from agents.prompt_enhancement_agent import PromptEnhancementAgent
from scripts.openai_tools.image_generation import OpenAIImageGenerator

# Enhance prompt
prompt_agent = PromptEnhancementAgent(config)
result = prompt_agent.enhance_prompt("a futuristic city", style='cinematic')

# Generate image
image_gen = OpenAIImageGenerator()
images = image_gen.generate_image(result['enhanced'])
```

---

## YouTube Shorts Production

### Complete Shorts Pipeline

```python
from agents.youtube_shorts_agent import YouTubeShortsAgent
from agents.video_analysis_agent import VideoAnalysisAgent
from agents.video_editing_agent import VideoEditingAgent

config = {
    'video_generation': {'output_directory': 'output/shorts'},
    'workflow': {'temp_directory': 'temp'}
}

# Initialize agents
shorts_agent = YouTubeShortsAgent(config)
analysis_agent = VideoAnalysisAgent(config)
editing_agent = VideoEditingAgent(config)

# Step 1: Download or use local video
video_path = shorts_agent.download_video('https://youtube.com/watch?v=...')
# OR
video_path = 'my_local_video.mp4'

# Step 2: Analyze video
analysis = analysis_agent.analyze_comprehensive(video_path)
print(f"Quality: {analysis['quality']['overall_score']}")
print(f"Duration: {analysis['metadata']['duration']}s")

# Check recommendations
for rec in analysis['recommendations']:
    print(f"• {rec}")

# Step 3: Create Shorts
if analysis['quality']['overall_score'] in ['Excellent', 'Good']:
    shorts = shorts_agent.create_shorts_from_video(video_path, auto_analyze=True)
    print(f"Created {len(shorts)} Shorts")
else:
    print("Video quality needs improvement")

# Step 4: Enhance each Short
enhanced_shorts = []
for i, short in enumerate(shorts):
    # Add effects
    enhanced = editing_agent.edit_video(short, {
        'color_grade': 'vibrant',
        'add_music': {
            'path': 'music/background.mp3',
            'volume': 0.3
        }
    })
    
    # Add branding
    branded = shorts_agent.add_shorts_branding(
        enhanced,
        logo_path='branding/logo.png',
        watermark_text='@YourChannel'
    )
    
    enhanced_shorts.append(branded)
    print(f"Enhanced Short {i+1}: {branded}")

print(f"\n✓ Pipeline complete! Created {len(enhanced_shorts)} branded Shorts")
```

### Batch Shorts Production

```python
import glob

# Get all videos
videos = glob.glob('input_videos/*.mp4')

all_shorts = []
for video in videos:
    print(f"Processing: {video}")
    
    # Quick quality check
    analysis = analysis_agent.get_metadata(video)
    
    if analysis.get('duration', 0) > 10:  # At least 10 seconds
        shorts = shorts_agent.create_shorts_from_video(video)
        all_shorts.extend(shorts)

print(f"Total Shorts created: {len(all_shorts)}")
```

---

## AI-Powered Prompt Creation

### Basic Prompt Enhancement

```python
from agents.prompt_enhancement_agent import PromptEnhancementAgent

agent = PromptEnhancementAgent(config)

# Simple to detailed
simple = "a sunset over mountains"
result = agent.enhance_prompt(simple, style='cinematic', creativity=0.8)

print(f"Original: {result['original']}")
print(f"Enhanced: {result['enhanced']}")
print(f"Negative: {result['negative']}")
```

### Scene Breakdown for Video

```python
# Break a scene into frames for video generation
scene = "a spaceship landing on an alien planet at sunrise"
frames = agent.break_down_scene(scene, num_frames=8)

# Generate each frame
for i, frame in enumerate(frames):
    print(f"\n=== Frame {i+1}/{len(frames)} ===")
    print(f"Progress: {frame['progress']*100:.0f}%")
    print(f"Prompt: {frame['prompt']}")
    
    # Use with image/video generator
    # image = generate_image(frame['prompt'], frame['negative'])
```

### Style Variations

```python
base_prompt = "a mysterious forest at night"

styles = {
    'cinematic': 'Film-quality video',
    'artistic': 'Artistic illustration',
    'realistic': 'Photorealistic image',
    'animation': 'Animated style'
}

for style_name, description in styles.items():
    result = agent.enhance_prompt(base_prompt, style=style_name)
    print(f"\n{style_name.upper()} ({description}):")
    print(result['enhanced'][:150] + "...")
```

### Research-Based Prompts

```python
# Use Gemini for research and prompt creation
from scripts.gemini_tools.gemini_client import GeminiClient

gemini = GeminiClient()

# Research a topic
topic = "cyberpunk street scene"
research = gemini.research_topic(topic)
print(f"Research: {research}")

# Generate script
script = gemini.generate_video_script(topic, duration=30)
print(f"Script: {script['script']}")

# Break into frames
frames = gemini.break_down_scene(topic, num_frames=5)
```

---

## Image Generation and Modification

### Generate Images with DALL-E

```python
from scripts.openai_tools.image_generation import OpenAIImageGenerator
from agents.prompt_enhancement_agent import PromptEnhancementAgent

# Enhance prompt first
prompt_agent = PromptEnhancementAgent(config)
result = prompt_agent.enhance_prompt(
    "a cat astronaut in space",
    style='cinematic'
)

# Generate image
image_gen = OpenAIImageGenerator()
images = image_gen.generate_image(
    result['enhanced'],
    model='dall-e-3',
    size='1024x1024',
    quality='hd'
)

# Save image
for i, image in enumerate(images):
    filename = image_gen.save_image(image.url, 'output/images')
    print(f"Saved: {filename}")
```

### Image Inpainting

```python
from agents.inpainting_agent import InpaintingAgent

inpaint_agent = InpaintingAgent(config)

# Remove object
result = inpaint_agent.remove_object(
    'photo.png',
    'object_mask.png'
)

# Replace object
result = inpaint_agent.replace_object(
    'photo.png',
    'object_mask.png',
    'a red sports car, photorealistic'
)

# Enhance region
result = inpaint_agent.enhance_region(
    'photo.png',
    'region_mask.png',
    'higher detail, sharper, more vibrant colors'
)
```

### Batch Image Processing

```python
images_to_process = [
    ('image1.png', 'mask1.png', 'a tree'),
    ('image2.png', 'mask2.png', 'a building'),
    ('image3.png', 'mask3.png', 'a person')
]

results = inpaint_agent.batch_inpaint(images_to_process)

for i, result in enumerate(results):
    if result:
        print(f"✓ Processed image {i+1}: {result}")
    else:
        print(f"✗ Failed to process image {i+1}")
```

---

## Video Analysis and Quality Control

### Comprehensive Analysis

```python
from agents.video_analysis_agent import VideoAnalysisAgent

agent = VideoAnalysisAgent(config)

# Full analysis
analysis = agent.analyze_comprehensive('video.mp4')

# Print report
print("=== Video Analysis Report ===\n")

print(f"Duration: {analysis['metadata']['duration']:.1f}s")
print(f"Resolution: {analysis['technical']['width']}x{analysis['technical']['height']}")
print(f"Codec: {analysis['technical']['codec']}")
print(f"FPS: {analysis['technical']['fps']}")
print(f"Bitrate: {analysis['metadata']['bitrate']/1000:.0f} kbps")

print(f"\nQuality Assessment:")
print(f"  Resolution: {analysis['quality']['resolution_quality']}")
print(f"  Bitrate: {analysis['quality']['bitrate_quality']}")
print(f"  FPS: {analysis['quality']['fps_quality']}")
print(f"  Overall: {analysis['quality']['overall_score']}")

if analysis.get('audio'):
    print(f"\nAudio:")
    print(f"  Codec: {analysis['audio'].get('codec', 'N/A')}")
    print(f"  Sample Rate: {analysis['audio'].get('sample_rate', 0)} Hz")

print(f"\nRecommendations:")
for rec in analysis['recommendations']:
    print(f"  • {rec}")
```

### Quality-Based Workflow

```python
def process_based_on_quality(video_path):
    analysis = analysis_agent.analyze_comprehensive(video_path)
    score = analysis['quality']['overall_score']
    
    if score == 'Excellent':
        # Use as-is, create multiple shorts
        return shorts_agent.create_shorts_from_video(
            video_path,
            num_shorts=5
        )
    
    elif score == 'Good':
        # Minor enhancement, create shorts
        enhanced = editing_agent.edit_video(video_path, {
            'color_grade': 'vibrant'
        })
        return shorts_agent.create_shorts_from_video(enhanced)
    
    else:
        # Significant enhancement needed
        print(f"Video quality is {score}")
        print("Recommendations:")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")
        return []

shorts = process_based_on_quality('my_video.mp4')
```

---

## Automated Video Production

### End-to-End Automated Workflow

```python
from agents.trending_topics_agent import TrendingTopicsAgent
from agents.deep_research_agent import DeepResearchAgent

# Full automation pipeline
class AutomatedProduction:
    def __init__(self, config):
        self.config = config
        self.trends = TrendingTopicsAgent(config)
        self.research = DeepResearchAgent(config)
        self.prompt = PromptEnhancementAgent(config)
        self.shorts = YouTubeShortsAgent(config)
    
    async def run(self):
        # 1. Find trending topic
        trends = await self.trends.research()
        top_trend = trends[0]
        print(f"Topic: {top_trend['topic']}")
        
        # 2. Research topic
        research = await self.research.research_topic(top_trend['topic'])
        
        # 3. Create prompts
        scenes = self.prompt.break_down_scene(
            research['summary'],
            num_frames=5
        )
        
        # 4. Generate images/videos for each scene
        # (integrate with your generation method)
        
        # 5. Create final video
        # (combine scenes, add music, etc.)
        
        # 6. Upload
        # (integrate with upload agent)
        
        print("✓ Automated production complete!")

# Run
import asyncio
pipeline = AutomatedProduction(config)
asyncio.run(pipeline.run())
```

---

## Integration Examples

### ComfyUI Integration

```python
from scripts.api_integrations import ComfyUIAPI
import json

# Load workflow
with open('workflows/text_to_video_animatediff.json') as f:
    workflow = json.load(f)

# Enhance prompt first
prompt_result = prompt_agent.enhance_prompt(
    "a cat walking in a garden",
    style='animation'
)

# Update workflow with enhanced prompt
workflow['2']['inputs']['text'] = prompt_result['enhanced']
workflow['3']['inputs']['text'] = prompt_result['negative']

# Queue and generate
api = ComfyUIAPI()
prompt_id = api.queue_prompt(workflow)

# Wait for result
result = api.wait_for_completion(prompt_id)
print(f"Video generated: {result}")
```

### Multi-Platform Distribution

```python
from agents.multiplatform_upload_agent import MultiPlatformUploadAgent

upload_agent = MultiPlatformUploadAgent(config)

# Prepare metadata
metadata = {
    'title': 'Amazing Content',
    'description': 'Check out this amazing content!',
    'tags': ['trending', 'viral', 'shorts']
}

# Upload to multiple platforms
results = await upload_agent.upload_to_all_platforms(
    video_path='output/shorts/final.mp4',
    metadata=metadata,
    platforms=['youtube', 'tiktok']  # Future support
)
```

---

## Tips and Best Practices

### 1. Prompt Engineering

- Start simple, let the agent enhance
- Use specific style templates
- Adjust creativity level based on needs
- Always use negative prompts for better results

### 2. Video Quality

- Always analyze before processing
- Follow recommendations
- Test with lower quality first
- Optimize for target platform

### 3. Automation

- Start with manual workflows
- Gradually automate proven processes
- Monitor results and adjust
- Use batch processing for efficiency

### 4. Resource Management

- Use temp directories for intermediate files
- Clean up after processing
- Cache frequently used resources
- Monitor disk space

---

## Troubleshooting

### Common Issues

**Issue: Low quality output**
- Solution: Analyze source first, follow recommendations
- Increase resolution/bitrate if needed

**Issue: Slow processing**
- Solution: Use batch processing, optimize settings
- Consider using lower quality for testing

**Issue: Agent errors**
- Solution: Check logs, verify dependencies
- Run validation script: `./install/validate_installation.sh`

---

**Last Updated**: 2024-02-13
