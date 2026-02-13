"""
Example: YouTube Shorts Creation Workflow

Demonstrates how to:
1. Download a video from YouTube
2. Analyze the video
3. Create multiple Shorts from it
4. Optimize for the Shorts format
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.youtube_shorts_agent import YouTubeShortsAgent
from agents.video_analysis_agent import VideoAnalysisAgent
import yaml


def load_config():
    """Load configuration"""
    config_path = 'config/config.yaml'
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    # Default configuration
    return {
        'video_generation': {'output_directory': 'output/shorts'},
        'workflow': {'temp_directory': 'temp'}
    }


def create_shorts_from_youtube_url(url: str):
    """Download video and create Shorts"""
    config = load_config()
    
    print("=" * 60)
    print("YouTube Shorts Creator")
    print("=" * 60)
    print()
    
    # Initialize agents
    shorts_agent = YouTubeShortsAgent(config)
    analysis_agent = VideoAnalysisAgent(config)
    
    # Step 1: Download video
    print("Step 1: Downloading video...")
    video_path = shorts_agent.download_video(url)
    
    if not video_path:
        print("❌ Failed to download video")
        return
    
    print(f"✓ Downloaded: {video_path}")
    print()
    
    # Step 2: Analyze video
    print("Step 2: Analyzing video...")
    analysis = analysis_agent.analyze_comprehensive(video_path)
    
    print(f"✓ Duration: {analysis['metadata'].get('duration', 0):.1f}s")
    print(f"✓ Resolution: {analysis['technical'].get('width')}x{analysis['technical'].get('height')}")
    print(f"✓ Quality: {analysis['quality'].get('overall_score')}")
    print()
    
    # Step 3: Create Shorts
    print("Step 3: Creating Shorts...")
    shorts = shorts_agent.create_shorts_from_video(video_path, auto_analyze=True)
    
    print(f"✓ Created {len(shorts)} Shorts:")
    for i, short in enumerate(shorts, 1):
        print(f"   {i}. {short}")
    print()
    
    print("=" * 60)
    print("Shorts creation complete!")
    print("=" * 60)


def create_shorts_from_local_video(video_path: str):
    """Create Shorts from local video file"""
    config = load_config()
    
    print("=" * 60)
    print("Create Shorts from Local Video")
    print("=" * 60)
    print()
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return
    
    # Initialize agents
    shorts_agent = YouTubeShortsAgent(config)
    analysis_agent = VideoAnalysisAgent(config)
    
    # Analyze video
    print("Analyzing video...")
    analysis = analysis_agent.analyze_comprehensive(video_path)
    
    print(f"Duration: {analysis['metadata'].get('duration', 0):.1f}s")
    print(f"Resolution: {analysis['technical'].get('width')}x{analysis['technical'].get('height')}")
    
    # Print recommendations
    if analysis.get('recommendations'):
        print("\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")
    print()
    
    # Create Shorts
    print("Creating Shorts...")
    shorts = shorts_agent.create_shorts_from_video(video_path)
    
    print(f"\n✓ Created {len(shorts)} Shorts:")
    for i, short in enumerate(shorts, 1):
        print(f"   {i}. {short}")
    print()


def optimize_existing_video_for_shorts(video_path: str):
    """Optimize an existing video for Shorts format"""
    config = load_config()
    
    print("=" * 60)
    print("Optimize Video for Shorts")
    print("=" * 60)
    print()
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return
    
    shorts_agent = YouTubeShortsAgent(config)
    
    print("Optimizing video for Shorts format (9:16 vertical)...")
    optimized = shorts_agent.optimize_for_shorts(video_path)
    
    print(f"✓ Optimized video: {optimized}")
    print()


def main():
    """Main example"""
    print("\nYouTube Shorts Creation Examples")
    print("=" * 60)
    print()
    print("Choose an option:")
    print("  1. Create Shorts from YouTube URL")
    print("  2. Create Shorts from local video file")
    print("  3. Optimize existing video for Shorts")
    print("  4. Run demo with sample video")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == '1':
        url = input("Enter YouTube URL: ").strip()
        if url:
            create_shorts_from_youtube_url(url)
        else:
            print("❌ No URL provided")
    
    elif choice == '2':
        path = input("Enter video file path: ").strip()
        if path:
            create_shorts_from_local_video(path)
        else:
            print("❌ No path provided")
    
    elif choice == '3':
        path = input("Enter video file path: ").strip()
        if path:
            optimize_existing_video_for_shorts(path)
        else:
            print("❌ No path provided")
    
    elif choice == '4':
        print("\nDemo mode:")
        print("This would normally process a sample video.")
        print("To use, provide a sample video file.")
        print()
        print("Example usage:")
        print("  python examples/create_shorts.py")
        print()
    
    else:
        print("❌ Invalid choice")


if __name__ == '__main__':
    main()
