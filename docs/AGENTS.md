# Video Generation Toolkit - Agents Documentation

## Overview

The toolkit includes three main agents that work together to create an automated video generation pipeline.

## Agents

### 1. Trending Topics Agent

**Purpose**: Research and identify trending topics across multiple platforms.

**File**: `agents/trending_topics_agent.py`

**Key Features**:
- Multi-source data aggregation (Reddit, YouTube, Google Trends)
- Scoring algorithm to evaluate video potential
- Asynchronous data fetching for speed
- JSON export for persistence

**Usage Example**:
```python
from agents.trending_topics_agent import TrendingTopicsAgent

config = {
    'research': {
        'sources': ['reddit', 'youtube', 'google_trends'],
        'topics_to_track': 10
    }
}

agent = TrendingTopicsAgent(config)
trends = await agent.research()

# Save trends
agent.save_trends(trends, 'output/trends.json')
```

**Methods**:
- `fetch_reddit_trends()` - Fetch from Reddit's hot posts
- `fetch_youtube_trends()` - Fetch from YouTube trending
- `fetch_google_trends()` - Fetch from Google Trends
- `analyze_trends()` - Score and rank trends
- `research()` - Main research method
- `save_trends()` - Save results to JSON

### 2. Video Generation Agent

**Purpose**: Orchestrate the video generation process from topic to final video.

**File**: `agents/video_generation_agent.py`

**Key Features**:
- Script generation from topics
- Visual prompt creation
- Multi-platform generation (Sora, ComfyUI, etc.)
- Video assembly
- Metadata tracking

**Usage Example**:
```python
from agents.video_generation_agent import VideoGenerationOrchestrator

config = {
    'video_generation': {
        'output_directory': 'output/videos',
        'default_resolution': '1920x1080',
        'default_fps': 30
    },
    'api_keys': {
        'openai': 'YOUR_KEY'
    }
}

orchestrator = VideoGenerationOrchestrator(config)

topic = {
    'title': 'Amazing AI Technology',
    'source': 'reddit',
    'score': 5000
}

result = await orchestrator.generate_video(topic)
```

**Methods**:
- `generate_script()` - Create video script from topic
- `generate_prompts()` - Extract visual prompts
- `generate_with_comfyui()` - Generate using ComfyUI
- `generate_with_sora()` - Generate using Sora API
- `generate_with_openrouter()` - Generate using OpenRouter
- `assemble_video()` - Combine frames into video
- `generate_video()` - Complete workflow
- `save_metadata()` - Save generation metadata

### 3. Video Upload Agent

**Purpose**: Handle uploading videos to various platforms with scheduling and metadata management.

**File**: `agents/video_upload_agent.py`

**Key Features**:
- YouTube upload with OAuth2
- Automatic metadata generation
- Upload scheduling
- Rate limiting
- Upload logging

**Usage Example**:
```python
from agents.video_upload_agent import VideoUploadAgent

config = {
    'upload': {
        'enabled': True,
        'platforms': ['youtube'],
        'max_videos_per_day': 5
    }
}

agent = VideoUploadAgent(config)

# Generate metadata
metadata = agent.generate_metadata(topic, script)

# Upload video
results = await agent.upload_video(video_path, metadata)

# Save log
agent.save_upload_log(results)
```

**Methods**:
- `check_upload_limit()` - Check daily quota
- `upload_to_youtube()` - Upload to YouTube
- `upload_video()` - Upload to all platforms
- `generate_metadata()` - Create upload metadata
- `save_upload_log()` - Log upload results

## Agent Coordination

The agents work together in a pipeline:

```
Trending Topics Agent
        ↓
    [Topics List]
        ↓
Video Generation Agent
        ↓
   [Generated Videos]
        ↓
Video Upload Agent
        ↓
  [Published Videos]
```

## Complete Workflow Example

```python
import asyncio
from agents.trending_topics_agent import TrendingTopicsAgent
from agents.video_generation_agent import VideoGenerationOrchestrator
from agents.video_upload_agent import VideoUploadAgent

async def complete_workflow(config):
    # Step 1: Research
    topics_agent = TrendingTopicsAgent(config)
    trends = await topics_agent.research()
    
    # Step 2: Generate
    generation_agent = VideoGenerationOrchestrator(config)
    results = []
    for topic in trends[:3]:  # Top 3 topics
        result = await generation_agent.generate_video(topic)
        results.append(result)
    
    # Step 3: Upload
    upload_agent = VideoUploadAgent(config)
    for result in results:
        if result['status'] == 'success':
            metadata = upload_agent.generate_metadata(
                result['topic'],
                result['script']
            )
            await upload_agent.upload_video(
                result['video_path'],
                metadata
            )

# Run workflow
config = {...}  # Your config
asyncio.run(complete_workflow(config))
```

## Extending Agents

### Adding New Research Sources

Edit `trending_topics_agent.py`:

```python
async def fetch_twitter_trends(self) -> List[Dict]:
    """Fetch from Twitter/X"""
    # Implementation
    pass
```

### Adding New Generation Methods

Edit `video_generation_agent.py`:

```python
async def generate_with_runway(self, prompt: str) -> str:
    """Generate using Runway ML"""
    # Implementation
    pass
```

### Adding New Upload Platforms

Edit `video_upload_agent.py`:

```python
async def upload_to_tiktok(self, video_path: str, metadata: Dict) -> Dict:
    """Upload to TikTok"""
    # Implementation
    pass
```

## Best Practices

1. **Error Handling**: All agents include error handling and logging
2. **Rate Limiting**: Respect API rate limits in all agents
3. **Async Operations**: Use async/await for all I/O operations
4. **Configuration**: Pass config through constructors
5. **Logging**: Use Python logging module for debugging
6. **Testing**: Test agents individually before integration

## Testing Agents

```bash
# Test trending topics agent
python agents/trending_topics_agent.py

# Test video generation agent
python agents/video_generation_agent.py

# Test upload agent
python agents/video_upload_agent.py
```

## Troubleshooting

### Agent Not Finding Topics
- Check API keys in config
- Verify network connectivity
- Check rate limits

### Video Generation Failing
- Ensure ComfyUI/Ollama is running
- Check API keys
- Verify output directory permissions

### Upload Failing
- Check YouTube OAuth credentials
- Verify video file exists
- Check upload quotas

## Performance Tips

1. Use async operations for parallel processing
2. Cache trending data to reduce API calls
3. Batch video generation when possible
4. Monitor API usage and costs
5. Use local models (Ollama) when possible

## Security Considerations

1. Never commit API keys
2. Use environment variables for secrets
3. Rotate credentials regularly
4. Implement rate limiting
5. Validate all user inputs
6. Review generated content before upload
