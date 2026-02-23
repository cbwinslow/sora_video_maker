"""
YouTube Shorts Agent

Specialized agent for creating, optimizing, and managing YouTube Shorts content.
Handles video analysis, segmentation, and optimization for the Shorts format.
"""

import os
import logging
import json
import subprocess
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import yt_dlp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeShortsAgent:
    """Agent for YouTube Shorts creation and analysis"""

    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = config.get('video_generation', {}).get('output_directory', 'output/shorts')
        self.temp_dir = config.get('workflow', {}).get('temp_directory', 'temp')
        self.shorts_duration = 60  # Max duration for Shorts (seconds)
        self.shorts_aspect_ratio = (9, 16)  # Vertical format
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def download_video(self, url: str) -> Optional[str]:
        """Download video from YouTube URL"""
        try:
            logger.info(f"Downloading video from: {url}")
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                'quiet': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                logger.info(f"Video downloaded: {filename}")
                return filename
                
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None

    def analyze_video(self, video_path: str) -> Dict:
        """Analyze video to find best segments for Shorts"""
        logger.info(f"Analyzing video: {video_path}")
        
        try:
            # Get video metadata
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            metadata = json.loads(result.stdout)
            
            # Extract key information
            video_stream = next(
                (s for s in metadata['streams'] if s['codec_type'] == 'video'),
                None
            )
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            duration = float(metadata['format']['duration'])
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            fps = eval(video_stream['r_frame_rate'])
            
            analysis = {
                'duration': duration,
                'width': width,
                'height': height,
                'fps': fps,
                'aspect_ratio': width / height,
                'is_vertical': height > width,
                'suggested_segments': self._suggest_segments(duration)
            }
            
            logger.info(f"Analysis complete: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            return {}

    def _suggest_segments(self, duration: float) -> List[Dict]:
        """Suggest optimal segments for Shorts based on video duration"""
        segments = []
        
        if duration <= self.shorts_duration:
            # Entire video fits in one Short
            segments.append({
                'start': 0,
                'end': duration,
                'duration': duration
            })
        else:
            # Split video into multiple segments
            num_segments = int(duration / self.shorts_duration) + 1
            segment_duration = min(self.shorts_duration, duration / num_segments)
            
            for i in range(num_segments):
                start = i * segment_duration
                end = min(start + self.shorts_duration, duration)
                
                if end - start >= 10:  # Minimum 10 seconds
                    segments.append({
                        'start': start,
                        'end': end,
                        'duration': end - start
                    })
        
        return segments

    def create_short(
        self,
        video_path: str,
        start_time: float = 0,
        duration: Optional[float] = None,
        add_captions: bool = True,
        optimize_audio: bool = True
    ) -> str:
        """Create a YouTube Short from a video segment"""
        logger.info(f"Creating Short from {video_path} starting at {start_time}s")
        
        if duration is None:
            duration = self.shorts_duration
        
        duration = min(duration, self.shorts_duration)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"short_{timestamp}.mp4"
        )
        
        # Build FFmpeg command for vertical video optimization
        cmd = [
            'ffmpeg',
            '-ss', str(start_time),
            '-i', video_path,
            '-t', str(duration),
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
        ]
        
        if optimize_audio:
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', '128k',
                '-ar', '44100'
            ])
        else:
            cmd.extend(['-c:a', 'copy'])
        
        cmd.extend(['-y', output_path])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Short created: {output_path}")
            
            if add_captions:
                output_path = self._add_auto_captions(output_path)
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating Short: {e.stderr.decode()}")
            raise

    def _add_auto_captions(self, video_path: str) -> str:
        """Add automatic captions to video (placeholder for future implementation)"""
        logger.info("Auto captions feature will be implemented with speech recognition")
        # TODO: Implement with Whisper or similar
        return video_path

    def create_shorts_from_video(
        self,
        video_path: str,
        num_shorts: Optional[int] = None,
        auto_analyze: bool = True
    ) -> List[str]:
        """Create multiple Shorts from a single video"""
        logger.info(f"Creating Shorts from video: {video_path}")
        
        if auto_analyze:
            analysis = self.analyze_video(video_path)
            segments = analysis.get('suggested_segments', [])
        else:
            # Create evenly spaced segments
            duration = self._get_video_duration(video_path)
            num_shorts = num_shorts or max(1, int(duration / self.shorts_duration))
            segment_duration = min(self.shorts_duration, duration / num_shorts)
            
            segments = [
                {
                    'start': i * segment_duration,
                    'duration': segment_duration
                }
                for i in range(num_shorts)
            ]
        
        shorts = []
        for i, segment in enumerate(segments):
            try:
                short_path = self.create_short(
                    video_path,
                    start_time=segment['start'],
                    duration=segment.get('duration', self.shorts_duration)
                )
                shorts.append(short_path)
                logger.info(f"Created Short {i+1}/{len(segments)}: {short_path}")
            except Exception as e:
                logger.error(f"Failed to create Short {i+1}: {e}")
        
        return shorts

    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            return 0.0

    def optimize_for_shorts(self, video_path: str) -> str:
        """Optimize existing video for YouTube Shorts format"""
        logger.info(f"Optimizing video for Shorts: {video_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"optimized_{timestamp}.mp4"
        )
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            # Vertical format (9:16)
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
            # Encoding settings optimized for mobile
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-maxrate', '2500k',
            '-bufsize', '5000k',
            # Audio settings
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '44100',
            # Output
            '-y', output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Video optimized: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error optimizing video: {e.stderr.decode()}")
            raise

    def add_shorts_branding(
        self,
        video_path: str,
        logo_path: Optional[str] = None,
        watermark_text: Optional[str] = None
    ) -> str:
        """Add branding elements to Shorts video"""
        logger.info(f"Adding branding to: {video_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"branded_{timestamp}.mp4"
        )
        
        filter_complex = []
        
        if watermark_text:
            filter_complex.append(
                f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white@0.7:"
                f"x=10:y=h-th-10:shadowcolor=black@0.5:shadowx=2:shadowy=2"
            )
        
        cmd = ['ffmpeg', '-i', video_path]
        
        if logo_path and os.path.exists(logo_path):
            cmd.extend(['-i', logo_path])
            filter_complex.append('[0:v][1:v]overlay=W-w-10:10')
        
        if filter_complex:
            cmd.extend(['-filter_complex', ';'.join(filter_complex)])
        
        cmd.extend(['-c:a', 'copy', '-y', output_path])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Branding added: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error adding branding: {e}")
            return video_path


def main():
    """Example usage"""
    config = {
        'video_generation': {'output_directory': 'output/shorts'},
        'workflow': {'temp_directory': 'temp'}
    }
    
    agent = YouTubeShortsAgent(config)
    
    print("YouTube Shorts Agent - Ready")
    print("\nAvailable methods:")
    print("  - download_video(url)")
    print("  - analyze_video(path)")
    print("  - create_short(path, start_time, duration)")
    print("  - create_shorts_from_video(path)")
    print("  - optimize_for_shorts(path)")
    print("  - add_shorts_branding(path, logo, watermark)")


if __name__ == '__main__':
    main()
