# Video Generation Toolkit - Complete Task List & Knowledge Base

## Table of Contents
1. [Quick Start Tasks](#quick-start-tasks)
2. [Production Workflow](#production-workflow)
3. [Agent Details](#agent-details)
4. [Platform-Specific Guidelines](#platform-specific-guidelines)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

---

## Quick Start Tasks

### Initial Setup (One-Time)
- [ ] Clone repository
- [ ] Run `bash install/install_all.sh`
- [ ] Copy `config/config.template.yaml` to `config/config.yaml`
- [ ] Add API keys to config.yaml:
  - [ ] OpenAI API key (for Sora when available)
  - [ ] OpenRouter API key (for free models)
  - [ ] YouTube API credentials
  - [ ] TikTok API key
  - [ ] Facebook/Instagram credentials
- [ ] Start Ollama: `ollama serve`
- [ ] Pull models: `ollama pull llama2`
- [ ] Test connections: `python examples/test_connections.py`

### First Video Creation
- [ ] Research trending topics: `python main.py --research-only`
- [ ] Review trending topics in `output/trends/`
- [ ] Generate test video: `python examples/basic_workflow.py`
- [ ] Review output in `output/videos/`

### Production Deployment
- [ ] Set up GitHub Actions secrets
- [ ] Enable workflows in `.github/workflows/`
- [ ] Configure upload platforms
- [ ] Test automated workflow
- [ ] Monitor logs and outputs

---

## Production Workflow

### Complete Video Production Pipeline

```
┌─────────────────┐
│  1. Research    │  Trending Topics Agent
│     Topics      │  → Discovers viral content
└────────┬────────┘
         │
         v
┌─────────────────┐
│  2. Deep        │  Deep Research Agent
│     Research    │  → Analyzes topic deeply
└────────┬────────┘
         │
         v
┌─────────────────┐
│  3. Generate    │  Video Generation Agent
│     Script      │  → Creates video script
└────────┬────────┘
         │
         v
┌─────────────────┐
│  4. Create      │  Video Generation Agent
│     Video       │  → Renders video (Sora/ComfyUI)
└────────┬────────┘
         │
         v
┌─────────────────┐
│  5. Edit        │  Video Editing Agent
│     Video       │  → Adds effects, music, etc.
└────────┬────────┘
         │
         v
┌─────────────────┐
│  6. Optimize    │  Multi-Platform Agent
│     Formats     │  → Creates platform versions
└────────┬────────┘
         │
         v
┌─────────────────┐
│  7. Upload      │  Multi-Platform Agent
│     Content     │  → Publishes to platforms
└─────────────────┘
```

### Task Checklist for Each Video

#### Pre-Production
- [ ] Research trending topics
- [ ] Perform deep research on selected topic
- [ ] Identify target audience
- [ ] Determine video angle (educational, trending, tutorial)
- [ ] Create script outline

#### Production
- [ ] Generate video script using LLM
- [ ] Create visual prompts from script
- [ ] Generate video using AI platform:
  - [ ] Sora (if available)
  - [ ] ComfyUI + AnimateDiff
  - [ ] Other platforms
- [ ] Review generated content
- [ ] Regenerate if needed

#### Post-Production
- [ ] Trim video to optimal length
- [ ] Add color grading (vibrant/cinematic/etc.)
- [ ] Add background music
- [ ] Generate and add subtitles
- [ ] Add intro/outro (if configured)
- [ ] Create platform-specific versions:
  - [ ] YouTube (16:9, any length)
  - [ ] YouTube Shorts (9:16, <60s)
  - [ ] TikTok (9:16, <10min)
  - [ ] Instagram Reels (9:16, <90s)
  - [ ] Facebook Reels (9:16, <90s)
  - [ ] Twitter (16:9 or square, <2:20)

#### Distribution
- [ ] Generate platform-specific metadata
- [ ] Optimize hashtags for each platform
- [ ] Schedule uploads
- [ ] Publish to platforms
- [ ] Monitor upload status
- [ ] Log results

#### Post-Upload
- [ ] Monitor engagement metrics
- [ ] Respond to comments (if enabled)
- [ ] Analyze performance
- [ ] Update content strategy

---

## Agent Details

### 1. Trending Topics Agent
**Purpose**: Discover viral content opportunities

**Tasks**:
- Fetch trending posts from Reddit
- Get YouTube trending videos
- Query Google Trends
- Score topics for video potential
- Export results to JSON

**Usage**:
```python
from agents.trending_topics_agent import TrendingTopicsAgent

agent = TrendingTopicsAgent(config)
trends = await agent.research()
```

**Key Methods**:
- `fetch_reddit_trends()` - Get Reddit hot posts
- `fetch_youtube_trends()` - Get YouTube trending
- `fetch_google_trends()` - Get search trends
- `analyze_trends()` - Score and rank
- `research()` - Main method
- `save_trends()` - Export to file

---

### 2. Deep Research Agent
**Purpose**: Perform comprehensive topic research

**Tasks**:
- Gather background information
- Extract key points
- Find credible sources
- Analyze video angles
- Determine target audience
- Find related topics

**Usage**:
```python
from agents.deep_research_agent import DeepResearchAgent

agent = DeepResearchAgent(config)
research = await agent.research_topic("AI Video Generation")
```

**Research Output**:
- Summary (200-300 words)
- 5-7 key points
- Credible sources list
- 3+ video angle suggestions
- Target audience description
- 5 related topics

---

### 3. Video Generation Agent
**Purpose**: Orchestrate video creation

**Tasks**:
- Generate scripts from topics
- Create visual prompts
- Interface with generation platforms
- Assemble final video
- Track metadata

**Usage**:
```python
from agents.video_generation_agent import VideoGenerationOrchestrator

agent = VideoGenerationOrchestrator(config)
result = await agent.generate_video(topic_data)
```

**Platforms Supported**:
- Sora API (OpenAI)
- ComfyUI (local)
- OpenRouter (free models)
- Ollama (local LLM)

---

### 4. Video Editing Agent
**Purpose**: Automated video editing

**Tasks**:
- Trim/cut videos
- Add color grading
- Add background music
- Generate subtitles
- Add intro/outro
- Create short-form versions

**Usage**:
```python
from agents.video_editing_agent import VideoEditingAgent

agent = VideoEditingAgent(config)
edited = agent.edit_video(video_path, edits)
short = agent.create_short_form(video_path, duration=60)
```

**Available Edits**:
- `trim` - Cut to specific duration
- `add_intro` - Prepend intro video
- `add_outro` - Append outro video
- `add_music` - Mix in background music
- `add_subtitles` - Burn in subtitles
- `color_grade` - Apply color preset
- `add_transitions` - Add transitions

---

### 5. Multi-Platform Upload Agent
**Purpose**: Upload to all social platforms

**Tasks**:
- Optimize videos for each platform
- Generate platform-specific metadata
- Handle OAuth authentication
- Rate limit uploads
- Log all uploads

**Usage**:
```python
from agents.multiplatform_upload_agent import MultiPlatformUploadAgent

agent = MultiPlatformUploadAgent(config)
results = await agent.upload_to_all_platforms(video_path, metadata)
```

**Supported Platforms**:
- YouTube (long-form)
- YouTube Shorts
- TikTok
- Instagram Reels
- Facebook Reels
- Twitter/X

---

## Platform-Specific Guidelines

### YouTube (Long-Form)
**Specs**:
- Aspect Ratio: 16:9
- Resolution: 1920x1080 (minimum 720p)
- Duration: No limit
- File Size: 256GB max
- Format: MP4, MOV, AVI, etc.

**Optimization**:
- Create compelling thumbnail
- Use keyword-rich title (max 100 chars)
- Detailed description with timestamps
- Add relevant tags (max 500 chars)
- Choose appropriate category
- Add end screens

**Metadata Tips**:
- First 2-3 lines of description most important
- Include links to social media
- Add #hashtags (max 15)
- Mention key topics in first 48 hours

---

### YouTube Shorts
**Specs**:
- Aspect Ratio: 9:16 (vertical)
- Resolution: 1080x1920
- Duration: Under 60 seconds
- Must include #Shorts in title or description

**Optimization**:
- Hook viewers in first 3 seconds
- Use trending audio when possible
- Add captions/subtitles
- High energy, fast paced
- Clear call-to-action
- Loop-worthy ending

**Best Practices**:
- Post daily for algorithm boost
- Use relevant hashtags
- Engage with comments quickly
- Cross-promote with long-form

---

### TikTok
**Specs**:
- Aspect Ratio: 9:16 (vertical)
- Resolution: 1080x1920
- Duration: 15s to 10 minutes
- File Size: 287.6MB max

**Optimization**:
- Use trending sounds
- Add text overlays
- Use popular hashtags
- Participate in challenges
- Duet/Stitch potential
- Strong hook in first second

**Algorithm Tips**:
- Post 1-3 times per day
- Best times: 6-10am, 7-11pm
- Engagement in first hour crucial
- Watch time percentage important
- Completion rate matters most

**Hashtag Strategy**:
- 3-5 hashtags max
- Mix of trending and niche
- Include #FYP or #ForYou
- Use location tags

---

### Instagram Reels
**Specs**:
- Aspect Ratio: 9:16 (vertical)
- Resolution: 1080x1920
- Duration: 15 to 90 seconds
- File Size: 4GB max

**Optimization**:
- Use Instagram music library
- Add stickers/effects
- Use trending audio
- Clear captions
- Engaging thumbnail
- Strong hook

**Best Practices**:
- Post during peak hours
- Share to Stories
- Share to Feed
- Use 3-5 hashtags
- Geotag your location
- Tag relevant accounts

---

### Facebook Reels
**Specs**:
- Aspect Ratio: 9:16 (vertical)
- Resolution: 1080x1920
- Duration: Under 90 seconds
- File Size: 4GB max

**Optimization**:
- Native uploads perform best
- Use Facebook sounds
- Add captions
- Engaging first frame
- Cross-post to Instagram
- Share to Stories

---

### Twitter/X
**Specs**:
- Aspect Ratio: 16:9, 1:1, or 9:16
- Resolution: 1920x1080 recommended
- Duration: 2:20 (regular), 10 min (Blue)
- File Size: 512MB max

**Optimization**:
- Grab attention quickly
- Add captions
- Use relevant hashtags (2-3 max)
- Thread for longer content
- Pin important videos
- Engage with replies

---

## Troubleshooting

### Common Issues

#### Ollama Not Responding
**Symptoms**: "Connection refused" errors
**Solutions**:
1. Check if Ollama is running: `ps aux | grep ollama`
2. Start Ollama: `ollama serve`
3. Check port 11434: `lsof -i :11434`
4. Pull models: `ollama pull llama2`

#### ComfyUI Connection Failed
**Symptoms**: Cannot connect to ComfyUI API
**Solutions**:
1. Start ComfyUI: `cd ComfyUI && python main.py`
2. Check URL: http://127.0.0.1:8188
3. Check port conflicts: `lsof -i :8188`
4. Review ComfyUI logs

#### FFmpeg Errors
**Symptoms**: Video processing fails
**Solutions**:
1. Install FFmpeg: `sudo apt-get install ffmpeg`
2. Check version: `ffmpeg -version`
3. Verify video file exists
4. Check file permissions
5. Review FFmpeg error messages

#### Upload Failures
**Symptoms**: Videos fail to upload
**Solutions**:
1. Check API keys in config
2. Verify OAuth tokens
3. Check rate limits
4. Verify video format
5. Check file size limits
6. Review platform requirements

#### Out of Memory
**Symptoms**: Process killed, memory errors
**Solutions**:
1. Reduce video resolution
2. Process in batches
3. Increase swap space
4. Use lower quality models
5. Close other applications

---

## Best Practices

### Content Strategy
1. **Research First**: Always research before creating
2. **Quality Over Quantity**: Better to post 1 great video than 10 poor ones
3. **Consistency**: Post on a regular schedule
4. **Trend Awareness**: Stay current with platform trends
5. **Audience Focus**: Know your target audience
6. **Analytics**: Track performance and adjust
7. **Engagement**: Respond to comments
8. **Cross-Promotion**: Share across platforms

### Technical Best Practices
1. **Test Locally**: Test workflows before automation
2. **Version Control**: Use git for all changes
3. **Backup**: Keep backups of successful content
4. **Monitoring**: Set up alerts for failures
5. **Logging**: Keep detailed logs
6. **Error Handling**: Gracefully handle errors
7. **Rate Limiting**: Respect API limits
8. **Security**: Never commit API keys

### Workflow Optimization
1. **Batch Processing**: Create multiple videos in batches
2. **Template Usage**: Use proven templates
3. **Asset Library**: Maintain library of intros, music, etc.
4. **Automation**: Automate repetitive tasks
5. **Review Process**: QA before publishing
6. **Scheduling**: Use optimal posting times
7. **A/B Testing**: Test different approaches
8. **Iteration**: Continuously improve

### Platform-Specific Tips

#### YouTube
- Create playlists for organization
- Use end screens effectively
- Add cards for engagement
- Create series for returning viewers
- Optimize for search
- Use community tab

#### Shorts/TikTok/Reels
- Post at peak times
- Use trending audio
- Add text overlays
- Hook in first 3 seconds
- Use popular hashtags
- Engage quickly with comments

#### Multi-Platform
- Adapt content for each platform
- Don't just repost
- Use platform-specific features
- Optimize metadata separately
- Track performance per platform
- Adjust strategy accordingly

---

## Additional Resources

### Required API Documentation
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [TikTok API](https://developers.tiktok.com/)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [Twitter API](https://developer.twitter.com/en/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [OpenRouter API](https://openrouter.ai/docs)

### Useful Tools
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [Ollama](https://ollama.com/)
- [FFmpeg](https://ffmpeg.org/)
- [Stable Diffusion](https://stability.ai/)
- [AnimateDiff](https://github.com/guoyww/AnimateDiff)

### Learning Resources
- YouTube Creator Academy
- TikTok Creator Portal
- Instagram for Creators
- Social Media Examiner
- Video Marketing guides

---

## Version History
- v1.0 - Initial release
- v1.1 - Added multi-platform support
- v1.2 - Added deep research agent
- v1.3 - Added video editing agent
- v2.0 - Added crews and GitHub workflows

---

**Last Updated**: 2024-01-27
**Maintained By**: Video Generation Toolkit Team
