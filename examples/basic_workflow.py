"""
Basic Workflow Example

This example demonstrates the basic usage of the video generation toolkit.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.trending_topics_agent import TrendingTopicsAgent
from agents.video_generation_agent import VideoGenerationOrchestrator


async def main():
    """Run basic workflow example"""
    print("=" * 60)
    print("Video Generation Toolkit - Basic Example")
    print("=" * 60)
    print()
    
    # Configuration
    config = {
        'research': {
            'sources': ['reddit', 'youtube'],
            'topics_to_track': 5
        },
        'video_generation': {
            'output_directory': 'output/videos'
        }
    }
    
    # Step 1: Research trending topics
    print("Step 1: Researching trending topics...")
    print("-" * 60)
    
    topics_agent = TrendingTopicsAgent(config)
    trends = await topics_agent.research()
    
    print(f"\nFound {len(trends)} trending topics:")
    for i, trend in enumerate(trends[:3], 1):
        print(f"  {i}. {trend.get('title', trend.get('query', 'N/A'))}")
        print(f"     Source: {trend['source']}, Score: {trend.get('video_potential_score', 0):.2f}")
    
    # Step 2: Generate video from top topic
    print("\n" + "=" * 60)
    print("Step 2: Generating video from top topic...")
    print("-" * 60)
    
    if trends:
        top_topic = trends[0]
        print(f"\nTopic: {top_topic.get('title', 'N/A')}")
        
        generation_agent = VideoGenerationOrchestrator(config)
        result = await generation_agent.generate_video(top_topic)
        
        if result['status'] == 'success':
            print("\n✓ Video generated successfully!")
            print(f"  Video path: {result['video_path']}")
            print(f"  Generation time: {result['duration']:.2f}s")
        else:
            print(f"\n✗ Video generation failed: {result.get('error', 'Unknown error')}")
    else:
        print("\nNo topics found to generate video from.")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
