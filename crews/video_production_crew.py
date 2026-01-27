"""
Video Production Crew

This module implements a CrewAI-style crew for video production,
coordinating multiple agents to create complete videos from concept to upload.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.trending_topics_agent import TrendingTopicsAgent
from agents.deep_research_agent import DeepResearchAgent
from agents.video_generation_agent import VideoGenerationOrchestrator
from agents.video_editing_agent import VideoEditingAgent
from agents.multiplatform_upload_agent import MultiPlatformUploadAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoProductionCrew:
    """Crew that coordinates video production from research to upload"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Initialize all agents
        self.research_agent = TrendingTopicsAgent(config)
        self.deep_research_agent = DeepResearchAgent(config)
        self.generation_agent = VideoGenerationOrchestrator(config)
        self.editing_agent = VideoEditingAgent(config)
        self.upload_agent = MultiPlatformUploadAgent(config)
        
        logger.info("Video Production Crew initialized with 5 agents")
    
    async def execute_full_production(self, topic: Optional[str] = None) -> Dict:
        """Execute full video production workflow"""
        logger.info("=" * 60)
        logger.info("STARTING FULL VIDEO PRODUCTION WORKFLOW")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Phase 1: Topic Research
            if topic is None:
                logger.info("\n[Phase 1] Researching Trending Topics...")
                trends = await self.research_agent.research()
                
                if not trends:
                    return {'status': 'error', 'message': 'No trending topics found'}
                
                topic = trends[0].get('title', '')
                logger.info(f"Selected topic: {topic}")
            
            # Phase 2: Deep Research
            logger.info(f"\n[Phase 2] Performing Deep Research on: {topic}")
            research_data = await self.deep_research_agent.research_topic(topic)
            
            # Phase 3: Video Generation
            logger.info("\n[Phase 3] Generating Video...")
            topic_data = {
                'title': topic,
                'source': 'deep_research',
                'research': research_data
            }
            
            generation_result = await self.generation_agent.generate_video(topic_data)
            
            if generation_result['status'] != 'success':
                return generation_result
            
            video_path = generation_result['video_path']
            
            # Phase 4: Video Editing
            logger.info("\n[Phase 4] Editing Video...")
            edits = {
                'color_grade': 'vibrant',
                'trim': {'start': 0, 'duration': 60}
            }
            
            edited_video = self.editing_agent.edit_video(video_path, edits)
            
            # Create short-form versions
            short_video = self.editing_agent.create_short_form(edited_video, duration=60)
            
            # Phase 5: Multi-Platform Upload
            logger.info("\n[Phase 5] Uploading to Platforms...")
            
            metadata = {
                'title': topic[:100],
                'description': research_data.get('summary', '')[:500],
                'tags': ['AI', 'Video', 'Automated']
            }
            
            upload_results = await self.upload_agent.upload_to_all_platforms(
                short_video,
                metadata
            )
            
            # Compile results
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                'status': 'success',
                'topic': topic,
                'research': research_data,
                'video_path': edited_video,
                'short_form_path': short_video,
                'uploads': upload_results,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("\n" + "=" * 60)
            logger.info(f"PRODUCTION COMPLETE! Duration: {duration:.2f}s")
            logger.info("=" * 60)
            
            return result
            
        except Exception as e:
            logger.error(f"Production workflow error: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def execute_research_only(self, topic: str) -> Dict:
        """Execute only research phase"""
        logger.info(f"Executing research on: {topic}")
        
        research_data = await self.deep_research_agent.research_topic(topic)
        
        return {
            'status': 'success',
            'topic': topic,
            'research': research_data,
            'timestamp': datetime.now().isoformat()
        }
    
    async def execute_batch_production(self, num_videos: int = 3) -> List[Dict]:
        """Execute batch video production"""
        logger.info(f"Starting batch production of {num_videos} videos")
        
        # Get trending topics
        trends = await self.research_agent.research()
        
        results = []
        
        for i, trend in enumerate(trends[:num_videos], 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"BATCH VIDEO {i}/{num_videos}")
            logger.info(f"{'='*60}")
            
            topic = trend.get('title', '')
            result = await self.execute_full_production(topic)
            results.append(result)
            
            # Delay between videos
            if i < num_videos:
                logger.info("Waiting before next video...")
                await asyncio.sleep(5)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"BATCH COMPLETE: {num_videos} videos produced")
        logger.info(f"{'='*60}")
        
        return results


class ShortFormCrew:
    """Specialized crew for short-form content (TikTok, Reels, Shorts)"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.research_agent = TrendingTopicsAgent(config)
        self.generation_agent = VideoGenerationOrchestrator(config)
        self.editing_agent = VideoEditingAgent(config)
        self.upload_agent = MultiPlatformUploadAgent(config)
        
        logger.info("Short-Form Crew initialized")
    
    async def create_short_form(self, topic: str, duration: int = 30) -> Dict:
        """Create optimized short-form content"""
        logger.info(f"Creating short-form content: {topic} ({duration}s)")
        
        # Generate video
        topic_data = {'title': topic, 'source': 'manual'}
        generation_result = await self.generation_agent.generate_video(topic_data)
        
        if generation_result['status'] != 'success':
            return generation_result
        
        # Create short version
        short_video = self.editing_agent.create_short_form(
            generation_result['video_path'],
            duration=duration
        )
        
        # Upload to short-form platforms
        metadata = {
            'title': topic,
            'description': f'#{topic.replace(" ", "")}',
            'tags': ['Shorts', 'TikTok', 'Reels']
        }
        
        # Override config to only use short-form platforms
        original_platforms = self.upload_agent.enabled_platforms
        self.upload_agent.enabled_platforms = [
            'youtube_shorts', 'tiktok', 'instagram_reels', 'facebook_reels'
        ]
        
        upload_results = await self.upload_agent.upload_to_all_platforms(
            short_video,
            metadata
        )
        
        # Restore original platforms
        self.upload_agent.enabled_platforms = original_platforms
        
        return {
            'status': 'success',
            'topic': topic,
            'video_path': short_video,
            'uploads': upload_results,
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Example usage"""
    config = {
        'research': {
            'sources': ['reddit', 'youtube'],
            'topics_to_track': 5,
            'depth': 'comprehensive'
        },
        'video_generation': {
            'output_directory': 'output/videos'
        },
        'upload': {
            'platforms': ['youtube_shorts', 'tiktok'],
            'max_videos_per_day': 10
        },
        'ollama': {
            'host': 'http://localhost:11434'
        }
    }
    
    print("\n" + "=" * 60)
    print("VIDEO PRODUCTION CREW - DEMO")
    print("=" * 60)
    
    # Create crew
    crew = VideoProductionCrew(config)
    
    # Execute production (without actual video generation)
    # In production, this would create real videos
    print("\nCrew initialized with 5 specialized agents:")
    print("  1. Trending Topics Agent")
    print("  2. Deep Research Agent")
    print("  3. Video Generation Agent")
    print("  4. Video Editing Agent")
    print("  5. Multi-Platform Upload Agent")
    
    print("\nReady to execute workflows:")
    print("  - execute_full_production()")
    print("  - execute_research_only(topic)")
    print("  - execute_batch_production(num_videos)")


if __name__ == '__main__':
    asyncio.run(main())
