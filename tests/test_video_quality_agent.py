"""
Comprehensive tests for Video Quality Agent

Implements AAA pattern and achieves high test coverage.
"""

import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from agents.video_quality_agent import VideoQualityAgent


@pytest.fixture
def config():
    """Test configuration"""
    return {
        'quality': {'output_directory': 'test_output/qa_reports'},
        'workflow': {'temp_directory': 'test_temp'}
    }


@pytest.fixture
def quality_agent(config):
    """Create VideoQualityAgent instance"""
    return VideoQualityAgent(config)


@pytest.fixture
def sample_ffprobe_data():
    """Sample ffprobe output"""
    return {
        'format': {
            'duration': '60.0',
            'size': '10000000',
            'bit_rate': '1500000',
            'format_name': 'mp4'
        },
        'streams': [
            {
                'codec_type': 'video',
                'codec_name': 'h264',
                'width': 1920,
                'height': 1080,
                'r_frame_rate': '30/1',
                'bit_rate': '1000000'
            },
            {
                'codec_type': 'audio',
                'codec_name': 'aac',
                'sample_rate': '44100',
                'channels': '2',
                'bit_rate': '192000'
            }
        ]
    }


class TestVideoQualityAgent:
    """Test suite for VideoQualityAgent"""
    
    # === Initialization Tests ===
    
    def test_init(self, quality_agent, config):
        """Test agent initialization"""
        # Assert
        assert quality_agent.config == config
        assert quality_agent.output_dir == config['quality']['output_directory']
        assert 'min_resolution' in quality_agent.thresholds
    
    def test_init_with_custom_thresholds(self, tmp_path):
        """Test initialization with custom thresholds"""
        # Arrange
        custom_config = {
            'quality': {
                'output_directory': str(tmp_path / 'qa'),
                'thresholds': {
                    'min_resolution': (1920, 1080),
                    'min_bitrate': 2000000
                }
            },
            'workflow': {'temp_directory': str(tmp_path / 'temp')}
        }
        
        # Act
        agent = VideoQualityAgent(custom_config)
        
        # Assert
        assert agent.thresholds['min_resolution'] == (1920, 1080)
        assert agent.thresholds['min_bitrate'] == 2000000
    
    # === File Integrity Tests ===
    
    def test_check_file_integrity_success(self, quality_agent, tmp_path):
        """Test successful file integrity check"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        with open(video_path, 'wb') as f:
            f.write(b'x' * 10000)  # Write some data
        
        report = {'metrics': {}, 'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_file_integrity(video_path, report)
        
        # Assert
        assert report['checks']['file_integrity'] == 'pass'
        assert report['metrics']['file_size'] == 10000
        assert len(report['errors']) == 0
    
    def test_check_file_integrity_empty_file(self, quality_agent, tmp_path):
        """Test file integrity check with empty file"""
        # Arrange
        video_path = str(tmp_path / 'empty.mp4')
        open(video_path, 'w').close()
        
        report = {'metrics': {}, 'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_file_integrity(video_path, report)
        
        # Assert
        assert report['checks']['file_integrity'] == 'pass'
        assert 'Video file is empty' in report['errors']
    
    def test_check_file_integrity_small_file(self, quality_agent, tmp_path):
        """Test file integrity check with very small file"""
        # Arrange
        video_path = str(tmp_path / 'small.mp4')
        with open(video_path, 'wb') as f:
            f.write(b'x' * 500)
        
        report = {'metrics': {}, 'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_file_integrity(video_path, report)
        
        # Assert
        assert 'very small' in ' '.join(report['warnings']).lower()
    
    # === Video Specs Tests ===
    
    @patch('subprocess.run')
    def test_check_video_specs_success(self, mock_run, quality_agent, tmp_path, sample_ffprobe_data):
        """Test successful video specs check"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        open(video_path, 'w').close()
        
        mock_run.return_value = Mock(
            stdout=json.dumps(sample_ffprobe_data),
            returncode=0
        )
        
        report = {'metrics': {}, 'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_video_specs(video_path, report)
        
        # Assert
        assert report['checks']['video_specs'] == 'pass'
        assert report['metrics']['width'] == 1920
        assert report['metrics']['height'] == 1080
        assert report['metrics']['fps'] == 30.0
    
    @patch('subprocess.run')
    def test_check_video_specs_low_resolution(self, mock_run, quality_agent, tmp_path):
        """Test video specs check with low resolution"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        open(video_path, 'w').close()
        
        low_res_data = {
            'format': {'duration': '60.0', 'bit_rate': '1000000'},
            'streams': [{
                'codec_type': 'video',
                'codec_name': 'h264',
                'width': 640,
                'height': 480,
                'r_frame_rate': '30/1'
            }]
        }
        
        mock_run.return_value = Mock(
            stdout=json.dumps(low_res_data),
            returncode=0
        )
        
        report = {'metrics': {}, 'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_video_specs(video_path, report)
        
        # Assert
        assert 'Resolution' in ' '.join(report['errors'])
    
    @patch('subprocess.run')
    def test_check_video_specs_low_fps(self, mock_run, quality_agent, tmp_path):
        """Test video specs check with low FPS"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        open(video_path, 'w').close()
        
        low_fps_data = {
            'format': {'duration': '60.0', 'bit_rate': '1000000'},
            'streams': [{
                'codec_type': 'video',
                'codec_name': 'h264',
                'width': 1920,
                'height': 1080,
                'r_frame_rate': '15/1'
            }]
        }
        
        mock_run.return_value = Mock(
            stdout=json.dumps(low_fps_data),
            returncode=0
        )
        
        report = {'metrics': {}, 'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_video_specs(video_path, report)
        
        # Assert
        assert any('FPS' in error for error in report['errors'])
    
    @patch('subprocess.run')
    def test_check_video_specs_no_video_stream(self, mock_run, quality_agent, tmp_path):
        """Test video specs check with no video stream"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        open(video_path, 'w').close()
        
        no_video_data = {
            'format': {'duration': '60.0'},
            'streams': []
        }
        
        mock_run.return_value = Mock(
            stdout=json.dumps(no_video_data),
            returncode=0
        )
        
        report = {'metrics': {}, 'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_video_specs(video_path, report)
        
        # Assert
        assert report['checks']['video_specs'] == 'fail'
        assert 'No video stream found' in report['errors']
    
    # === Audio Specs Tests ===
    
    @patch('subprocess.run')
    def test_check_audio_specs_success(self, mock_run, quality_agent, tmp_path):
        """Test successful audio specs check"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        open(video_path, 'w').close()
        
        audio_data = {
            'streams': [{
                'codec_name': 'aac',
                'sample_rate': '44100',
                'channels': '2',
                'bit_rate': '192000'
            }]
        }
        
        mock_run.return_value = Mock(
            stdout=json.dumps(audio_data),
            returncode=0
        )
        
        report = {'metrics': {}, 'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_audio_specs(video_path, report)
        
        # Assert
        assert report['checks']['audio_specs'] == 'pass'
        assert report['metrics']['audio_sample_rate'] == 44100
        assert report['metrics']['audio_channels'] == 2
    
    @patch('subprocess.run')
    def test_check_audio_specs_no_audio(self, mock_run, quality_agent, tmp_path):
        """Test audio specs check with no audio stream"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        open(video_path, 'w').close()
        
        mock_run.return_value = Mock(
            stdout=json.dumps({'streams': []}),
            returncode=0
        )
        
        report = {'metrics': {}, 'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_audio_specs(video_path, report)
        
        # Assert
        assert report['checks']['audio_specs'] == 'warn'
        assert any('No audio stream' in warning for warning in report['warnings'])
    
    @patch('subprocess.run')
    def test_check_audio_specs_mono(self, mock_run, quality_agent, tmp_path):
        """Test audio specs check with mono audio"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        open(video_path, 'w').close()
        
        mono_data = {
            'streams': [{
                'codec_name': 'aac',
                'sample_rate': '44100',
                'channels': '1',
                'bit_rate': '128000'
            }]
        }
        
        mock_run.return_value = Mock(
            stdout=json.dumps(mono_data),
            returncode=0
        )
        
        report = {'metrics': {}, 'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_audio_specs(video_path, report)
        
        # Assert
        assert any('mono' in warning.lower() for warning in report['warnings'])
    
    # === Validation Tests ===
    
    def test_validate_video_file_not_found(self, quality_agent):
        """Test validation with non-existent file"""
        # Act
        report = quality_agent.validate_video('/nonexistent/video.mp4')
        
        # Assert
        assert report['valid'] is False
        assert 'Video file not found' in report['errors']
    
    @patch('subprocess.run')
    @patch('os.path.getsize')
    def test_validate_video_success(self, mock_getsize, mock_run, quality_agent, tmp_path, sample_ffprobe_data):
        """Test successful video validation"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        with open(video_path, 'wb') as f:
            f.write(b'x' * 10000)
        
        mock_getsize.return_value = 10000
        mock_run.return_value = Mock(
            stdout=json.dumps(sample_ffprobe_data),
            stderr='',
            returncode=0
        )
        
        # Act
        report = quality_agent.validate_video(video_path)
        
        # Assert
        assert report is not None
        assert 'valid' in report
        assert 'score' in report
        assert 'metrics' in report
    
    # === Quality Score Tests ===
    
    def test_calculate_quality_score_perfect(self, quality_agent):
        """Test quality score calculation for perfect video"""
        # Arrange
        report = {
            'errors': [],
            'warnings': [],
            'checks': {
                'file_integrity': 'pass',
                'video_specs': 'pass',
                'audio_specs': 'pass',
                'encoding': 'pass',
                'corruption': 'pass'
            }
        }
        
        # Act
        score = quality_agent._calculate_quality_score(report)
        
        # Assert
        assert score == 100.0
    
    def test_calculate_quality_score_with_errors(self, quality_agent):
        """Test quality score calculation with errors"""
        # Arrange
        report = {
            'errors': ['Error 1', 'Error 2'],
            'warnings': [],
            'checks': {
                'file_integrity': 'pass',
                'video_specs': 'fail'
            }
        }
        
        # Act
        score = quality_agent._calculate_quality_score(report)
        
        # Assert
        assert score < 100.0
    
    def test_calculate_quality_score_with_warnings(self, quality_agent):
        """Test quality score calculation with warnings"""
        # Arrange
        report = {
            'errors': [],
            'warnings': ['Warning 1', 'Warning 2', 'Warning 3'],
            'checks': {
                'file_integrity': 'pass',
                'video_specs': 'pass'
            }
        }
        
        # Act
        score = quality_agent._calculate_quality_score(report)
        
        # Assert
        assert 50 < score < 100
    
    # === Frame Rate Parsing Tests ===
    
    @pytest.mark.parametrize("fps_str,expected", [
        ('30/1', 30.0),
        ('60/1', 60.0),
        ('24000/1001', 23.976),
        ('25', 25.0),
        ('invalid', 0.0),
        ('30/0', 0.0),
    ])
    def test_parse_frame_rate(self, quality_agent, fps_str, expected):
        """Test frame rate parsing"""
        # Act
        result = quality_agent._parse_frame_rate(fps_str)
        
        # Assert
        if expected == 23.976:
            assert abs(result - expected) < 0.01
        else:
            assert result == expected
    
    # === Batch Validation Tests ===
    
    @patch.object(VideoQualityAgent, 'validate_video')
    def test_batch_validate_success(self, mock_validate, quality_agent):
        """Test successful batch validation"""
        # Arrange
        video_paths = ['video1.mp4', 'video2.mp4', 'video3.mp4']
        mock_validate.side_effect = [
            {'valid': True, 'score': 90},
            {'valid': True, 'score': 85},
            {'valid': False, 'score': 50}
        ]
        
        # Act
        reports = quality_agent.batch_validate(video_paths)
        
        # Assert
        assert len(reports) == 3
        assert mock_validate.call_count == 3
    
    @patch.object(VideoQualityAgent, 'validate_video')
    def test_batch_validate_empty_list(self, mock_validate, quality_agent):
        """Test batch validation with empty list"""
        # Act
        reports = quality_agent.batch_validate([])
        
        # Assert
        assert reports == []
        assert mock_validate.call_count == 0
    
    # === Video Comparison Tests ===
    
    @patch.object(VideoQualityAgent, 'validate_video')
    def test_compare_videos(self, mock_validate, quality_agent):
        """Test video comparison"""
        # Arrange
        mock_validate.side_effect = [
            {
                'valid': True,
                'score': 90,
                'metrics': {'width': 1920, 'height': 1080, 'fps': 30}
            },
            {
                'valid': True,
                'score': 85,
                'metrics': {'width': 1280, 'height': 720, 'fps': 24}
            }
        ]
        
        # Act
        comparison = quality_agent.compare_videos('video1.mp4', 'video2.mp4')
        
        # Assert
        assert 'video1' in comparison
        assert 'video2' in comparison
        assert 'differences' in comparison
        assert len(comparison['differences']) > 0
    
    # === Report Generation Tests ===
    
    @patch.object(VideoQualityAgent, 'validate_video')
    def test_generate_quality_report(self, mock_validate, quality_agent, tmp_path):
        """Test quality report generation"""
        # Arrange
        video_path = 'test.mp4'
        mock_validate.return_value = {
            'timestamp': '2024-01-01T00:00:00',
            'valid': True,
            'score': 90,
            'metrics': {'width': 1920, 'height': 1080},
            'checks': {'file_integrity': 'pass'},
            'errors': [],
            'warnings': ['Minor warning']
        }
        
        # Act
        report_path = quality_agent.generate_quality_report(video_path)
        
        # Assert
        assert report_path is not None
        assert report_path.endswith('.md')
        assert os.path.exists(report_path)
    
    # === Encoding Check Tests ===
    
    @patch('subprocess.run')
    def test_check_encoding_success(self, mock_run, quality_agent, tmp_path):
        """Test successful encoding check"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        open(video_path, 'w').close()
        mock_run.return_value = Mock(stderr='', returncode=0)
        
        report = {'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_encoding(video_path, report)
        
        # Assert
        assert report['checks']['encoding'] == 'pass'
    
    @patch('subprocess.run')
    def test_check_encoding_with_warnings(self, mock_run, quality_agent, tmp_path):
        """Test encoding check with warnings"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        open(video_path, 'w').close()
        mock_run.return_value = Mock(
            stderr='[warning] Some encoding issue\n',
            returncode=0
        )
        
        report = {'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_encoding(video_path, report)
        
        # Assert
        assert len(report['warnings']) > 0
    
    # === Corruption Check Tests ===
    
    @patch('subprocess.run')
    def test_check_corruption_pass(self, mock_run, quality_agent, tmp_path):
        """Test corruption check for clean video"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        open(video_path, 'w').close()
        mock_run.return_value = Mock(stderr='', returncode=0)
        
        report = {'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_corruption(video_path, report)
        
        # Assert
        assert report['checks']['corruption'] == 'pass'
    
    @patch('subprocess.run')
    def test_check_corruption_fail(self, mock_run, quality_agent, tmp_path):
        """Test corruption check for corrupted video"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        open(video_path, 'w').close()
        mock_run.return_value = Mock(
            stderr='corrupt data detected',
            returncode=0
        )
        
        report = {'errors': [], 'warnings': [], 'checks': {}}
        
        # Act
        quality_agent._check_corruption(video_path, report)
        
        # Assert
        assert report['checks']['corruption'] == 'fail'
        assert any('corrupt' in error.lower() for error in report['errors'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
