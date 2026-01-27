"""
Video Upload Agent

This agent handles uploading generated videos to various platforms
like YouTube, with scheduling and metadata management.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoUploadAgent:
    """Agent for uploading videos to various platforms"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('upload', {}).get('enabled', False)
        self.platforms = config.get('upload', {}).get('platforms', [])
        self.max_videos_per_day = config.get('upload', {}).get('max_videos_per_day', 5)
        self.upload_count = 0
        
    def check_upload_limit(self) -> bool:
        """Check if upload limit has been reached"""
        if self.upload_count >= self.max_videos_per_day:
            logger.warning(f"Daily upload limit reached ({self.max_videos_per_day})")
            return False
        return True
    
    async def upload_to_youtube(self, video_path: str, metadata: Dict) -> Dict:
        """Upload video to YouTube"""
        if not self.enabled:
            logger.warning("Upload is disabled in configuration")
            return {'status': 'disabled'}
        
        if not self.check_upload_limit():
            return {'status': 'limit_reached'}
        
        logger.info(f"Uploading to YouTube: {video_path}")
        
        try:
            # In production, this would use the YouTube Data API
            # Requires OAuth2 authentication and google-api-python-client
            
            # Placeholder implementation
            youtube_metadata = {
                'title': metadata.get('title', 'Untitled Video'),
                'description': metadata.get('description', ''),
                'tags': metadata.get('tags', []),
                'category': '22',  # People & Blogs
                'privacyStatus': metadata.get('privacy', 'private')
            }
            
            # Simulated upload
            video_id = f"simulated_{int(time.time())}"
            
            self.upload_count += 1
            
            result = {
                'status': 'success',
                'platform': 'youtube',
                'video_id': video_id,
                'url': f"https://youtube.com/watch?v={video_id}",
                'metadata': youtube_metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Upload successful! Video ID: {video_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error uploading to YouTube: {e}")
            return {
                'status': 'error',
                'platform': 'youtube',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def upload_video(self, video_path: str, metadata: Dict) -> List[Dict]:
        """Upload video to all configured platforms"""
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return []
        
        results = []
        
        for platform in self.platforms:
            if platform == 'youtube':
                result = await self.upload_to_youtube(video_path, metadata)
                results.append(result)
            # Add more platforms here (TikTok, Instagram, etc.)
        
        return results
    
    def generate_metadata(self, topic: Dict, script: str = "") -> Dict:
        """Generate upload metadata from topic and script"""
        title = topic.get('title', 'Untitled Video')
        
        # Truncate title if too long (YouTube limit is 100 chars)
        if len(title) > 100:
            title = title[:97] + "..."
        
        description = f"""
{script[:500] if script else 'Auto-generated video content'}

Generated using AI Video Toolkit
Trending Topic: {topic.get('source', 'N/A')}

#AI #VideoGeneration #Trending
        """.strip()
        
        tags = [
            'AI',
            'Video Generation',
            'Automated',
            topic.get('source', '').title()
        ]
        
        return {
            'title': title,
            'description': description,
            'tags': tags,
            'privacy': 'private'  # Start with private, manually publish after review
        }
    
    def save_upload_log(self, results: List[Dict], filename: str = 'logs/upload_log.json'):
        """Save upload results to log file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            # Load existing log
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    log = json.load(f)
            else:
                log = []
            
            # Append new results
            log.extend(results)
            
            # Save updated log
            with open(filename, 'w') as f:
                json.dump(log, f, indent=2)
            
            logger.info(f"Upload log saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving upload log: {e}")


async def main():
    """Example usage"""
    config = {
        'upload': {
            'enabled': True,
            'platforms': ['youtube'],
            'max_videos_per_day': 5
        }
    }
    
    # Example topic and video
    topic = {
        'title': 'Amazing AI Technology Demo',
        'source': 'reddit'
    }
    
    script = "This is an example script for the video content."
    
    agent = VideoUploadAgent(config)
    
    # Generate metadata
    metadata = agent.generate_metadata(topic, script)
    print("\n=== Generated Metadata ===")
    print(json.dumps(metadata, indent=2))
    
    # Simulate upload (would use actual video path in production)
    video_path = "output/videos/example_video.mp4"
    results = await agent.upload_video(video_path, metadata)
    
    print("\n=== Upload Results ===")
    print(json.dumps(results, indent=2))
    
    # Save log
    agent.save_upload_log(results)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
