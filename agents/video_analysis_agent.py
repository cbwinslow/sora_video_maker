"""
Video Analysis Agent

Analyzes videos to extract metadata, detect scenes, identify key moments,
and provide insights for content optimization.
"""

import os
import json
import logging
import subprocess
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoAnalysisAgent:
    """Agent for comprehensive video analysis"""

    def __init__(self, config: Dict):
        self.config = config
        self.temp_dir = config.get('workflow', {}).get('temp_directory', 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)

    def analyze_comprehensive(self, video_path: str) -> Dict:
        """Perform comprehensive video analysis"""
        logger.info(f"Starting comprehensive analysis of: {video_path}")
        
        analysis = {
            'metadata': self.get_metadata(video_path),
            'technical': self.get_technical_info(video_path),
            'scenes': self.detect_scenes(video_path),
            'audio': self.analyze_audio(video_path),
            'quality': self.assess_quality(video_path)
        }
        
        # Add recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        logger.info("Comprehensive analysis complete")
        return analysis

    def get_metadata(self, video_path: str) -> Dict:
        """Extract basic video metadata"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            format_info = data.get('format', {})
            video_stream = next(
                (s for s in data.get('streams', []) if s['codec_type'] == 'video'),
                {}
            )
            audio_stream = next(
                (s for s in data.get('streams', []) if s['codec_type'] == 'audio'),
                {}
            )
            
            return {
                'filename': os.path.basename(video_path),
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bitrate': int(format_info.get('bit_rate', 0)),
                'format': format_info.get('format_name', 'unknown'),
                'has_video': bool(video_stream),
                'has_audio': bool(audio_stream)
            }
        except Exception as e:
            logger.error(f"Error getting metadata: {e}")
            return {}

    def get_technical_info(self, video_path: str) -> Dict:
        """Get detailed technical information"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            video_stream = next(
                (s for s in data.get('streams', []) if s['codec_type'] == 'video'),
                {}
            )
            
            if not video_stream:
                return {}
            
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            
            return {
                'codec': video_stream.get('codec_name', 'unknown'),
                'width': width,
                'height': height,
                'aspect_ratio': f"{width}:{height}",
                'fps': self._parse_frame_rate(video_stream.get('r_frame_rate', '0/1')),
                'pixel_format': video_stream.get('pix_fmt', 'unknown'),
                'color_space': video_stream.get('color_space', 'unknown'),
                'total_frames': int(video_stream.get('nb_frames', 0))
            }
        except Exception as e:
            logger.error(f"Error getting technical info: {e}")
            return {}

    def detect_scenes(self, video_path: str, threshold: float = 0.4) -> List[Dict]:
        """Detect scene changes in video"""
        logger.info(f"Detecting scenes with threshold {threshold}")
        
        try:
            # Use ffmpeg scene detection
            output_file = os.path.join(self.temp_dir, 'scenes.txt')
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-filter:v', f'select=gt(scene\\,{threshold}),showinfo',
                '-f', 'null',
                '-'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse scene detection output
            scenes = self._parse_scene_output(result.stderr)
            
            logger.info(f"Detected {len(scenes)} scenes")
            return scenes
            
        except subprocess.TimeoutExpired:
            logger.warning("Scene detection timed out")
            return []
        except Exception as e:
            logger.error(f"Error detecting scenes: {e}")
            return []

    def _parse_scene_output(self, output: str) -> List[Dict]:
        """Parse ffmpeg scene detection output"""
        scenes = []
        lines = output.split('\n')
        
        for line in lines:
            if 'pts_time:' in line:
                try:
                    # Extract timestamp
                    time_str = line.split('pts_time:')[1].split()[0]
                    timestamp = float(time_str)
                    
                    scenes.append({
                        'timestamp': timestamp,
                        'time_formatted': str(timedelta(seconds=int(timestamp)))
                    })
                except (IndexError, ValueError) as e:
                    continue
        
        return scenes

    def analyze_audio(self, video_path: str) -> Dict:
        """Analyze audio track"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                '-select_streams', 'a:0',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            if not data.get('streams'):
                return {'has_audio': False}
            
            audio_stream = data['streams'][0]
            
            return {
                'has_audio': True,
                'codec': audio_stream.get('codec_name', 'unknown'),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'bitrate': int(audio_stream.get('bit_rate', 0)),
                'duration': float(audio_stream.get('duration', 0))
            }
        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            return {'has_audio': False}

    def assess_quality(self, video_path: str) -> Dict:
        """Assess video quality"""
        metadata = self.get_metadata(video_path)
        technical = self.get_technical_info(video_path)
        
        # Calculate quality metrics
        width = technical.get('width', 0)
        height = technical.get('height', 0)
        fps = technical.get('fps', 0)
        bitrate = metadata.get('bitrate', 0)
        
        # Determine resolution category
        if height >= 2160:
            resolution_quality = '4K'
        elif height >= 1080:
            resolution_quality = 'Full HD'
        elif height >= 720:
            resolution_quality = 'HD'
        else:
            resolution_quality = 'SD'
        
        # Assess bitrate quality
        pixels = width * height
        bitrate_per_pixel = bitrate / pixels if pixels > 0 else 0
        
        if bitrate_per_pixel > 0.1:
            bitrate_quality = 'High'
        elif bitrate_per_pixel > 0.05:
            bitrate_quality = 'Medium'
        else:
            bitrate_quality = 'Low'
        
        # Assess frame rate
        if fps >= 60:
            fps_quality = 'High (60+ fps)'
        elif fps >= 30:
            fps_quality = 'Standard (30 fps)'
        elif fps >= 24:
            fps_quality = 'Cinematic (24 fps)'
        else:
            fps_quality = 'Low'
        
        return {
            'resolution_quality': resolution_quality,
            'bitrate_quality': bitrate_quality,
            'fps_quality': fps_quality,
            'overall_score': self._calculate_overall_score(
                resolution_quality,
                bitrate_quality,
                fps_quality
            )
        }

    def _calculate_overall_score(
        self,
        resolution: str,
        bitrate: str,
        fps: str
    ) -> str:
        """Calculate overall quality score"""
        score = 0
        
        if resolution in ['4K', 'Full HD']:
            score += 3
        elif resolution == 'HD':
            score += 2
        else:
            score += 1
        
        if bitrate == 'High':
            score += 3
        elif bitrate == 'Medium':
            score += 2
        else:
            score += 1
        
        if 'High' in fps or 'Standard' in fps:
            score += 2
        else:
            score += 1
        
        if score >= 7:
            return 'Excellent'
        elif score >= 5:
            return 'Good'
        elif score >= 3:
            return 'Fair'
        else:
            return 'Poor'

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        technical = analysis.get('technical', {})
        quality = analysis.get('quality', {})
        metadata = analysis.get('metadata', {})
        
        # Resolution recommendations
        height = technical.get('height', 0)
        if height < 720:
            recommendations.append("Consider upscaling to at least 720p for better quality")
        
        # Bitrate recommendations
        if quality.get('bitrate_quality') == 'Low':
            recommendations.append("Increase bitrate for better video quality")
        
        # Duration recommendations
        duration = metadata.get('duration', 0)
        if duration > 600:  # 10 minutes
            recommendations.append("Consider splitting into shorter segments for better engagement")
        
        # Audio recommendations
        audio = analysis.get('audio', {})
        if not audio.get('has_audio'):
            recommendations.append("Add audio track or background music")
        
        # Shorts optimization
        if duration <= 60 and height < 1920:
            recommendations.append("Optimize for YouTube Shorts (1080x1920 vertical format)")
        
        return recommendations

    def _parse_frame_rate(self, fps_str: str) -> float:
        """Parse frame rate string (e.g., '30/1' -> 30.0)"""
        try:
            if '/' in fps_str:
                num, den = fps_str.split('/')
                return float(num) / float(den)
            return float(fps_str)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def extract_keyframes(self, video_path: str, output_dir: Optional[str] = None) -> List[str]:
        """Extract keyframes from video"""
        if output_dir is None:
            output_dir = os.path.join(self.temp_dir, 'keyframes')
        
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Extracting keyframes to: {output_dir}")
        
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', 'select=eq(pict_type\\,I)',
                '-vsync', 'vfr',
                os.path.join(output_dir, 'keyframe_%04d.png')
            ]
            
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            
            keyframes = sorted([
                os.path.join(output_dir, f)
                for f in os.listdir(output_dir)
                if f.endswith('.png')
            ])
            
            logger.info(f"Extracted {len(keyframes)} keyframes")
            return keyframes
            
        except Exception as e:
            logger.error(f"Error extracting keyframes: {e}")
            return []


def main():
    """Example usage"""
    config = {
        'workflow': {'temp_directory': 'temp'}
    }
    
    agent = VideoAnalysisAgent(config)
    
    print("Video Analysis Agent - Ready")
    print("\nAvailable methods:")
    print("  - analyze_comprehensive(path)")
    print("  - get_metadata(path)")
    print("  - get_technical_info(path)")
    print("  - detect_scenes(path)")
    print("  - analyze_audio(path)")
    print("  - assess_quality(path)")
    print("  - extract_keyframes(path)")


if __name__ == '__main__':
    main()
