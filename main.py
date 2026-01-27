"""
Main Workflow Orchestrator

This is the main entry point for the automated video generation workflow.
It coordinates all agents and services to create videos from trending topics.
"""

import os
import sys
import yaml
import asyncio
import logging
from datetime import datetime
from typing import Dict, List
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.trending_topics_agent import TrendingTopicsAgent
from agents.video_generation_agent import VideoGenerationOrchestrator
from agents.video_upload_agent import VideoUploadAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Main orchestrator for the video generation workflow"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        self.config = self.load_config(config_path)
        
        # Initialize agents
        self.topics_agent = TrendingTopicsAgent(self.config)
        self.generation_agent = VideoGenerationOrchestrator(self.config)
        self.upload_agent = VideoUploadAgent(self.config)
        
        # Create necessary directories
        self.setup_directories()
    
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}")
            logger.info("Using default configuration")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'research': {
                'sources': ['reddit', 'youtube', 'google_trends'],
                'topics_to_track': 10
            },
            'video_generation': {
                'output_directory': 'output/videos',
                'default_resolution': '1920x1080',
                'default_fps': 30
            },
            'upload': {
                'enabled': False,
                'platforms': ['youtube'],
                'max_videos_per_day': 5
            },
            'workflow': {
                'auto_generate': False,
                'auto_upload': False
            }
        }
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            'output/videos',
            'output/trends',
            'logs',
            'temp'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    async def run_research_phase(self) -> List[Dict]:
        """Research trending topics"""
        logger.info("=" * 50)
        logger.info("PHASE 1: Researching Trending Topics")
        logger.info("=" * 50)
        
        trends = await self.topics_agent.research()
        
        # Save trends
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        trends_file = f'output/trends/trends_{timestamp}.json'
        self.topics_agent.save_trends(trends, trends_file)
        
        logger.info(f"Found {len(trends)} trending topics")
        return trends
    
    async def run_generation_phase(self, topics: List[Dict]) -> List[Dict]:
        """Generate videos from topics"""
        logger.info("=" * 50)
        logger.info("PHASE 2: Generating Videos")
        logger.info("=" * 50)
        
        results = []
        
        # Generate videos for top N topics
        max_videos = min(len(topics), 3)  # Limit to top 3 for demo
        
        for i, topic in enumerate(topics[:max_videos], 1):
            logger.info(f"\nGenerating video {i}/{max_videos}")
            logger.info(f"Topic: {topic.get('title', 'N/A')}")
            
            result = await self.generation_agent.generate_video(topic)
            results.append(result)
            
            # Save metadata
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            metadata_file = f'output/videos/metadata_{timestamp}_{i}.json'
            self.generation_agent.save_metadata(result, metadata_file)
        
        logger.info(f"\nGenerated {len(results)} videos")
        return results
    
    async def run_upload_phase(self, generation_results: List[Dict]) -> List[Dict]:
        """Upload generated videos"""
        logger.info("=" * 50)
        logger.info("PHASE 3: Uploading Videos")
        logger.info("=" * 50)
        
        all_upload_results = []
        
        for i, result in enumerate(generation_results, 1):
            if result['status'] != 'success':
                logger.warning(f"Skipping upload for failed generation {i}")
                continue
            
            logger.info(f"\nUploading video {i}/{len(generation_results)}")
            
            # Generate metadata
            metadata = self.upload_agent.generate_metadata(
                result['topic'],
                result.get('script', '')
            )
            
            # Upload
            upload_results = await self.upload_agent.upload_video(
                result['video_path'],
                metadata
            )
            
            all_upload_results.extend(upload_results)
        
        # Save upload log
        self.upload_agent.save_upload_log(all_upload_results)
        
        logger.info(f"\nUploaded {len(all_upload_results)} videos")
        return all_upload_results
    
    async def run_full_workflow(self):
        """Run the complete workflow"""
        start_time = datetime.now()
        
        logger.info("\n" + "=" * 50)
        logger.info("VIDEO GENERATION WORKFLOW STARTED")
        logger.info("=" * 50 + "\n")
        
        try:
            # Phase 1: Research
            trends = await self.run_research_phase()
            
            # Phase 2: Generate
            if self.config.get('workflow', {}).get('auto_generate', False) or len(sys.argv) > 1:
                generation_results = await self.run_generation_phase(trends)
                
                # Phase 3: Upload
                if self.config.get('workflow', {}).get('auto_upload', False):
                    upload_results = await self.run_upload_phase(generation_results)
            else:
                logger.info("\nAuto-generation is disabled. Enable it in config to continue.")
                logger.info("Or run with --generate flag")
        
        except Exception as e:
            logger.error(f"Workflow error: {e}", exc_info=True)
        
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            logger.info("\n" + "=" * 50)
            logger.info(f"WORKFLOW COMPLETE - Duration: {duration:.2f}s")
            logger.info("=" * 50 + "\n")
    
    async def run_research_only(self):
        """Run only the research phase"""
        logger.info("Running research phase only...")
        trends = await self.run_research_phase()
        
        print("\n=== Top Trending Topics ===")
        for i, trend in enumerate(trends, 1):
            print(f"{i}. [{trend['source']}] {trend.get('title', trend.get('query', 'N/A'))}")
            print(f"   Score: {trend.get('video_potential_score', 0):.2f}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Video Generation Toolkit Workflow')
    parser.add_argument('--config', default='config/config.yaml', help='Config file path')
    parser.add_argument('--research-only', action='store_true', help='Run research phase only')
    parser.add_argument('--generate', action='store_true', help='Enable video generation')
    
    args = parser.parse_args()
    
    orchestrator = WorkflowOrchestrator(args.config)
    
    if args.research_only:
        await orchestrator.run_research_only()
    else:
        # Override config if --generate flag is used
        if args.generate:
            orchestrator.config['workflow']['auto_generate'] = True
        
        await orchestrator.run_full_workflow()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nWorkflow interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
