"""
Video Editing Agent

This agent handles automated video editing tasks including:
- Trimming and cutting
- Adding transitions
- Color grading
- Audio enhancement
- Subtitle generation
- Adding music and effects
"""

import os
import json
import logging
import subprocess
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoEditingAgent:
    """Agent for automated video editing"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = config.get('video_generation', {}).get('output_directory', 'output/videos')
        self.temp_dir = config.get('workflow', {}).get('temp_directory', 'temp')
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def edit_video(self, video_path: str, edits: Dict) -> str:
        """Apply edits to a video"""
        logger.info(f"Editing video: {video_path}")
        
        output_path = os.path.join(
            self.output_dir,
            f"edited_{datetime.now().timestamp()}.mp4"
        )
        
        # Apply edits in sequence
        current_video = video_path
        
        if edits.get('trim'):
            current_video = self.trim_video(current_video, edits['trim'])
        
        if edits.get('add_intro'):
            current_video = self.add_intro(current_video, edits['add_intro'])
        
        if edits.get('add_outro'):
            current_video = self.add_outro(current_video, edits['add_outro'])
        
        if edits.get('add_music'):
            current_video = self.add_background_music(current_video, edits['add_music'])
        
        if edits.get('add_subtitles'):
            current_video = self.add_subtitles(current_video, edits['add_subtitles'])
        
        if edits.get('color_grade'):
            current_video = self.apply_color_grade(current_video, edits['color_grade'])
        
        if edits.get('add_transitions'):
            current_video = self.add_transitions(current_video, edits['add_transitions'])
        
        # Copy to final output if different
        if current_video != output_path:
            os.rename(current_video, output_path)
        
        logger.info(f"Editing complete: {output_path}")
        return output_path
    
    def trim_video(self, video_path: str, trim_config: Dict) -> str:
        """Trim video to specified duration"""
        start_time = trim_config.get('start', 0)
        duration = trim_config.get('duration', None)
        
        output_path = os.path.join(self.temp_dir, f"trimmed_{os.path.basename(video_path)}")
        
        cmd = ['ffmpeg', '-i', video_path, '-ss', str(start_time)]
        
        if duration:
            cmd.extend(['-t', str(duration)])
        
        cmd.extend(['-c', 'copy', '-y', output_path])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Video trimmed: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error trimming video: {e}")
            return video_path
    
    def add_intro(self, video_path: str, intro_path: str) -> str:
        """Add intro to video"""
        output_path = os.path.join(self.temp_dir, f"with_intro_{os.path.basename(video_path)}")
        
        # Create concat file
        concat_file = os.path.join(self.temp_dir, 'concat_intro.txt')
        with open(concat_file, 'w') as f:
            f.write(f"file '{os.path.abspath(intro_path)}'\n")
            f.write(f"file '{os.path.abspath(video_path)}'\n")
        
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y', output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Intro added: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error adding intro: {e}")
            return video_path
    
    def add_outro(self, video_path: str, outro_path: str) -> str:
        """Add outro to video"""
        output_path = os.path.join(self.temp_dir, f"with_outro_{os.path.basename(video_path)}")
        
        # Create concat file
        concat_file = os.path.join(self.temp_dir, 'concat_outro.txt')
        with open(concat_file, 'w') as f:
            f.write(f"file '{os.path.abspath(video_path)}'\n")
            f.write(f"file '{os.path.abspath(outro_path)}'\n")
        
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y', output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Outro added: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error adding outro: {e}")
            return video_path
    
    def add_background_music(self, video_path: str, music_config: Dict) -> str:
        """Add background music to video"""
        music_path = music_config.get('path')
        volume = music_config.get('volume', 0.3)
        
        output_path = os.path.join(self.temp_dir, f"with_music_{os.path.basename(video_path)}")
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-i', music_path,
            '-filter_complex',
            f'[1:a]volume={volume}[a1];[0:a][a1]amix=inputs=2:duration=first',
            '-c:v', 'copy',
            '-y', output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Background music added: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error adding music: {e}")
            return video_path
    
    def add_subtitles(self, video_path: str, subtitle_config: Dict) -> str:
        """Add subtitles to video"""
        subtitles = subtitle_config.get('text', [])
        
        output_path = os.path.join(self.temp_dir, f"with_subs_{os.path.basename(video_path)}")
        
        # Create SRT file
        srt_file = os.path.join(self.temp_dir, 'subtitles.srt')
        with open(srt_file, 'w') as f:
            for i, sub in enumerate(subtitles, 1):
                f.write(f"{i}\n")
                f.write(f"{sub['start']} --> {sub['end']}\n")
                f.write(f"{sub['text']}\n\n")
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f"subtitles={srt_file}:force_style='FontSize=24,PrimaryColour=&HFFFFFF'",
            '-c:a', 'copy',
            '-y', output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Subtitles added: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error adding subtitles: {e}")
            return video_path
    
    def apply_color_grade(self, video_path: str, grade: str) -> str:
        """Apply color grading to video"""
        output_path = os.path.join(self.temp_dir, f"graded_{os.path.basename(video_path)}")
        
        # Preset color grades
        grades = {
            'vibrant': 'eq=contrast=1.2:brightness=0.05:saturation=1.3',
            'cinematic': 'curves=vintage',
            'warm': 'colorbalance=rs=0.2:gs=0.1:bs=-0.1',
            'cool': 'colorbalance=rs=-0.1:gs=-0.05:bs=0.2',
            'bw': 'hue=s=0'
        }
        
        filter_str = grades.get(grade, grades['vibrant'])
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', filter_str,
            '-c:a', 'copy',
            '-y', output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Color grading applied: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error applying color grade: {e}")
            return video_path
    
    def add_transitions(self, video_path: str, transition_config: Dict) -> str:
        """Add transitions between clips (requires multiple clips)"""
        # This is a simplified version
        # In production, would handle complex multi-clip transitions
        logger.info("Transition support is simplified in this version")
        return video_path
    
    def create_short_form(self, video_path: str, duration: int = 60) -> str:
        """Create short-form version for TikTok/Shorts/Reels"""
        logger.info(f"Creating short-form version ({duration}s)")
        
        output_path = os.path.join(
            self.output_dir,
            f"short_{os.path.basename(video_path)}"
        )
        
        # Extract most interesting part and format for vertical video
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-t', str(duration),
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
            '-c:a', 'copy',
            '-y', output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Short-form video created: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating short-form: {e}")
            return video_path


def main():
    """Example usage"""
    config = {
        'video_generation': {'output_directory': 'output/videos'},
        'workflow': {'temp_directory': 'temp'}
    }
    
    agent = VideoEditingAgent(config)
    
    # Example edits
    edits = {
        'trim': {'start': 0, 'duration': 30},
        'color_grade': 'vibrant',
        # 'add_music': {'path': 'music/background.mp3', 'volume': 0.3},
        # 'add_subtitles': {'text': [
        #     {'start': '00:00:00,000', 'end': '00:00:05,000', 'text': 'Hello World'}
        # ]}
    }
    
    print("Video Editing Agent - Ready")
    print("Available edits: trim, add_intro, add_outro, add_music, add_subtitles, color_grade")


if __name__ == '__main__':
    main()
