"""
Audio Processing and Enhancement Agent

Specialized agent for audio processing, enhancement, and synchronization.
Based on industry best practices for audio automation.
"""

import os
import logging
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioProcessingAgent:
    """Agent for audio processing and enhancement"""

    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = config.get('audio', {}).get('output_directory', 'output/audio')
        self.temp_dir = config.get('workflow', {}).get('temp_directory', 'temp')
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def extract_audio(self, video_path: str, output_format: str = 'mp3') -> str:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to video file
            output_format: Audio format (mp3, wav, aac, flac)
        
        Returns:
            Path to extracted audio file
        """
        logger.info(f"Extracting audio from: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"extracted_audio_{timestamp}.{output_format}"
        )
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', self._get_audio_codec(output_format),
            '-ab', '192k',  # Audio bitrate
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Stereo
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                timeout=300
            )
            logger.info(f"Audio extracted: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting audio: {e.stderr.decode()}")
            raise
        except subprocess.TimeoutExpired:
            logger.error("Audio extraction timed out")
            raise

    def _get_audio_codec(self, format: str) -> str:
        """Get appropriate audio codec for format"""
        codecs = {
            'mp3': 'libmp3lame',
            'wav': 'pcm_s16le',
            'aac': 'aac',
            'flac': 'flac',
            'ogg': 'libvorbis'
        }
        return codecs.get(format, 'libmp3lame')

    def normalize_audio(self, audio_path: str, target_level: float = -16.0) -> str:
        """
        Normalize audio levels using loudness normalization
        
        Args:
            audio_path: Path to audio file
            target_level: Target LUFS level (default: -16.0 for streaming)
        
        Returns:
            Path to normalized audio file
        """
        logger.info(f"Normalizing audio: {audio_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"normalized_{timestamp}_{os.path.basename(audio_path)}"
        )
        
        # Two-pass loudness normalization
        cmd = [
            'ffmpeg',
            '-i', audio_path,
            '-af', f'loudnorm=I={target_level}:TP=-1.5:LRA=11',
            '-ar', '44100',
            '-y',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            logger.info(f"Audio normalized: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error normalizing audio: {e.stderr.decode()}")
            raise

    def remove_noise(self, audio_path: str, noise_reduction: int = 10) -> str:
        """
        Remove background noise from audio
        
        Args:
            audio_path: Path to audio file
            noise_reduction: Noise reduction amount (1-100)
        
        Returns:
            Path to cleaned audio file
        """
        logger.info(f"Removing noise from: {audio_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"cleaned_{timestamp}_{os.path.basename(audio_path)}"
        )
        
        # Use highpass and lowpass filters for noise reduction
        cmd = [
            'ffmpeg',
            '-i', audio_path,
            '-af', f'highpass=f=200,lowpass=f=3000,afftdn=nr={noise_reduction}',
            '-y',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            logger.info(f"Noise removed: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error removing noise: {e.stderr.decode()}")
            raise

    def mix_audio_tracks(
        self,
        tracks: List[Tuple[str, float]],
        output_path: Optional[str] = None
    ) -> str:
        """
        Mix multiple audio tracks with volume controls
        
        Args:
            tracks: List of (audio_path, volume_level) tuples
            output_path: Optional output path
        
        Returns:
            Path to mixed audio file
        """
        logger.info(f"Mixing {len(tracks)} audio tracks")
        
        if not tracks:
            raise ValueError("No audio tracks provided")
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(
                self.output_dir,
                f"mixed_{timestamp}.mp3"
            )
        
        # Build filter complex for mixing
        inputs = []
        filter_parts = []
        
        for i, (track_path, volume) in enumerate(tracks):
            inputs.extend(['-i', track_path])
            filter_parts.append(f'[{i}:a]volume={volume}[a{i}]')
        
        # Combine all tracks
        mix_inputs = ''.join([f'[a{i}]' for i in range(len(tracks))])
        filter_complex = ';'.join(filter_parts) + f';{mix_inputs}amix=inputs={len(tracks)}:duration=longest[out]'
        
        cmd = [
            'ffmpeg',
            *inputs,
            '-filter_complex', filter_complex,
            '-map', '[out]',
            '-ac', '2',
            '-y',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            logger.info(f"Audio mixed: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error mixing audio: {e.stderr.decode()}")
            raise

    def analyze_audio(self, audio_path: str) -> Dict:
        """
        Analyze audio file for technical properties and quality metrics
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary with audio analysis data
        """
        logger.info(f"Analyzing audio: {audio_path}")
        
        try:
            # Get basic info
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            audio_stream = next(
                (s for s in data.get('streams', []) if s['codec_type'] == 'audio'),
                {}
            )
            
            # Get loudness stats
            loudness_cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-af', 'loudnorm=print_format=json',
                '-f', 'null',
                '-'
            ]
            
            loudness_result = subprocess.run(
                loudness_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse loudness from stderr
            loudness_data = self._parse_loudness_stats(loudness_result.stderr)
            
            analysis = {
                'codec': audio_stream.get('codec_name', 'unknown'),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'bitrate': int(audio_stream.get('bit_rate', 0)),
                'duration': float(data.get('format', {}).get('duration', 0)),
                'loudness': loudness_data,
                'quality_score': self._calculate_audio_quality(audio_stream, loudness_data)
            }
            
            logger.info(f"Audio analysis complete")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            return {}

    def _parse_loudness_stats(self, stderr: str) -> Dict:
        """Parse loudness stats from ffmpeg output"""
        try:
            # Look for JSON block in stderr
            json_start = stderr.rfind('{')
            json_end = stderr.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = stderr[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Could not parse loudness stats: {e}")
        
        return {}

    def _calculate_audio_quality(self, stream: Dict, loudness: Dict) -> str:
        """Calculate overall audio quality score"""
        score = 0
        
        # Check sample rate
        sample_rate = int(stream.get('sample_rate', 0))
        if sample_rate >= 44100:
            score += 3
        elif sample_rate >= 22050:
            score += 2
        else:
            score += 1
        
        # Check bitrate
        bitrate = int(stream.get('bit_rate', 0))
        if bitrate >= 256000:
            score += 3
        elif bitrate >= 128000:
            score += 2
        else:
            score += 1
        
        # Check loudness
        input_i = loudness.get('input_i', -100)
        if -20 <= float(input_i) <= -10:
            score += 2
        elif -25 <= float(input_i) <= -5:
            score += 1
        
        if score >= 7:
            return 'Excellent'
        elif score >= 5:
            return 'Good'
        elif score >= 3:
            return 'Fair'
        else:
            return 'Poor'

    def add_fade(
        self,
        audio_path: str,
        fade_in: float = 0,
        fade_out: float = 0
    ) -> str:
        """
        Add fade in/out effects to audio
        
        Args:
            audio_path: Path to audio file
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds
        
        Returns:
            Path to processed audio file
        """
        logger.info(f"Adding fade effects: in={fade_in}s, out={fade_out}s")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"faded_{timestamp}_{os.path.basename(audio_path)}"
        )
        
        # Build filter
        filters = []
        if fade_in > 0:
            filters.append(f'afade=t=in:st=0:d={fade_in}')
        if fade_out > 0:
            # Get duration first
            duration = self._get_audio_duration(audio_path)
            start_time = duration - fade_out
            filters.append(f'afade=t=out:st={start_time}:d={fade_out}')
        
        if not filters:
            logger.warning("No fade effects specified")
            return audio_path
        
        filter_str = ','.join(filters)
        
        cmd = [
            'ffmpeg',
            '-i', audio_path,
            '-af', filter_str,
            '-y',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            logger.info(f"Fade effects added: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error adding fade: {e.stderr.decode()}")
            raise

    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    def convert_format(
        self,
        audio_path: str,
        output_format: str,
        quality: str = 'high'
    ) -> str:
        """
        Convert audio to different format with quality presets
        
        Args:
            audio_path: Path to audio file
            output_format: Target format (mp3, wav, aac, flac, ogg)
            quality: Quality preset (low, medium, high, lossless)
        
        Returns:
            Path to converted audio file
        """
        logger.info(f"Converting audio to {output_format} ({quality} quality)")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"converted_{timestamp}.{output_format}"
        )
        
        # Quality presets
        quality_settings = {
            'low': {'bitrate': '96k', 'sample_rate': '22050'},
            'medium': {'bitrate': '128k', 'sample_rate': '44100'},
            'high': {'bitrate': '320k', 'sample_rate': '48000'},
            'lossless': {'bitrate': None, 'sample_rate': '48000'}
        }
        
        settings = quality_settings.get(quality, quality_settings['high'])
        
        cmd = [
            'ffmpeg',
            '-i', audio_path,
            '-acodec', self._get_audio_codec(output_format),
            '-ar', settings['sample_rate']
        ]
        
        if settings['bitrate'] and output_format != 'flac':
            cmd.extend(['-ab', settings['bitrate']])
        
        cmd.extend(['-y', output_path])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            logger.info(f"Audio converted: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error converting audio: {e.stderr.decode()}")
            raise


def main():
    """Example usage"""
    config = {
        'audio': {'output_directory': 'output/audio'},
        'workflow': {'temp_directory': 'temp'}
    }
    
    agent = AudioProcessingAgent(config)
    
    print("Audio Processing Agent - Ready")
    print("\nAvailable methods:")
    print("  - extract_audio(video_path)")
    print("  - normalize_audio(audio_path)")
    print("  - remove_noise(audio_path)")
    print("  - mix_audio_tracks(tracks)")
    print("  - analyze_audio(audio_path)")
    print("  - add_fade(audio_path, fade_in, fade_out)")
    print("  - convert_format(audio_path, format, quality)")


if __name__ == '__main__':
    main()
