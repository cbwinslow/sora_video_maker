"""
Subtitle Generation Agent

Automated subtitle/caption generation and synchronization for videos.
Supports multiple formats and languages.
"""

import os
import logging
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubtitleAgent:
    """Agent for subtitle generation and management"""

    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = config.get('subtitles', {}).get('output_directory', 'output/subtitles')
        self.temp_dir = config.get('workflow', {}).get('temp_directory', 'temp')
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def generate_subtitles_from_audio(
        self,
        video_path: str,
        language: str = 'en',
        model_size: str = 'base'
    ) -> str:
        """
        Generate subtitles from video audio using speech recognition
        (Placeholder for Whisper or similar integration)
        
        Args:
            video_path: Path to video file
            language: Language code (en, es, fr, etc.)
            model_size: Model size for transcription (tiny, base, small, medium, large)
        
        Returns:
            Path to generated SRT file
        """
        logger.info(f"Generating subtitles for: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        srt_path = os.path.join(
            self.output_dir,
            f"subtitles_{timestamp}.srt"
        )
        
        # TODO: Integrate with Whisper or speech recognition API
        # For now, create placeholder subtitles
        logger.warning("Speech recognition not yet integrated. Creating placeholder subtitles.")
        
        self._create_placeholder_subtitles(srt_path)
        
        logger.info(f"Subtitles generated: {srt_path}")
        return srt_path

    def _create_placeholder_subtitles(self, srt_path: str):
        """Create placeholder subtitles for demonstration"""
        subtitles = [
            {'index': 1, 'start': '00:00:00,000', 'end': '00:00:03,000', 'text': 'Welcome to this video.'},
            {'index': 2, 'start': '00:00:03,000', 'end': '00:00:06,000', 'text': 'This is an automated subtitle.'},
            {'index': 3, 'start': '00:00:06,000', 'end': '00:00:09,000', 'text': 'Thank you for watching!'}
        ]
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            for sub in subtitles:
                f.write(f"{sub['index']}\n")
                f.write(f"{sub['start']} --> {sub['end']}\n")
                f.write(f"{sub['text']}\n\n")

    def create_srt(self, subtitles: List[Dict], output_path: Optional[str] = None) -> str:
        """
        Create SRT subtitle file from subtitle data
        
        Args:
            subtitles: List of subtitle dictionaries with 'start', 'end', 'text'
            output_path: Optional output path
        
        Returns:
            Path to created SRT file
        """
        logger.info(f"Creating SRT file with {len(subtitles)} entries")
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(
                self.output_dir,
                f"subtitles_{timestamp}.srt"
            )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(subtitles, 1):
                start_time = self._format_timestamp(sub['start'])
                end_time = self._format_timestamp(sub['end'])
                text = sub['text']
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        
        logger.info(f"SRT file created: {output_path}")
        return output_path

    def create_vtt(self, subtitles: List[Dict], output_path: Optional[str] = None) -> str:
        """
        Create WebVTT subtitle file from subtitle data
        
        Args:
            subtitles: List of subtitle dictionaries
            output_path: Optional output path
        
        Returns:
            Path to created VTT file
        """
        logger.info(f"Creating VTT file with {len(subtitles)} entries")
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(
                self.output_dir,
                f"subtitles_{timestamp}.vtt"
            )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for i, sub in enumerate(subtitles, 1):
                start_time = self._format_timestamp(sub['start'], vtt=True)
                end_time = self._format_timestamp(sub['end'], vtt=True)
                text = sub['text']
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        
        logger.info(f"VTT file created: {output_path}")
        return output_path

    def _format_timestamp(self, seconds: float, vtt: bool = False) -> str:
        """
        Format timestamp for subtitles
        
        Args:
            seconds: Time in seconds
            vtt: Use VTT format instead of SRT
        
        Returns:
            Formatted timestamp string
        """
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        millis = int((seconds - int(seconds)) * 1000)
        
        if vtt:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def burn_subtitles(
        self,
        video_path: str,
        subtitle_path: str,
        style: Optional[Dict] = None
    ) -> str:
        """
        Burn subtitles into video (hard-coded)
        
        Args:
            video_path: Path to video file
            subtitle_path: Path to subtitle file
            style: Optional style dictionary (fontsize, color, etc.)
        
        Returns:
            Path to video with burned subtitles
        """
        logger.info(f"Burning subtitles into video: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not os.path.exists(subtitle_path):
            raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"subtitled_{timestamp}.mp4"
        )
        
        # Default style
        if style is None:
            style = {
                'fontsize': 24,
                'fontcolor': 'white',
                'bordercolor': 'black',
                'borderwidth': 2
            }
        
        # Escape subtitle path for FFmpeg
        subtitle_path_escaped = subtitle_path.replace('\\', '/').replace(':', '\\:')
        
        # Build subtitles filter
        subtitles_filter = (
            f"subtitles='{subtitle_path_escaped}':"
            f"force_style='FontSize={style['fontsize']},"
            f"PrimaryColour={self._color_to_ass(style['fontcolor'])},"
            f"OutlineColour={self._color_to_ass(style['bordercolor'])},"
            f"Outline={style['borderwidth']}'"
        )
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', subtitles_filter,
            '-c:a', 'copy',
            '-y',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            logger.info(f"Subtitles burned: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error burning subtitles: {e.stderr.decode()}")
            raise

    def _color_to_ass(self, color: str) -> str:
        """Convert color name to ASS subtitle format"""
        colors = {
            'white': '&HFFFFFF',
            'black': '&H000000',
            'red': '&H0000FF',
            'green': '&H00FF00',
            'blue': '&HFF0000',
            'yellow': '&H00FFFF'
        }
        return colors.get(color.lower(), '&HFFFFFF')

    def add_soft_subtitles(
        self,
        video_path: str,
        subtitle_path: str,
        language: str = 'eng'
    ) -> str:
        """
        Add soft subtitles to video (as separate stream)
        
        Args:
            video_path: Path to video file
            subtitle_path: Path to subtitle file
            language: Language code
        
        Returns:
            Path to video with soft subtitles
        """
        logger.info(f"Adding soft subtitles to: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not os.path.exists(subtitle_path):
            raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"with_subs_{timestamp}.mkv"
        )
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-i', subtitle_path,
            '-c', 'copy',
            '-c:s', 'srt',
            '-metadata:s:s:0', f'language={language}',
            '-y',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            logger.info(f"Soft subtitles added: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error adding soft subtitles: {e.stderr.decode()}")
            raise

    def translate_subtitles(
        self,
        subtitle_path: str,
        target_language: str = 'es'
    ) -> str:
        """
        Translate subtitles to another language
        (Placeholder for translation API integration)
        
        Args:
            subtitle_path: Path to subtitle file
            target_language: Target language code
        
        Returns:
            Path to translated subtitle file
        """
        logger.info(f"Translating subtitles to: {target_language}")
        
        # TODO: Integrate with translation API (Google Translate, DeepL, etc.)
        logger.warning("Translation API not yet integrated")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"translated_{target_language}_{timestamp}.srt"
        )
        
        # For now, copy the original
        import shutil
        shutil.copy(subtitle_path, output_path)
        
        logger.info(f"Translated subtitles: {output_path}")
        return output_path

    def sync_subtitles(
        self,
        subtitle_path: str,
        offset_seconds: float
    ) -> str:
        """
        Adjust subtitle timing by offset
        
        Args:
            subtitle_path: Path to subtitle file
            offset_seconds: Time offset in seconds (positive or negative)
        
        Returns:
            Path to adjusted subtitle file
        """
        logger.info(f"Syncing subtitles with offset: {offset_seconds}s")
        
        if not os.path.exists(subtitle_path):
            raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")
        
        # Read subtitles
        subtitles = self._parse_srt(subtitle_path)
        
        # Adjust timing
        for sub in subtitles:
            sub['start'] += offset_seconds
            sub['end'] += offset_seconds
            
            # Ensure non-negative times
            sub['start'] = max(0, sub['start'])
            sub['end'] = max(0, sub['end'])
        
        # Save adjusted subtitles
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"synced_{timestamp}.srt"
        )
        
        return self.create_srt(subtitles, output_path)

    def _parse_srt(self, srt_path: str) -> List[Dict]:
        """Parse SRT file into subtitle list"""
        subtitles = []
        
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into subtitle blocks
        blocks = content.strip().split('\n\n')
        
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                try:
                    # Parse timing line
                    timing = lines[1].split(' --> ')
                    start_time = self._parse_timestamp(timing[0])
                    end_time = self._parse_timestamp(timing[1])
                    
                    # Get text (may be multiple lines)
                    text = '\n'.join(lines[2:])
                    
                    subtitles.append({
                        'start': start_time,
                        'end': end_time,
                        'text': text
                    })
                except (IndexError, ValueError) as e:
                    logger.warning(f"Failed to parse subtitle block: {e}")
                    continue
        
        return subtitles

    def _parse_timestamp(self, timestamp: str) -> float:
        """Parse SRT timestamp to seconds"""
        try:
            # Format: HH:MM:SS,mmm or HH:MM:SS.mmm
            timestamp = timestamp.replace(',', '.')
            parts = timestamp.split(':')
            
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            
            return hours * 3600 + minutes * 60 + seconds
        except (IndexError, ValueError):
            return 0.0

    def merge_subtitles(
        self,
        subtitle_paths: List[str],
        output_path: Optional[str] = None
    ) -> str:
        """
        Merge multiple subtitle files
        
        Args:
            subtitle_paths: List of subtitle file paths
            output_path: Optional output path
        
        Returns:
            Path to merged subtitle file
        """
        logger.info(f"Merging {len(subtitle_paths)} subtitle files")
        
        all_subtitles = []
        
        for path in subtitle_paths:
            if os.path.exists(path):
                subs = self._parse_srt(path)
                all_subtitles.extend(subs)
        
        # Sort by start time
        all_subtitles.sort(key=lambda x: x['start'])
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(
                self.output_dir,
                f"merged_{timestamp}.srt"
            )
        
        return self.create_srt(all_subtitles, output_path)


def main():
    """Example usage"""
    config = {
        'subtitles': {'output_directory': 'output/subtitles'},
        'workflow': {'temp_directory': 'temp'}
    }
    
    agent = SubtitleAgent(config)
    
    print("Subtitle Generation Agent - Ready")
    print("\nAvailable methods:")
    print("  - generate_subtitles_from_audio(video_path)")
    print("  - create_srt(subtitles)")
    print("  - create_vtt(subtitles)")
    print("  - burn_subtitles(video, subtitle)")
    print("  - add_soft_subtitles(video, subtitle)")
    print("  - translate_subtitles(subtitle, language)")
    print("  - sync_subtitles(subtitle, offset)")
    print("  - merge_subtitles(subtitle_list)")


if __name__ == '__main__':
    main()
