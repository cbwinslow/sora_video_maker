# Tools and Utilities Guide

This guide covers all the utility tools and scripts available in the Sora Video Maker project.

## Table of Contents

- [SEO Optimizer](#seo-optimizer)
- [Content Moderator](#content-moderator)
- [Video Validator](#video-validator)
- [Thumbnail Generator](#thumbnail-generator)
- [Analytics Tracker](#analytics-tracker)
- [Batch Processor](#batch-processor)
- [Notification System](#notification-system)
- [Video Utilities](#video-utilities)

## SEO Optimizer

Optimize video metadata for search engines and platforms.

### Usage

```python
from scripts.seo_optimizer import SEOOptimizer

optimizer = SEOOptimizer()

# Optimize title
title = "AI Video Generation Tutorial"
keywords = ["OpenAI", "Automation"]
optimized_title = optimizer.optimize_title(title, keywords)

# Optimize description
description = "Learn how to generate videos using AI."
links = ["https://example.com/tutorial"]
optimized_desc = optimizer.optimize_description(description, keywords, links)

# Generate tags
tags = optimizer.generate_tags(optimized_title, optimized_desc)

# Generate thumbnail text
thumb_text = optimizer.generate_thumbnail_text(optimized_title)

# Analyze title quality
analysis = optimizer.analyze_title_quality(optimized_title)
print(f"Title Quality: {analysis['quality']} (Score: {analysis['score']}/60)")
```

### Features

- **Title Optimization**: Improves SEO with keywords, proper length
- **Description Enhancement**: Adds keywords, links, call-to-action
- **Tag Generation**: Extracts relevant tags automatically
- **Thumbnail Text**: Creates eye-catching thumbnail overlay text
- **Quality Analysis**: Scores and suggests improvements for titles
- **Posting Time Suggestions**: Recommends optimal upload times

## Content Moderator

Filter and moderate content before video generation.

### Usage

```python
from scripts.content_moderator import ContentModerator

moderator = ContentModerator({
    'strict_mode': False,
    'allow_controversial': False
})

# Moderate content
text = "Your video content text here"
result = moderator.moderate_content(text)

if result['is_approved']:
    print(f"Content approved (score: {result['moderation_score']}/100)")
else:
    print(f"Content rejected: {result['issues']}")

# Sanitize text
sanitized = moderator.sanitize_text(text)

# Generate report
report = moderator.generate_moderation_report(result)
print(report)
```

### Checks Performed

- **Profanity Detection**: Identifies inappropriate language
- **Banned Topics**: Blocks illegal or harmful content
- **Suspicious Patterns**: Detects potentially problematic patterns
- **Personal Information**: Identifies PII (emails, phones, SSNs)
- **Spam Indicators**: Detects spam-like content

### Severity Levels

- **Low**: Content passes with no issues
- **Medium**: Minor issues, warnings generated
- **High**: Significant issues, may be rejected
- **Critical**: Serious issues, always rejected

## Video Validator

Validate video files and check quality metrics.

### Usage

```python
from scripts.video_validator import VideoValidator

validator = VideoValidator({
    'min_duration': 1.0,
    'max_duration': 600.0,
    'min_resolution': (640, 480),
    'supported_codecs': ['h264', 'h265']
})

# Validate video
results = validator.validate_video('path/to/video.mp4', check_corruption=True)

if results['is_valid']:
    print(f"Valid video (quality: {results['quality_score']:.1f}/100)")
else:
    print(f"Invalid video: {results['errors']}")

# View detailed checks
for check_name, check_result in results['checks'].items():
    status = "✓" if check_result['valid'] else "✗"
    print(f"{status} {check_name}: {check_result['message']}")
```

### Validation Checks

- **File Existence**: Checks if file exists and is readable
- **Duration**: Validates video length
- **Resolution**: Checks video dimensions
- **Codec**: Verifies supported video codec
- **Audio**: Checks for audio stream presence
- **Corruption**: Detects file corruption
- **Quality Score**: Calculates overall quality (0-100)

## Thumbnail Generator

Generate professional thumbnails for videos.

### Usage

```python
from scripts.thumbnail_generator import ThumbnailGenerator

generator = ThumbnailGenerator()

# Simple text thumbnail
generator.create_text_thumbnail(
    text="AI Video Generation",
    output_path="thumbnail1.png",
    bg_color=(41, 128, 185),
    text_color=(255, 255, 255)
)

# Gradient thumbnail
generator.create_gradient_thumbnail(
    text="Amazing Tutorial",
    output_path="thumbnail2.png",
    color1=(52, 152, 219),
    color2=(155, 89, 182)
)

# Extract frame from video
generator.extract_frame_as_thumbnail(
    video_path="video.mp4",
    output_path="thumbnail3.png",
    timestamp=2.0,  # Extract at 2 seconds
    add_text="Watch Now!"
)

# Create collage
generator.create_collage_thumbnail(
    images=['img1.png', 'img2.png', 'img3.png'],
    output_path="collage.png",
    text="Best Moments"
)
```

### Thumbnail Styles

- **Text Thumbnail**: Simple background with text
- **Gradient**: Eye-catching gradient backgrounds
- **Frame Extract**: Use video frame as thumbnail
- **Collage**: Combine multiple images

## Analytics Tracker

Track and analyze workflow performance.

### Usage

```python
from scripts.analytics_tracker import AnalyticsTracker, PerformanceTimer

tracker = AnalyticsTracker({'storage_path': 'analytics/data'})

# Track events
tracker.track_event('video_generated', {'quality': 'HD', 'duration': 60})

# Track metrics
tracker.track_metric('processing_time', 45.2, {'unit': 'seconds'})

# Time operations
with PerformanceTimer(tracker, 'video_generation'):
    # Your code here
    pass

# Get statistics
stats = tracker.get_metric_stats('processing_time')
print(f"Average processing time: {stats['mean']:.2f}s")

# Generate report
print(tracker.generate_performance_report())

# Save session
tracker.save_session_data()

# Analyze trends
trends = tracker.analyze_trends('processing_time', num_sessions=10)
print(f"Trend: {trends['trend']}")
```

### Tracked Metrics

- **Duration**: Operation timing
- **Success Rate**: Success/failure tracking
- **Throughput**: Events per hour
- **Custom Metrics**: Any numeric values

## Batch Processor

Process multiple videos with queue management.

### Usage

```python
import asyncio
from scripts.batch_processor import BatchProcessor

processor = BatchProcessor({
    'max_concurrent': 3,
    'max_retries': 2,
    'save_state': True
})

# Define task handler
async def generate_video_handler(data):
    # Your video generation code
    return {'video_path': f"/output/video_{data['id']}.mp4"}

# Register handler
processor.register_handler('generate_video', generate_video_handler)

# Add tasks
for i in range(10):
    processor.add_task('generate_video', {
        'id': i,
        'title': f'Video {i}'
    }, priority=i)

# Process queue
await processor.process_queue()

# Check status
status = processor.get_queue_status()
print(f"Completed: {status['completed']}/{status['total']}")

# Export results
processor.export_results('batch_results.json')
```

### Features

- **Queue Management**: Priority-based task ordering
- **Concurrent Processing**: Process multiple tasks simultaneously
- **Retry Logic**: Automatic retry on failure
- **State Persistence**: Resume after interruption
- **Progress Tracking**: Monitor task status

## Notification System

Send notifications via multiple channels.

### Usage

```python
from scripts.notification_system import NotificationSystem, NotificationType

config = {
    'enabled_channels': ['console', 'email', 'slack'],
    'email': {
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your-email@gmail.com',
        'password': 'your-password',
        'from_address': 'your-email@gmail.com',
        'to_addresses': ['recipient@example.com']
    },
    'slack': {
        'webhook_url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    }
}

notifier = NotificationSystem(config)

# Send notification
notifier.send_notification(
    title="Video Generated",
    message="New video created successfully",
    notification_type=NotificationType.SUCCESS,
    data={'video_path': '/output/video.mp4'}
)

# Convenience methods
notifier.send_video_generated('/output/video.mp4', 'Tutorial', 60.5)
notifier.send_error('Upload', 'Connection failed')
notifier.send_workflow_complete({'videos_generated': 5})
```

### Supported Channels

- **Console**: Terminal output
- **Email**: SMTP email notifications
- **Slack**: Slack webhooks
- **Discord**: Discord webhooks
- **Webhook**: Custom HTTP webhooks
- **File**: Log to file

## Video Utilities

Common video processing functions.

### Usage

```python
from scripts.video_utils import *

# Get video info
info = get_video_info('video.mp4')
print(f"Duration: {info['format']['duration']}s")

# Resize video
resize_video('input.mp4', 'output.mp4', 1280, 720)

# Concatenate videos
concatenate_videos(['video1.mp4', 'video2.mp4'], 'combined.mp4')

# Add audio
add_audio_to_video('video.mp4', 'audio.mp3', 'output.mp4')

# Extract frames
extract_frames('video.mp4', 'frames/', fps=2)

# Create video from images
create_video_from_images('frames/', 'output.mp4', fps=30)

# Add text overlay
add_text_overlay('video.mp4', 'output.mp4', 'Welcome!', position='top')
```

### Available Functions

- `get_video_info()`: Get video metadata
- `resize_video()`: Change video resolution
- `concatenate_videos()`: Join multiple videos
- `add_audio_to_video()`: Add/replace audio track
- `extract_frames()`: Export video frames
- `create_video_from_images()`: Create video from images
- `add_text_overlay()`: Add text to video

## Integration Examples

### Complete Workflow Example

```python
import asyncio
from scripts.seo_optimizer import SEOOptimizer
from scripts.content_moderator import ContentModerator
from scripts.video_validator import VideoValidator
from scripts.thumbnail_generator import ThumbnailGenerator
from scripts.notification_system import NotificationSystem

async def process_video_workflow(topic, script, video_path):
    # 1. Moderate content
    moderator = ContentModerator()
    moderation = moderator.moderate_content(script)
    
    if not moderation['is_approved']:
        print(f"Content rejected: {moderation['issues']}")
        return
    
    # 2. Validate video
    validator = VideoValidator()
    validation = validator.validate_video(video_path)
    
    if not validation['is_valid']:
        print(f"Video invalid: {validation['errors']}")
        return
    
    # 3. Optimize metadata
    optimizer = SEOOptimizer()
    title = optimizer.optimize_title(topic)
    description = optimizer.optimize_description(script)
    tags = optimizer.generate_tags(title, description)
    
    # 4. Generate thumbnail
    generator = ThumbnailGenerator()
    thumb_text = optimizer.generate_thumbnail_text(title)
    generator.create_text_thumbnail(
        thumb_text,
        f"{video_path}.thumb.png"
    )
    
    # 5. Send notification
    notifier = NotificationSystem()
    notifier.send_video_generated(video_path, topic, validation['info']['format']['duration'])
    
    print("Workflow complete!")
    return {
        'video_path': video_path,
        'title': title,
        'description': description,
        'tags': tags,
        'thumbnail': f"{video_path}.thumb.png"
    }

# Run workflow
result = asyncio.run(process_video_workflow(
    "AI Tutorial",
    "Learn about AI...",
    "output/video.mp4"
))
```

## Best Practices

1. **Always validate inputs** before processing
2. **Use moderation** for user-generated content
3. **Track analytics** for performance insights
4. **Send notifications** for important events
5. **Batch process** when handling multiple items
6. **Cache results** to avoid redundant work
7. **Handle errors gracefully** with proper logging
8. **Test thoroughly** before production use

## Troubleshooting

### Common Issues

**Issue: FFmpeg not found**
```bash
# Install FFmpeg
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg           # macOS
```

**Issue: PIL/Pillow not available**
```bash
pip install Pillow
```

**Issue: Notifications not sending**
- Check configuration values
- Verify network connectivity
- Test with console channel first

**Issue: Video validation fails**
- Check file exists and is readable
- Verify video format is supported
- Try with corruption check disabled

## Additional Resources

- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [Testing Guide](TESTING.md)
- [API Documentation](API.md)
