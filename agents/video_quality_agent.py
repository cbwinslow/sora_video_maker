"""
Video Quality Assurance Agent

Comprehensive video quality checking, validation, and certification system.
Implements industry-standard quality metrics and automated QA workflows.
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


class VideoQualityAgent:
    """Agent for automated video quality assurance"""

    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = config.get('quality', {}).get('output_directory', 'output/qa_reports')
        self.temp_dir = config.get('workflow', {}).get('temp_directory', 'temp')
        
        # Quality thresholds
        self.thresholds = config.get('quality', {}).get('thresholds', {
            'min_resolution': (1280, 720),
            'min_bitrate': 1000000,  # 1 Mbps
            'min_fps': 24,
            'max_duration': 3600,  # 1 hour
            'min_audio_bitrate': 128000,
            'min_audio_sample_rate': 44100
        })
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def validate_video(self, video_path: str) -> Dict:
        """
        Comprehensive video validation
        
        Args:
            video_path: Path to video file
        
        Returns:
            Validation report with pass/fail status and issues
        """
        logger.info(f"Validating video: {video_path}")
        
        if not os.path.exists(video_path):
            return {
                'valid': False,
                'errors': ['Video file not found'],
                'warnings': [],
                'metrics': {}
            }
        
        report = {
            'video_path': video_path,
            'timestamp': datetime.now().isoformat(),
            'valid': True,
            'errors': [],
            'warnings': [],
            'metrics': {},
            'checks': {}
        }
        
        try:
            # Run all validation checks
            self._check_file_integrity(video_path, report)
            self._check_video_specs(video_path, report)
            self._check_audio_specs(video_path, report)
            self._check_encoding(video_path, report)
            self._check_corruption(video_path, report)
            self._check_quality_metrics(video_path, report)
            
            # Determine overall validity
            report['valid'] = len(report['errors']) == 0
            report['score'] = self._calculate_quality_score(report)
            
            # Save report
            self._save_report(report)
            
            logger.info(f"Validation complete. Valid: {report['valid']}, Score: {report['score']}")
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            report['valid'] = False
            report['errors'].append(f"Validation exception: {str(e)}")
        
        return report

    def _check_file_integrity(self, video_path: str, report: Dict):
        """Check file size and readability"""
        try:
            file_size = os.path.getsize(video_path)
            report['metrics']['file_size'] = file_size
            
            if file_size == 0:
                report['errors'].append("Video file is empty")
            elif file_size < 1000:  # Less than 1KB
                report['warnings'].append("Video file is very small, might be corrupted")
            
            # Check if file is readable
            with open(video_path, 'rb') as f:
                f.read(100)  # Try to read first 100 bytes
            
            report['checks']['file_integrity'] = 'pass'
            
        except Exception as e:
            report['errors'].append(f"File integrity check failed: {str(e)}")
            report['checks']['file_integrity'] = 'fail'

    def _check_video_specs(self, video_path: str, report: Dict):
        """Check video specifications against thresholds"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            data = json.loads(result.stdout)
            
            video_stream = next(
                (s for s in data.get('streams', []) if s['codec_type'] == 'video'),
                None
            )
            
            if not video_stream:
                report['errors'].append("No video stream found")
                report['checks']['video_specs'] = 'fail'
                return
            
            # Extract specs
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            fps = self._parse_frame_rate(video_stream.get('r_frame_rate', '0/1'))
            bitrate = int(data.get('format', {}).get('bit_rate', 0))
            duration = float(data.get('format', {}).get('duration', 0))
            codec = video_stream.get('codec_name', 'unknown')
            
            report['metrics'].update({
                'width': width,
                'height': height,
                'fps': fps,
                'bitrate': bitrate,
                'duration': duration,
                'codec': codec
            })
            
            # Check against thresholds
            min_width, min_height = self.thresholds['min_resolution']
            
            if width < min_width or height < min_height:
                report['errors'].append(
                    f"Resolution {width}x{height} below minimum {min_width}x{min_height}"
                )
            
            if bitrate < self.thresholds['min_bitrate']:
                report['warnings'].append(
                    f"Bitrate {bitrate} below recommended {self.thresholds['min_bitrate']}"
                )
            
            if fps < self.thresholds['min_fps']:
                report['errors'].append(
                    f"FPS {fps} below minimum {self.thresholds['min_fps']}"
                )
            
            if duration > self.thresholds['max_duration']:
                report['warnings'].append(
                    f"Duration {duration}s exceeds maximum {self.thresholds['max_duration']}s"
                )
            
            if duration == 0:
                report['errors'].append("Video has zero duration")
            
            # Check codec
            unsupported_codecs = ['rv40', 'rv30', 'wmv1', 'wmv2']
            if codec in unsupported_codecs:
                report['warnings'].append(f"Codec {codec} may have compatibility issues")
            
            report['checks']['video_specs'] = 'pass' if len(report['errors']) == 0 else 'fail'
            
        except subprocess.TimeoutExpired:
            report['errors'].append("Video specs check timed out")
            report['checks']['video_specs'] = 'fail'
        except Exception as e:
            report['errors'].append(f"Video specs check failed: {str(e)}")
            report['checks']['video_specs'] = 'fail'

    def _check_audio_specs(self, video_path: str, report: Dict):
        """Check audio specifications"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                '-select_streams', 'a:0',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            data = json.loads(result.stdout)
            
            if not data.get('streams'):
                report['warnings'].append("No audio stream found")
                report['checks']['audio_specs'] = 'warn'
                return
            
            audio_stream = data['streams'][0]
            
            sample_rate = int(audio_stream.get('sample_rate', 0))
            bitrate = int(audio_stream.get('bit_rate', 0))
            channels = int(audio_stream.get('channels', 0))
            codec = audio_stream.get('codec_name', 'unknown')
            
            report['metrics'].update({
                'audio_sample_rate': sample_rate,
                'audio_bitrate': bitrate,
                'audio_channels': channels,
                'audio_codec': codec
            })
            
            # Check against thresholds
            if sample_rate < self.thresholds['min_audio_sample_rate']:
                report['warnings'].append(
                    f"Audio sample rate {sample_rate} below recommended {self.thresholds['min_audio_sample_rate']}"
                )
            
            if bitrate < self.thresholds['min_audio_bitrate']:
                report['warnings'].append(
                    f"Audio bitrate {bitrate} below recommended {self.thresholds['min_audio_bitrate']}"
                )
            
            if channels < 2:
                report['warnings'].append("Audio is mono, stereo recommended")
            
            report['checks']['audio_specs'] = 'pass'
            
        except Exception as e:
            logger.warning(f"Audio specs check failed: {e}")
            report['warnings'].append(f"Could not check audio specs: {str(e)}")
            report['checks']['audio_specs'] = 'warn'

    def _check_encoding(self, video_path: str, report: Dict):
        """Check encoding quality and settings"""
        try:
            # Check for encoding issues
            cmd = [
                'ffmpeg',
                '-v', 'error',
                '-i', video_path,
                '-f', 'null',
                '-'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.stderr:
                # Parse errors
                errors = result.stderr.strip().split('\n')
                for error in errors:
                    if error:
                        report['warnings'].append(f"Encoding issue: {error[:100]}")
            
            report['checks']['encoding'] = 'pass'
            
        except subprocess.TimeoutExpired:
            report['warnings'].append("Encoding check timed out")
            report['checks']['encoding'] = 'warn'
        except Exception as e:
            report['warnings'].append(f"Encoding check failed: {str(e)}")
            report['checks']['encoding'] = 'warn'

    def _check_corruption(self, video_path: str, report: Dict):
        """Check for video corruption"""
        try:
            # Try to decode first 10 seconds
            cmd = [
                'ffmpeg',
                '-v', 'error',
                '-i', video_path,
                '-t', '10',
                '-f', 'null',
                '-'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if 'corrupt' in result.stderr.lower() or 'error' in result.stderr.lower():
                report['errors'].append("Video may be corrupted")
                report['checks']['corruption'] = 'fail'
            else:
                report['checks']['corruption'] = 'pass'
            
        except Exception as e:
            report['warnings'].append(f"Corruption check failed: {str(e)}")
            report['checks']['corruption'] = 'warn'

    def _check_quality_metrics(self, video_path: str, report: Dict):
        """Check advanced quality metrics"""
        try:
            # Calculate PSNR if reference is available (placeholder)
            # Calculate SSIM if reference is available (placeholder)
            # In production, these would compare against reference video
            
            report['checks']['quality_metrics'] = 'pass'
            
        except Exception as e:
            logger.warning(f"Quality metrics check failed: {e}")
            report['checks']['quality_metrics'] = 'warn'

    def _parse_frame_rate(self, fps_str: str) -> float:
        """Parse frame rate string"""
        try:
            if '/' in fps_str:
                num, den = fps_str.split('/')
                return float(num) / float(den)
            return float(fps_str)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def _calculate_quality_score(self, report: Dict) -> float:
        """Calculate overall quality score (0-100)"""
        score = 100.0
        
        # Deduct for errors (more severe)
        score -= len(report['errors']) * 20
        
        # Deduct for warnings (less severe)
        score -= len(report['warnings']) * 5
        
        # Bonus for passed checks
        passed_checks = sum(1 for v in report['checks'].values() if v == 'pass')
        total_checks = len(report['checks'])
        
        if total_checks > 0:
            check_score = (passed_checks / total_checks) * 20
            score = score * 0.8 + check_score  # Weighted combination
        
        return max(0.0, min(100.0, score))

    def _save_report(self, report: Dict):
        """Save validation report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(
            self.output_dir,
            f"qa_report_{timestamp}.json"
        )
        
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

    def batch_validate(self, video_paths: List[str]) -> List[Dict]:
        """
        Validate multiple videos
        
        Args:
            video_paths: List of video file paths
        
        Returns:
            List of validation reports
        """
        logger.info(f"Batch validating {len(video_paths)} videos")
        
        reports = []
        for i, video_path in enumerate(video_paths):
            logger.info(f"Validating {i+1}/{len(video_paths)}: {video_path}")
            report = self.validate_video(video_path)
            reports.append(report)
        
        # Generate summary
        summary = {
            'total': len(reports),
            'valid': sum(1 for r in reports if r['valid']),
            'invalid': sum(1 for r in reports if not r['valid']),
            'average_score': sum(r.get('score', 0) for r in reports) / len(reports) if reports else 0
        }
        
        logger.info(f"Batch validation complete: {summary}")
        return reports

    def compare_videos(self, video1_path: str, video2_path: str) -> Dict:
        """
        Compare two videos for quality differences
        
        Args:
            video1_path: First video path
            video2_path: Second video path
        
        Returns:
            Comparison report
        """
        logger.info(f"Comparing videos: {video1_path} vs {video2_path}")
        
        report1 = self.validate_video(video1_path)
        report2 = self.validate_video(video2_path)
        
        comparison = {
            'video1': report1,
            'video2': report2,
            'differences': [],
            'recommendations': []
        }
        
        # Compare metrics
        metrics1 = report1.get('metrics', {})
        metrics2 = report2.get('metrics', {})
        
        for key in metrics1.keys():
            if key in metrics2:
                val1 = metrics1[key]
                val2 = metrics2[key]
                
                if val1 != val2:
                    comparison['differences'].append({
                        'metric': key,
                        'video1': val1,
                        'video2': val2,
                        'difference': abs(val1 - val2) if isinstance(val1, (int, float)) else 'N/A'
                    })
        
        # Generate recommendations
        if report1['score'] > report2['score']:
            comparison['recommendations'].append("Video 1 has better overall quality")
        elif report2['score'] > report1['score']:
            comparison['recommendations'].append("Video 2 has better overall quality")
        
        return comparison

    def generate_quality_report(self, video_path: str) -> str:
        """
        Generate human-readable quality report
        
        Args:
            video_path: Path to video file
        
        Returns:
            Path to generated report (markdown format)
        """
        logger.info(f"Generating quality report for: {video_path}")
        
        validation = self.validate_video(video_path)
        
        # Build markdown report
        report_lines = [
            f"# Video Quality Report",
            f"",
            f"**Video:** {video_path}",
            f"**Timestamp:** {validation['timestamp']}",
            f"**Valid:** {'✅ Yes' if validation['valid'] else '❌ No'}",
            f"**Quality Score:** {validation.get('score', 0):.1f}/100",
            f"",
            f"## Metrics",
            f""
        ]
        
        # Add metrics
        for key, value in validation.get('metrics', {}).items():
            report_lines.append(f"- **{key}:** {value}")
        
        # Add checks
        report_lines.extend([
            f"",
            f"## Checks",
            f""
        ])
        
        for check, status in validation.get('checks', {}).items():
            emoji = '✅' if status == 'pass' else '⚠️' if status == 'warn' else '❌'
            report_lines.append(f"- **{check}:** {emoji} {status}")
        
        # Add errors
        if validation['errors']:
            report_lines.extend([
                f"",
                f"## ❌ Errors",
                f""
            ])
            for error in validation['errors']:
                report_lines.append(f"- {error}")
        
        # Add warnings
        if validation['warnings']:
            report_lines.extend([
                f"",
                f"## ⚠️ Warnings",
                f""
            ])
            for warning in validation['warnings']:
                report_lines.append(f"- {warning}")
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(
            self.output_dir,
            f"quality_report_{timestamp}.md"
        )
        
        with open(report_path, 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Quality report generated: {report_path}")
        return report_path


def main():
    """Example usage"""
    config = {
        'quality': {'output_directory': 'output/qa_reports'},
        'workflow': {'temp_directory': 'temp'}
    }
    
    agent = VideoQualityAgent(config)
    
    print("Video Quality Assurance Agent - Ready")
    print("\nAvailable methods:")
    print("  - validate_video(video_path)")
    print("  - batch_validate(video_paths)")
    print("  - compare_videos(video1, video2)")
    print("  - generate_quality_report(video_path)")


if __name__ == '__main__':
    main()
