"""
Tests for YouTube Shorts Agent
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from agents.youtube_shorts_agent import YouTubeShortsAgent


@pytest.fixture
def config():
    """Test configuration"""
    return {
        'video_generation': {'output_directory': 'test_output/shorts'},
        'workflow': {'temp_directory': 'test_temp'}
    }


@pytest.fixture
def shorts_agent(config):
    """Create YouTubeShortsAgent instance"""
    return YouTubeShortsAgent(config)


class TestYouTubeShortsAgent:
    """Test suite for YouTubeShortsAgent"""
    
    def test_init(self, shorts_agent, config):
        """Test agent initialization"""
        assert shorts_agent.config == config
        assert shorts_agent.shorts_duration == 60
        assert shorts_agent.shorts_aspect_ratio == (9, 16)
    
    def test_suggest_segments_short_video(self, shorts_agent):
        """Test segment suggestion for short video"""
        duration = 30.0  # 30 seconds
        segments = shorts_agent._suggest_segments(duration)
        
        assert len(segments) == 1
        assert segments[0]['start'] == 0
        assert segments[0]['end'] == duration
    
    def test_suggest_segments_long_video(self, shorts_agent):
        """Test segment suggestion for long video"""
        duration = 180.0  # 3 minutes
        segments = shorts_agent._suggest_segments(duration)
        
        assert len(segments) > 1
        for segment in segments:
            assert segment['duration'] <= 60
            assert segment['duration'] >= 10
    
    @patch('subprocess.run')
    def test_get_video_duration(self, mock_run, shorts_agent):
        """Test getting video duration"""
        mock_run.return_value = Mock(
            stdout='120.5\n',
            returncode=0
        )
        
        duration = shorts_agent._get_video_duration('test.mp4')
        assert duration == 120.5
    
    @patch('subprocess.run')
    def test_analyze_video(self, mock_run, shorts_agent):
        """Test video analysis"""
        import json
        
        mock_metadata = {
            'format': {
                'duration': '120.0',
                'size': '1000000',
                'bit_rate': '800000'
            },
            'streams': [
                {
                    'codec_type': 'video',
                    'width': 1920,
                    'height': 1080,
                    'r_frame_rate': '30/1'
                }
            ]
        }
        
        mock_run.return_value = Mock(
            stdout=json.dumps(mock_metadata),
            returncode=0
        )
        
        analysis = shorts_agent.analyze_video('test.mp4')
        
        assert 'duration' in analysis
        assert 'width' in analysis
        assert 'height' in analysis
        assert 'fps' in analysis
    
    @patch('subprocess.run')
    def test_create_short(self, mock_run, shorts_agent, tmp_path):
        """Test creating a short"""
        # Mock successful ffmpeg run
        mock_run.return_value = Mock(returncode=0)
        
        # Create a fake video file
        video_path = str(tmp_path / "test_video.mp4")
        with open(video_path, 'w') as f:
            f.write("fake video")
        
        output = shorts_agent.create_short(
            video_path,
            start_time=0,
            duration=30,
            add_captions=False
        )
        
        assert output is not None
        assert 'short_' in output
        assert output.endswith('.mp4')
    
    @patch('yt_dlp.YoutubeDL')
    def test_download_video(self, mock_ytdl, shorts_agent):
        """Test video download"""
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {
            'title': 'Test Video',
            'ext': 'mp4'
        }
        mock_instance.prepare_filename.return_value = 'test_temp/Test Video.mp4'
        mock_ytdl.return_value.__enter__.return_value = mock_instance
        
        result = shorts_agent.download_video('https://youtube.com/watch?v=test')
        
        assert result == 'test_temp/Test Video.mp4'
    
    def test_optimize_for_shorts(self, shorts_agent, tmp_path):
        """Test shorts optimization"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            video_path = str(tmp_path / "test.mp4")
            with open(video_path, 'w') as f:
                f.write("fake video")
            
            output = shorts_agent.optimize_for_shorts(video_path)
            
            assert output is not None
            assert 'optimized_' in output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
