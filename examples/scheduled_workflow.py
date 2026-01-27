"""
Advanced Workflow Example - Scheduled Video Generation

This example demonstrates scheduled automated video generation
with trending topics research and upload automation.
"""

import asyncio
import schedule
import time
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.trending_topics_agent import TrendingTopicsAgent
from agents.video_generation_agent import VideoGenerationOrchestrator
from agents.video_upload_agent import VideoUploadAgent


class ScheduledWorkflow:
    """Scheduled video generation workflow"""
    
    def __init__(self, config):
        self.config = config
        self.topics_agent = TrendingTopicsAgent(config)
        self.generation_agent = VideoGenerationOrchestrator(config)
        self.upload_agent = VideoUploadAgent(config)
        
        self.videos_generated_today = 0
        self.max_videos_per_day = config.get('upload', {}).get('max_videos_per_day', 5)
    
    async def run_workflow(self):
        """Run the complete workflow once"""
        print("\n" + "=" * 60)
        print(f"Running Workflow - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Check daily limit
        if self.videos_generated_today >= self.max_videos_per_day:
            print(f"Daily limit reached ({self.max_videos_per_day} videos)")
            return
        
        try:
            # Step 1: Research trending topics
            print("\n[1/3] Researching trending topics...")
            trends = await self.topics_agent.research()
            
            if not trends:
                print("No trends found. Skipping generation.")
                return
            
            print(f"Found {len(trends)} trending topics")
            
            # Step 2: Generate video from top topic
            print("\n[2/3] Generating video...")
            top_topic = trends[0]
            print(f"Topic: {top_topic.get('title', 'N/A')}")
            
            result = await self.generation_agent.generate_video(top_topic)
            
            if result['status'] != 'success':
                print(f"Generation failed: {result.get('error', 'Unknown error')}")
                return
            
            print(f"✓ Video generated: {result['video_path']}")
            self.videos_generated_today += 1
            
            # Step 3: Upload if enabled
            if self.config.get('upload', {}).get('enabled', False):
                print("\n[3/3] Uploading video...")
                
                metadata = self.upload_agent.generate_metadata(
                    top_topic,
                    result.get('script', '')
                )
                
                upload_results = await self.upload_agent.upload_video(
                    result['video_path'],
                    metadata
                )
                
                for upload_result in upload_results:
                    if upload_result['status'] == 'success':
                        print(f"✓ Uploaded to {upload_result['platform']}: {upload_result['url']}")
                    else:
                        print(f"✗ Upload to {upload_result['platform']} failed")
            else:
                print("\n[3/3] Upload disabled (skipping)")
            
            print("\n" + "=" * 60)
            print("Workflow Complete!")
            print(f"Videos generated today: {self.videos_generated_today}/{self.max_videos_per_day}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Workflow error: {e}")
    
    def reset_daily_counter(self):
        """Reset the daily video counter"""
        print(f"\nResetting daily counter (was: {self.videos_generated_today})")
        self.videos_generated_today = 0
    
    def schedule_workflows(self):
        """Schedule workflow execution"""
        # Run workflow every 6 hours
        schedule.every(6).hours.do(lambda: asyncio.run(self.run_workflow()))
        
        # Reset counter at midnight
        schedule.every().day.at("00:00").do(self.reset_daily_counter)
        
        print("\n" + "=" * 60)
        print("Scheduled Workflow Configuration")
        print("=" * 60)
        print("- Workflow runs: Every 6 hours")
        print("- Daily video limit:", self.max_videos_per_day)
        print("- Counter reset: Daily at midnight")
        print("=" * 60)
        print("\nScheduler started. Press Ctrl+C to stop.")
        print()
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        self.schedule_workflows()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\nScheduler stopped by user.")


async def run_once():
    """Run workflow once (for testing)"""
    config = {
        'research': {
            'sources': ['reddit', 'youtube'],
            'topics_to_track': 5
        },
        'video_generation': {
            'output_directory': 'output/videos'
        },
        'upload': {
            'enabled': False,
            'max_videos_per_day': 5
        }
    }
    
    workflow = ScheduledWorkflow(config)
    await workflow.run_workflow()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Scheduled Workflow')
    parser.add_argument('--once', action='store_true', help='Run workflow once (for testing)')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule')
    
    args = parser.parse_args()
    
    if args.once:
        print("Running workflow once (test mode)...")
        asyncio.run(run_once())
    elif args.schedule:
        # Load config
        import yaml
        try:
            with open('config/config.yaml', 'r') as f:
                config = yaml.safe_load(f)
        except:
            print("Error loading config. Using defaults.")
            config = {
                'research': {'sources': ['reddit'], 'topics_to_track': 5},
                'video_generation': {'output_directory': 'output/videos'},
                'upload': {'enabled': False, 'max_videos_per_day': 5}
            }
        
        workflow = ScheduledWorkflow(config)
        workflow.run_scheduler()
    else:
        print("Please specify --once or --schedule")
        parser.print_help()


if __name__ == '__main__':
    main()
