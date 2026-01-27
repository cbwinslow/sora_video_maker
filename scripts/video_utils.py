"""
Utility functions for video processing and manipulation
"""

import os
import subprocess
import logging
from typing import Optional, Tuple, List
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_video_info(video_path: str) -> Optional[Dict]:
    """Get video information using ffprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        else:
            logger.error(f"ffprobe error: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return None


def resize_video(input_path: str, output_path: str, width: int = 1920, height: int = 1080) -> bool:
    """Resize video to specified dimensions"""
    try:
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', f'scale={width}:{height}',
            '-c:a', 'copy',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            logger.info(f"Video resized successfully: {output_path}")
            return True
        else:
            logger.error(f"ffmpeg error: {result.stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Error resizing video: {e}")
        return False


def concatenate_videos(video_paths: List[str], output_path: str) -> bool:
    """Concatenate multiple videos into one"""
    try:
        # Create temporary file list
        list_file = 'temp/concat_list.txt'
        os.makedirs('temp', exist_ok=True)
        
        with open(list_file, 'w') as f:
            for path in video_paths:
                f.write(f"file '{os.path.abspath(path)}'\n")
        
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c', 'copy',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            logger.info(f"Videos concatenated successfully: {output_path}")
            return True
        else:
            logger.error(f"ffmpeg error: {result.stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Error concatenating videos: {e}")
        return False
    finally:
        # Clean up temp file
        if os.path.exists(list_file):
            os.remove(list_file)


def add_audio_to_video(video_path: str, audio_path: str, output_path: str) -> bool:
    """Add audio track to video"""
    try:
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            logger.info(f"Audio added successfully: {output_path}")
            return True
        else:
            logger.error(f"ffmpeg error: {result.stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Error adding audio: {e}")
        return False


def extract_frames(video_path: str, output_dir: str, fps: int = 1) -> bool:
    """Extract frames from video at specified fps"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'fps={fps}',
            '-y',
            os.path.join(output_dir, 'frame_%04d.png')
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            logger.info(f"Frames extracted to: {output_dir}")
            return True
        else:
            logger.error(f"ffmpeg error: {result.stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Error extracting frames: {e}")
        return False


def create_video_from_images(image_dir: str, output_path: str, fps: int = 30) -> bool:
    """Create video from sequence of images"""
    try:
        cmd = [
            'ffmpeg',
            '-framerate', str(fps),
            '-pattern_type', 'glob',
            '-i', os.path.join(image_dir, '*.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            logger.info(f"Video created successfully: {output_path}")
            return True
        else:
            logger.error(f"ffmpeg error: {result.stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        return False


def add_text_overlay(video_path: str, output_path: str, text: str, position: str = 'top') -> bool:
    """Add text overlay to video"""
    try:
        # Position mappings
        positions = {
            'top': 'x=(w-text_w)/2:y=50',
            'bottom': 'x=(w-text_w)/2:y=h-th-50',
            'center': 'x=(w-text_w)/2:y=(h-text_h)/2'
        }
        
        pos = positions.get(position, positions['top'])
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f"drawtext=text='{text}':fontsize=48:fontcolor=white:{pos}",
            '-codec:a', 'copy',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            logger.info(f"Text overlay added: {output_path}")
            return True
        else:
            logger.error(f"ffmpeg error: {result.stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Error adding text overlay: {e}")
        return False


if __name__ == '__main__':
    # Test functions
    print("Video utilities module loaded successfully")
    print("\nAvailable functions:")
    print("- get_video_info()")
    print("- resize_video()")
    print("- concatenate_videos()")
    print("- add_audio_to_video()")
    print("- extract_frames()")
    print("- create_video_from_images()")
    print("- add_text_overlay()")
