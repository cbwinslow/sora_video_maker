"""
Multi-Platform Upload Agent

This agent handles uploading videos to multiple platforms:
- YouTube (long-form and Shorts)
- TikTok
- Facebook/Instagram Reels
- Twitter/X
"""

import os
import json
import logging
from typing import Dict, List
from datetime import datetime
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiPlatformUploadAgent:
    """Agent for uploading videos to multiple platforms"""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled_platforms = config.get('upload', {}).get('platforms', [])
        self.max_uploads_per_day = config.get('upload', {}).get('max_videos_per_day', 5)
        self.upload_count = {'daily': 0, 'by_platform': {}}

    async def upload_to_all_platforms(self, video_path: str, metadata: Dict) -> List[Dict]:
        """Upload video to all enabled platforms"""
        logger.info(f"Uploading {video_path} to {len(self.enabled_platforms)} platforms")

        results = []

        for platform in self.enabled_platforms:
            if platform == 'youtube':
                result = await self.upload_to_youtube(video_path, metadata)
                results.append(result)
            elif platform == 'youtube_shorts':
                result = await self.upload_to_youtube_shorts(video_path, metadata)
                results.append(result)
            elif platform == 'tiktok':
                result = await self.upload_to_tiktok(video_path, metadata)
                results.append(result)
            elif platform == 'facebook_reels':
                result = await self.upload_to_facebook_reels(video_path, metadata)
                results.append(result)
            elif platform == 'instagram_reels':
                result = await self.upload_to_instagram_reels(video_path, metadata)
                results.append(result)
            elif platform == 'twitter':
                result = await self.upload_to_twitter(video_path, metadata)
                results.append(result)

        self.save_upload_log(results)
        return results

    async def upload_to_youtube(self, video_path: str, metadata: Dict) -> Dict:
        """Upload to YouTube (long-form)"""
        logger.info("Uploading to YouTube (long-form)")

        # In production, use YouTube Data API v3
        # Requires OAuth2 authentication

        return {
            'platform': 'youtube',
            'status': 'success',
            'video_id': f'yt_{int(datetime.now().timestamp())}',
            'url': 'https://youtube.com/watch?v=EXAMPLE',
            'format': 'long-form',
            'timestamp': datetime.now().isoformat()
        }

    async def upload_to_youtube_shorts(self, video_path: str, metadata: Dict) -> Dict:
        """Upload to YouTube Shorts"""
        logger.info("Uploading to YouTube Shorts")

        # Shorts requirements:
        # - Vertical (9:16)
        # - Under 60 seconds
        # - #Shorts in title or description

        metadata_copy = metadata.copy()
        if '#Shorts' not in metadata_copy.get('title', ''):
            metadata_copy['title'] = f"{metadata_copy.get('title', '')} #Shorts"

        return {
            'platform': 'youtube_shorts',
            'status': 'success',
            'video_id': f'yt_short_{int(datetime.now().timestamp())}',
            'url': 'https://youtube.com/shorts/EXAMPLE',
            'format': 'short-form',
            'timestamp': datetime.now().isoformat()
        }

    async def upload_to_tiktok(self, video_path: str, metadata: Dict) -> Dict:
        """Upload to TikTok"""
        logger.info("Uploading to TikTok")

        # TikTok requirements:
        # - Vertical (9:16) preferred
        # - 15s to 10 minutes
        # - Use trending sounds/hashtags

        # In production, use TikTok API
        # Requires TikTok for Developers account

        return {
            'platform': 'tiktok',
            'status': 'success',
            'video_id': f'tt_{int(datetime.now().timestamp())}',
            'url': 'https://tiktok.com/@user/video/EXAMPLE',
            'format': 'short-form',
            'timestamp': datetime.now().isoformat()
        }

    async def upload_to_facebook_reels(self, video_path: str, metadata: Dict) -> Dict:
        """Upload to Facebook Reels"""
        logger.info("Uploading to Facebook Reels")

        # Facebook Reels requirements:
        # - Vertical (9:16)
        # - Under 90 seconds

        # In production, use Facebook Graph API

        return {
            'platform': 'facebook_reels',
            'status': 'success',
            'video_id': f'fb_reel_{int(datetime.now().timestamp())}',
            'url': 'https://facebook.com/reel/EXAMPLE',
            'format': 'short-form',
            'timestamp': datetime.now().isoformat()
        }

    async def upload_to_instagram_reels(self, video_path: str, metadata: Dict) -> Dict:
        """Upload to Instagram Reels"""
        logger.info("Uploading to Instagram Reels")

        # Instagram Reels requirements:
        # - Vertical (9:16)
        # - 15 to 90 seconds
        # - Engaging thumbnail

        # In production, use Instagram Graph API

        return {
            'platform': 'instagram_reels',
            'status': 'success',
            'video_id': f'ig_reel_{int(datetime.now().timestamp())}',
            'url': 'https://instagram.com/reel/EXAMPLE',
            'format': 'short-form',
            'timestamp': datetime.now().isoformat()
        }

    async def upload_to_twitter(self, video_path: str, metadata: Dict) -> Dict:
        """Upload to Twitter/X"""
        logger.info("Uploading to Twitter/X")

        # Twitter requirements:
        # - Up to 2:20 (140 seconds) for most accounts
        # - Up to 10 minutes for Twitter Blue
        # - Various aspect ratios supported

        # In production, use Twitter API v2

        return {
            'platform': 'twitter',
            'status': 'success',
            'video_id': f'tw_{int(datetime.now().timestamp())}',
            'url': 'https://twitter.com/user/status/EXAMPLE',
            'format': 'short-form',
            'timestamp': datetime.now().isoformat()
        }

    def optimize_for_platform(self, video_path: str, platform: str) -> str:
        """Optimize video for specific platform"""
        logger.info(f"Optimizing video for {platform}")

        # Platform-specific optimizations
        optimizations = {
            'youtube': {
                'aspect_ratio': '16:9',
                'resolution': '1920x1080',
                'max_duration': None
            },
            'youtube_shorts': {
                'aspect_ratio': '9:16',
                'resolution': '1080x1920',
                'max_duration': 60
            },
            'tiktok': {
                'aspect_ratio': '9:16',
                'resolution': '1080x1920',
                'max_duration': 600
            },
            'facebook_reels': {
                'aspect_ratio': '9:16',
                'resolution': '1080x1920',
                'max_duration': 90
            },
            'instagram_reels': {
                'aspect_ratio': '9:16',
                'resolution': '1080x1920',
                'max_duration': 90
            },
            'twitter': {
                'aspect_ratio': '16:9',
                'resolution': '1280x720',
                'max_duration': 140
            }
        }

        # In production, would actually resize/optimize the video
        return video_path

    def generate_platform_specific_metadata(self, base_metadata: Dict, platform: str) -> Dict:
        """Generate platform-specific metadata"""
        metadata = base_metadata.copy()

        # Add platform-specific hashtags
        hashtags = {
            'youtube': ['#YouTube', '#Video'],
            'youtube_shorts': ['#Shorts', '#YouTubeShorts'],
            'tiktok': ['#FYP', '#ForYou', '#TikTok'],
            'facebook_reels': ['#Reels', '#FacebookReels'],
            'instagram_reels': ['#Reels', '#InstagramReels', '#IG'],
            'twitter': ['#Twitter', '#Video']
        }

        if platform in hashtags:
            description = metadata.get('description', '')
            description += '\n\n' + ' '.join(hashtags[platform])
            metadata['description'] = description

        # Adjust title length for platform
        title_limits = {
            'twitter': 280,  # Including description
            'tiktok': 150,
            'instagram_reels': 2200,
            'youtube': 100
        }

        if platform in title_limits:
            max_len = title_limits[platform]
            if len(metadata.get('title', '')) > max_len:
                metadata['title'] = metadata['title'][:max_len-3] + '...'

        return metadata

    def save_upload_log(self, results: List[Dict], filename: str = 'logs/multi_platform_upload.json'):
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

    def get_upload_stats(self) -> Dict:
        """Get upload statistics"""
        return {
            'total_uploads_today': self.upload_count['daily'],
            'uploads_by_platform': self.upload_count['by_platform'],
            'remaining_quota': self.max_uploads_per_day - self.upload_count['daily']
        }


async def main():
    """Example usage"""
    config = {
        'upload': {
            'platforms': ['youtube', 'youtube_shorts', 'tiktok', 'instagram_reels', 'twitter'],
            'max_videos_per_day': 10
        }
    }

    agent = MultiPlatformUploadAgent(config)

    # Example metadata
    metadata = {
        'title': 'Amazing AI Generated Video',
        'description': 'Check out this AI-generated video!',
        'tags': ['AI', 'Video', 'Technology']
    }

    # Simulate upload (would use actual video path)
    video_path = 'output/videos/example.mp4'
    results = await agent.upload_to_all_platforms(video_path, metadata)

    print("\n=== Upload Results ===")
    for result in results:
        print(f"{result['platform']}: {result['status']}")

    print("\n=== Upload Stats ===")
    stats = agent.get_upload_stats()
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
