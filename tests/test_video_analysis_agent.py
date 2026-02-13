"""
Tests for Video Analysis Agent
"""

import pytest
import json
from unittest.mock import Mock, patch
from agents.video_analysis_agent import VideoAnalysisAgent


@pytest.fixture
def config():
    """Test configuration"""
    return {
        'workflow': {'temp_directory': 'test_temp'}
    }


@pytest.fixture
def agent(config):
    """Create VideoAnalysisAgent instance"""
    return VideoAnalysisAgent(config)


class TestVideoAnalysisAgent:
    """Test suite for VideoAnalysisAgent"""
    
    def test_init(self, agent, config):
        """Test agent initialization"""
        assert agent.config == config
        assert agent.temp_dir == config['workflow']['temp_directory']
    
    @patch('subprocess.run')
    def test_get_metadata(self, mock_run, agent):
        """Test metadata extraction"""
        mock_data = {
            'format': {
                'duration': '120.5',
                'size': '10000000',
                'bit_rate': '800000',
                'format_name': 'mp4'
            },
            'streams': [
                {'codec_type': 'video'},
                {'codec_type': 'audio'}
            ]
        }
        
        mock_run.return_value = Mock(
            stdout=json.dumps(mock_data),
            returncode=0
        )
        
        metadata = agent.get_metadata('test.mp4')
        
        assert metadata['duration'] == 120.5
        assert metadata['size'] == 10000000
        assert metadata['format'] == 'mp4'
        assert metadata['has_video'] is True
        assert metadata['has_audio'] is True
    
    @patch('subprocess.run')
    def test_get_technical_info(self, mock_run, agent):
        """Test technical info extraction"""
        mock_data = {
            'streams': [
                {
                    'codec_type': 'video',
                    'codec_name': 'h264',
                    'width': 1920,
                    'height': 1080,
                    'r_frame_rate': '30/1',
                    'pix_fmt': 'yuv420p',
                    'nb_frames': '3600'
                }
            ]
        }
        
        mock_run.return_value = Mock(
            stdout=json.dumps(mock_data),
            returncode=0
        )
        
        info = agent.get_technical_info('test.mp4')
        
        assert info['codec'] == 'h264'
        assert info['width'] == 1920
        assert info['height'] == 1080
        assert info['fps'] == 30.0
        assert info['total_frames'] == 3600
    
    @patch('subprocess.run')
    def test_analyze_audio(self, mock_run, agent):
        """Test audio analysis"""
        mock_data = {
            'streams': [
                {
                    'codec_name': 'aac',
                    'sample_rate': '44100',
                    'channels': '2',
                    'bit_rate': '128000',
                    'duration': '120.0'
                }
            ]
        }
        
        mock_run.return_value = Mock(
            stdout=json.dumps(mock_data),
            returncode=0
        )
        
        audio_info = agent.analyze_audio('test.mp4')
        
        assert audio_info['has_audio'] is True
        assert audio_info['codec'] == 'aac'
        assert audio_info['sample_rate'] == 44100
        assert audio_info['channels'] == 2
    
    @patch('subprocess.run')
    def test_analyze_audio_no_audio(self, mock_run, agent):
        """Test audio analysis with no audio stream"""
        mock_run.return_value = Mock(
            stdout=json.dumps({'streams': []}),
            returncode=0
        )
        
        audio_info = agent.analyze_audio('test.mp4')
        
        assert audio_info['has_audio'] is False
    
    def test_assess_quality_4k(self, agent):
        """Test quality assessment for 4K video"""
        with patch.object(agent, 'get_metadata') as mock_metadata, \
             patch.object(agent, 'get_technical_info') as mock_technical:
            
            mock_metadata.return_value = {
                'bitrate': 50000000  # High bitrate
            }
            mock_technical.return_value = {
                'width': 3840,
                'height': 2160,
                'fps': 60
            }
            
            quality = agent.assess_quality('test.mp4')
            
            assert quality['resolution_quality'] == '4K'
            assert quality['fps_quality'] == 'High (60+ fps)'
            assert quality['overall_score'] == 'Excellent'
    
    def test_assess_quality_hd(self, agent):
        """Test quality assessment for HD video"""
        with patch.object(agent, 'get_metadata') as mock_metadata, \
             patch.object(agent, 'get_technical_info') as mock_technical:
            
            mock_metadata.return_value = {
                'bitrate': 5000000
            }
            mock_technical.return_value = {
                'width': 1280,
                'height': 720,
                'fps': 30
            }
            
            quality = agent.assess_quality('test.mp4')
            
            assert quality['resolution_quality'] == 'HD'
            assert quality['fps_quality'] == 'Standard (30 fps)'
    
    def test_parse_frame_rate(self, agent):
        """Test frame rate parsing"""
        assert agent._parse_frame_rate('30/1') == 30.0
        assert agent._parse_frame_rate('60/1') == 60.0
        assert agent._parse_frame_rate('24000/1001') == pytest.approx(23.976, rel=0.01)
        assert agent._parse_frame_rate('invalid') == 0.0
    
    def test_generate_recommendations_low_resolution(self, agent):
        """Test recommendations for low resolution video"""
        analysis = {
            'technical': {'height': 480},
            'quality': {'bitrate_quality': 'Medium'},
            'metadata': {'duration': 60},
            'audio': {'has_audio': True}
        }
        
        recommendations = agent._generate_recommendations(analysis)
        
        assert any('720p' in rec for rec in recommendations)
    
    def test_generate_recommendations_no_audio(self, agent):
        """Test recommendations for video without audio"""
        analysis = {
            'technical': {'height': 1080},
            'quality': {'bitrate_quality': 'High'},
            'metadata': {'duration': 60},
            'audio': {'has_audio': False}
        }
        
        recommendations = agent._generate_recommendations(analysis)
        
        assert any('audio' in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_long_video(self, agent):
        """Test recommendations for long video"""
        analysis = {
            'technical': {'height': 1080},
            'quality': {'bitrate_quality': 'High'},
            'metadata': {'duration': 720},  # 12 minutes
            'audio': {'has_audio': True}
        }
        
        recommendations = agent._generate_recommendations(analysis)
        
        assert any('shorter' in rec.lower() for rec in recommendations)
    
    @patch('subprocess.run')
    def test_comprehensive_analysis(self, mock_run, agent):
        """Test comprehensive analysis"""
        # Mock all subprocess calls
        mock_run.return_value = Mock(
            stdout=json.dumps({
                'format': {
                    'duration': '120.0',
                    'size': '10000000',
                    'bit_rate': '800000',
                    'format_name': 'mp4'
                },
                'streams': [
                    {
                        'codec_type': 'video',
                        'width': 1920,
                        'height': 1080,
                        'r_frame_rate': '30/1'
                    }
                ]
            }),
            returncode=0,
            stderr='pts_time:10.5 pts_time:25.3'
        )
        
        analysis = agent.analyze_comprehensive('test.mp4')
        
        assert 'metadata' in analysis
        assert 'technical' in analysis
        assert 'quality' in analysis
        assert 'recommendations' in analysis


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
