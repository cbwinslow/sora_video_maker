"""
Video Validation and Quality Check Tool

This tool validates video files and checks their quality.
"""

import os
import subprocess
import json
import logging
from typing import Dict, Optional, List, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoValidator:
    """Validate and check video quality"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.min_duration = self.config.get('min_duration', 1.0)  # seconds
        self.max_duration = self.config.get('max_duration', 3600.0)  # 1 hour
        self.min_resolution = self.config.get('min_resolution', (640, 480))
        self.supported_codecs = self.config.get('supported_codecs', ['h264', 'h265', 'vp8', 'vp9'])
        
    def validate_file_exists(self, video_path: str) -> Tuple[bool, str]:
        """
        Check if video file exists and is readable
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not os.path.exists(video_path):
            return False, f"File does not exist: {video_path}"
        
        if not os.path.isfile(video_path):
            return False, f"Path is not a file: {video_path}"
        
        if not os.access(video_path, os.R_OK):
            return False, f"File is not readable: {video_path}"
        
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            return False, "File is empty"
        
        return True, "File exists and is readable"
    
    def get_video_info(self, video_path: str) -> Optional[Dict]:
        """
        Get detailed video information using ffprobe
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video info or None
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"ffprobe error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("ffprobe timeout")
            return None
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    def validate_duration(self, info: Dict) -> Tuple[bool, str]:
        """
        Validate video duration
        
        Args:
            info: Video info from ffprobe
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            duration = float(info.get('format', {}).get('duration', 0))
            
            if duration < self.min_duration:
                return False, f"Duration too short: {duration}s (min: {self.min_duration}s)"
            
            if duration > self.max_duration:
                return False, f"Duration too long: {duration}s (max: {self.max_duration}s)"
            
            return True, f"Duration valid: {duration:.2f}s"
            
        except (ValueError, TypeError) as e:
            return False, f"Invalid duration value: {e}"
    
    def validate_resolution(self, info: Dict) -> Tuple[bool, str]:
        """
        Validate video resolution
        
        Args:
            info: Video info from ffprobe
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            video_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                return False, "No video stream found"
            
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            
            if width < self.min_resolution[0] or height < self.min_resolution[1]:
                return False, f"Resolution too low: {width}x{height} (min: {self.min_resolution[0]}x{self.min_resolution[1]})"
            
            return True, f"Resolution valid: {width}x{height}"
            
        except (ValueError, TypeError) as e:
            return False, f"Invalid resolution value: {e}"
    
    def validate_codec(self, info: Dict) -> Tuple[bool, str]:
        """
        Validate video codec
        
        Args:
            info: Video info from ffprobe
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            video_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                return False, "No video stream found"
            
            codec = video_stream.get('codec_name', '')
            
            if codec not in self.supported_codecs:
                return False, f"Unsupported codec: {codec} (supported: {', '.join(self.supported_codecs)})"
            
            return True, f"Codec valid: {codec}"
            
        except Exception as e:
            return False, f"Error validating codec: {e}"
    
    def validate_audio(self, info: Dict) -> Tuple[bool, str]:
        """
        Check if video has audio stream
        
        Args:
            info: Video info from ffprobe
            
        Returns:
            Tuple of (has_audio, message)
        """
        try:
            audio_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    audio_stream = stream
                    break
            
            if not audio_stream:
                return False, "No audio stream found"
            
            codec = audio_stream.get('codec_name', '')
            sample_rate = audio_stream.get('sample_rate', '')
            
            return True, f"Audio valid: {codec} @ {sample_rate}Hz"
            
        except Exception as e:
            return False, f"Error checking audio: {e}"
    
    def check_corruption(self, video_path: str) -> Tuple[bool, str]:
        """
        Check for video file corruption
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Try to decode a few frames
            cmd = [
                'ffmpeg',
                '-v', 'error',
                '-i', video_path,
                '-f', 'null',
                '-t', '5',  # Check first 5 seconds
                '-'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0 or result.stderr:
                return False, f"Corruption detected: {result.stderr[:200]}"
            
            return True, "No corruption detected"
            
        except subprocess.TimeoutExpired:
            return False, "Corruption check timeout"
        except Exception as e:
            return False, f"Error checking corruption: {e}"
    
    def calculate_quality_score(self, info: Dict) -> float:
        """
        Calculate overall quality score (0-100)
        
        Args:
            info: Video info from ffprobe
            
        Returns:
            Quality score
        """
        score = 0.0
        
        try:
            # Resolution score (0-30)
            video_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), None)
            if video_stream:
                width = int(video_stream.get('width', 0))
                height = int(video_stream.get('height', 0))
                pixels = width * height
                
                if pixels >= 1920 * 1080:
                    score += 30
                elif pixels >= 1280 * 720:
                    score += 20
                elif pixels >= 640 * 480:
                    score += 10
            
            # Codec score (0-20)
            if video_stream:
                codec = video_stream.get('codec_name', '')
                if codec in ['h265', 'vp9']:
                    score += 20
                elif codec in ['h264', 'vp8']:
                    score += 15
                else:
                    score += 5
            
            # Bitrate score (0-20)
            bit_rate = float(info.get('format', {}).get('bit_rate', 0))
            if bit_rate >= 5000000:  # 5 Mbps
                score += 20
            elif bit_rate >= 2000000:  # 2 Mbps
                score += 15
            elif bit_rate >= 1000000:  # 1 Mbps
                score += 10
            else:
                score += 5
            
            # Audio score (0-15)
            audio_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'audio'), None)
            if audio_stream:
                score += 10
                sample_rate = int(audio_stream.get('sample_rate', 0))
                if sample_rate >= 44100:
                    score += 5
            
            # Frame rate score (0-15)
            if video_stream:
                fps_str = video_stream.get('r_frame_rate', '0/1')
                try:
                    num, den = map(int, fps_str.split('/'))
                    fps = num / den if den != 0 else 0
                    
                    if fps >= 60:
                        score += 15
                    elif fps >= 30:
                        score += 10
                    elif fps >= 24:
                        score += 5
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error calculating quality score: {e}")
        
        return min(score, 100.0)
    
    def validate_video(self, video_path: str, check_corruption: bool = True) -> Dict:
        """
        Perform complete video validation
        
        Args:
            video_path: Path to video file
            check_corruption: Whether to check for corruption
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'path': video_path,
            'is_valid': False,
            'checks': {},
            'errors': [],
            'warnings': [],
            'quality_score': 0.0
        }
        
        # Check file exists
        is_valid, message = self.validate_file_exists(video_path)
        results['checks']['file_exists'] = {'valid': is_valid, 'message': message}
        
        if not is_valid:
            results['errors'].append(message)
            return results
        
        # Get video info
        info = self.get_video_info(video_path)
        if not info:
            results['errors'].append("Failed to get video information")
            return results
        
        results['info'] = info
        
        # Validate duration
        is_valid, message = self.validate_duration(info)
        results['checks']['duration'] = {'valid': is_valid, 'message': message}
        if not is_valid:
            results['errors'].append(message)
        
        # Validate resolution
        is_valid, message = self.validate_resolution(info)
        results['checks']['resolution'] = {'valid': is_valid, 'message': message}
        if not is_valid:
            results['errors'].append(message)
        
        # Validate codec
        is_valid, message = self.validate_codec(info)
        results['checks']['codec'] = {'valid': is_valid, 'message': message}
        if not is_valid:
            results['errors'].append(message)
        
        # Check audio
        has_audio, message = self.validate_audio(info)
        results['checks']['audio'] = {'valid': has_audio, 'message': message}
        if not has_audio:
            results['warnings'].append(message)
        
        # Check corruption
        if check_corruption:
            is_valid, message = self.check_corruption(video_path)
            results['checks']['corruption'] = {'valid': is_valid, 'message': message}
            if not is_valid:
                results['errors'].append(message)
        
        # Calculate quality score
        results['quality_score'] = self.calculate_quality_score(info)
        
        # Overall validity
        results['is_valid'] = len(results['errors']) == 0
        
        return results


def main():
    """Example usage"""
    validator = VideoValidator({
        'min_duration': 1.0,
        'max_duration': 600.0,
        'min_resolution': (640, 480),
        'supported_codecs': ['h264', 'h265', 'vp8', 'vp9']
    })
    
    # Example validation
    test_video = 'output/videos/test.mp4'
    
    print(f"Validating video: {test_video}")
    results = validator.validate_video(test_video, check_corruption=True)
    
    print(f"\nValidation Results:")
    print(f"Valid: {results['is_valid']}")
    print(f"Quality Score: {results['quality_score']:.1f}/100")
    
    if results['errors']:
        print(f"\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
    
    if results['warnings']:
        print(f"\nWarnings:")
        for warning in results['warnings']:
            print(f"  - {warning}")
    
    print(f"\nDetailed Checks:")
    for check_name, check_result in results['checks'].items():
        status = "✓" if check_result['valid'] else "✗"
        print(f"  {status} {check_name}: {check_result['message']}")


if __name__ == '__main__':
    main()
