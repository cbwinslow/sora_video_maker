"""
Command-Line Interface for Video Processing Agents

Easy-to-use CLI for accessing all video processing capabilities.
"""

import argparse
import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.audio_processing_agent import AudioProcessingAgent
from agents.video_quality_agent import VideoQualityAgent
from agents.subtitle_agent import SubtitleAgent


def load_config():
    """Load configuration from config file"""
    config_path = Path('config/config.yaml')
    if config_path.exists():
        import yaml
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    # Default config
    return {
        'audio': {'output_directory': 'output/audio'},
        'quality': {'output_directory': 'output/qa_reports'},
        'subtitles': {'output_directory': 'output/subtitles'},
        'workflow': {'temp_directory': 'temp'}
    }


def cmd_audio(args):
    """Handle audio processing commands"""
    config = load_config()
    agent = AudioProcessingAgent(config)
    
    if args.action == 'extract':
        result = agent.extract_audio(args.video, output_format=args.format or 'mp3')
        print(f"✓ Audio extracted: {result}")
    
    elif args.action == 'normalize':
        result = agent.normalize_audio(args.audio, target_level=args.level or -16.0)
        print(f"✓ Audio normalized: {result}")
    
    elif args.action == 'denoise':
        result = agent.remove_noise(args.audio, noise_reduction=args.reduction or 10)
        print(f"✓ Noise removed: {result}")
    
    elif args.action == 'mix':
        tracks = []
        for track_spec in args.tracks:
            path, volume = track_spec.split(':')
            tracks.append((path, float(volume)))
        result = agent.mix_audio_tracks(tracks)
        print(f"✓ Audio mixed: {result}")
    
    elif args.action == 'analyze':
        result = agent.analyze_audio(args.audio)
        print(f"\n=== Audio Analysis ===")
        print(f"Codec: {result.get('codec', 'unknown')}")
        print(f"Sample Rate: {result.get('sample_rate', 0)} Hz")
        print(f"Bitrate: {result.get('bitrate', 0)} bps")
        print(f"Duration: {result.get('duration', 0):.1f}s")
        print(f"Quality: {result.get('quality_score', 'unknown')}")
    
    elif args.action == 'convert':
        result = agent.convert_format(args.audio, args.format, quality=args.quality or 'high')
        print(f"✓ Audio converted: {result}")


def cmd_quality(args):
    """Handle quality assurance commands"""
    config = load_config()
    agent = VideoQualityAgent(config)
    
    if args.action == 'validate':
        report = agent.validate_video(args.video)
        
        print(f"\n=== Video Quality Report ===")
        print(f"Valid: {'✓ Yes' if report['valid'] else '✗ No'}")
        print(f"Score: {report.get('score', 0):.1f}/100")
        
        if report.get('errors'):
            print(f"\nErrors:")
            for error in report['errors']:
                print(f"  ✗ {error}")
        
        if report.get('warnings'):
            print(f"\nWarnings:")
            for warning in report['warnings']:
                print(f"  ⚠ {warning}")
        
        print(f"\nFull report saved to: output/qa_reports/")
    
    elif args.action == 'batch':
        videos = args.videos
        reports = agent.batch_validate(videos)
        
        valid_count = sum(1 for r in reports if r['valid'])
        avg_score = sum(r.get('score', 0) for r in reports) / len(reports) if reports else 0
        
        print(f"\n=== Batch Validation Results ===")
        print(f"Total: {len(reports)}")
        print(f"Valid: {valid_count}")
        print(f"Invalid: {len(reports) - valid_count}")
        print(f"Average Score: {avg_score:.1f}/100")
    
    elif args.action == 'compare':
        comparison = agent.compare_videos(args.video1, args.video2)
        
        print(f"\n=== Video Comparison ===")
        print(f"Video 1 Score: {comparison['video1'].get('score', 0):.1f}/100")
        print(f"Video 2 Score: {comparison['video2'].get('score', 0):.1f}/100")
        
        if comparison['differences']:
            print(f"\nDifferences:")
            for diff in comparison['differences']:
                print(f"  {diff['metric']}: {diff['video1']} vs {diff['video2']}")
    
    elif args.action == 'report':
        report_path = agent.generate_quality_report(args.video)
        print(f"✓ Quality report generated: {report_path}")


def cmd_subtitle(args):
    """Handle subtitle commands"""
    config = load_config()
    agent = SubtitleAgent(config)
    
    if args.action == 'generate':
        result = agent.generate_subtitles_from_audio(args.video, language=args.language or 'en')
        print(f"✓ Subtitles generated: {result}")
    
    elif args.action == 'burn':
        style = {}
        if args.fontsize:
            style['fontsize'] = args.fontsize
        if args.fontcolor:
            style['fontcolor'] = args.fontcolor
        
        result = agent.burn_subtitles(args.video, args.subtitle, style=style if style else None)
        print(f"✓ Subtitles burned: {result}")
    
    elif args.action == 'soft':
        result = agent.add_soft_subtitles(args.video, args.subtitle, language=args.language or 'eng')
        print(f"✓ Soft subtitles added: {result}")
    
    elif args.action == 'sync':
        result = agent.sync_subtitles(args.subtitle, args.offset)
        print(f"✓ Subtitles synced: {result}")
    
    elif args.action == 'merge':
        result = agent.merge_subtitles(args.subtitles)
        print(f"✓ Subtitles merged: {result}")
    
    elif args.action == 'translate':
        result = agent.translate_subtitles(args.subtitle, target_language=args.language)
        print(f"✓ Subtitles translated: {result}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Video Processing CLI - Access all video processing agents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Audio processing
  python cli.py audio extract video.mp4 --format mp3
  python cli.py audio normalize audio.mp3 --level -16
  python cli.py audio mix --tracks audio1.mp3:1.0 music.mp3:0.3
  
  # Quality assurance
  python cli.py quality validate video.mp4
  python cli.py quality batch video1.mp4 video2.mp4 video3.mp4
  python cli.py quality compare video1.mp4 video2.mp4
  
  # Subtitles
  python cli.py subtitle generate video.mp4 --language en
  python cli.py subtitle burn video.mp4 subtitles.srt
  python cli.py subtitle sync subtitles.srt --offset 2.0
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Audio commands
    audio_parser = subparsers.add_parser('audio', help='Audio processing commands')
    audio_parser.add_argument('action', choices=['extract', 'normalize', 'denoise', 'mix', 'analyze', 'convert'])
    audio_parser.add_argument('--video', help='Video file path')
    audio_parser.add_argument('--audio', help='Audio file path')
    audio_parser.add_argument('--format', help='Output format')
    audio_parser.add_argument('--level', type=float, help='Target LUFS level')
    audio_parser.add_argument('--reduction', type=int, help='Noise reduction level')
    audio_parser.add_argument('--tracks', nargs='+', help='Tracks to mix (path:volume)')
    audio_parser.add_argument('--quality', help='Quality preset (low, medium, high, lossless)')
    audio_parser.set_defaults(func=cmd_audio)
    
    # Quality commands
    quality_parser = subparsers.add_parser('quality', help='Quality assurance commands')
    quality_parser.add_argument('action', choices=['validate', 'batch', 'compare', 'report'])
    quality_parser.add_argument('--video', help='Video file path')
    quality_parser.add_argument('--video1', help='First video for comparison')
    quality_parser.add_argument('--video2', help='Second video for comparison')
    quality_parser.add_argument('--videos', nargs='+', help='Multiple videos for batch processing')
    quality_parser.set_defaults(func=cmd_quality)
    
    # Subtitle commands
    subtitle_parser = subparsers.add_parser('subtitle', help='Subtitle commands')
    subtitle_parser.add_argument('action', choices=['generate', 'burn', 'soft', 'sync', 'merge', 'translate'])
    subtitle_parser.add_argument('--video', help='Video file path')
    subtitle_parser.add_argument('--subtitle', help='Subtitle file path')
    subtitle_parser.add_argument('--subtitles', nargs='+', help='Multiple subtitle files')
    subtitle_parser.add_argument('--language', help='Language code')
    subtitle_parser.add_argument('--offset', type=float, help='Time offset in seconds')
    subtitle_parser.add_argument('--fontsize', type=int, help='Font size')
    subtitle_parser.add_argument('--fontcolor', help='Font color')
    subtitle_parser.set_defaults(func=cmd_subtitle)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        args.func(args)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
