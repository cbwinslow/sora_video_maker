"""
Comprehensive tests for Subtitle Agent

Implements AAA pattern and achieves high test coverage.
"""

import pytest
import os
from unittest.mock import Mock, patch
from agents.subtitle_agent import SubtitleAgent


@pytest.fixture
def config():
    """Test configuration"""
    return {
        'subtitles': {'output_directory': 'test_output/subtitles'},
        'workflow': {'temp_directory': 'test_temp'}
    }


@pytest.fixture
def subtitle_agent(config):
    """Create SubtitleAgent instance"""
    return SubtitleAgent(config)


@pytest.fixture
def sample_subtitles():
    """Sample subtitle data"""
    return [
        {'start': 0.0, 'end': 3.0, 'text': 'Hello world'},
        {'start': 3.0, 'end': 6.0, 'text': 'This is a test'},
        {'start': 6.0, 'end': 9.0, 'text': 'Thank you'}
    ]


@pytest.fixture
def sample_srt_content():
    """Sample SRT file content"""
    return """1
00:00:00,000 --> 00:00:03,000
Hello world

2
00:00:03,000 --> 00:00:06,000
This is a test

3
00:00:06,000 --> 00:00:09,000
Thank you

"""


class TestSubtitleAgent:
    """Test suite for SubtitleAgent"""
    
    # === Initialization Tests ===
    
    def test_init(self, subtitle_agent, config):
        """Test agent initialization"""
        # Assert
        assert subtitle_agent.config == config
        assert subtitle_agent.output_dir == config['subtitles']['output_directory']
        assert subtitle_agent.temp_dir == config['workflow']['temp_directory']
    
    def test_init_creates_directories(self, tmp_path):
        """Test that initialization creates required directories"""
        # Arrange
        config = {
            'subtitles': {'output_directory': str(tmp_path / 'subs')},
            'workflow': {'temp_directory': str(tmp_path / 'temp')}
        }
        
        # Act
        agent = SubtitleAgent(config)
        
        # Assert
        assert os.path.exists(agent.output_dir)
        assert os.path.exists(agent.temp_dir)
    
    # === Subtitle Generation Tests ===
    
    def test_generate_subtitles_from_audio(self, subtitle_agent, tmp_path):
        """Test subtitle generation from audio"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        with open(video_path, 'wb') as f:
            f.write(b'fake video')
        
        # Act
        result = subtitle_agent.generate_subtitles_from_audio(video_path)
        
        # Assert
        assert result is not None
        assert result.endswith('.srt')
        assert os.path.exists(result)
    
    def test_generate_subtitles_file_not_found(self, subtitle_agent):
        """Test subtitle generation with non-existent file"""
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            subtitle_agent.generate_subtitles_from_audio('/nonexistent/video.mp4')
    
    # === SRT Creation Tests ===
    
    def test_create_srt_success(self, subtitle_agent, sample_subtitles):
        """Test successful SRT file creation"""
        # Act
        result = subtitle_agent.create_srt(sample_subtitles)
        
        # Assert
        assert result is not None
        assert result.endswith('.srt')
        assert os.path.exists(result)
        
        # Verify content
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Hello world' in content
            assert '00:00:00,000 --> 00:00:03,000' in content
    
    def test_create_srt_with_custom_path(self, subtitle_agent, sample_subtitles, tmp_path):
        """Test SRT creation with custom output path"""
        # Arrange
        output_path = str(tmp_path / 'custom.srt')
        
        # Act
        result = subtitle_agent.create_srt(sample_subtitles, output_path)
        
        # Assert
        assert result == output_path
        assert os.path.exists(output_path)
    
    def test_create_srt_empty_list(self, subtitle_agent):
        """Test SRT creation with empty subtitle list"""
        # Act
        result = subtitle_agent.create_srt([])
        
        # Assert
        assert os.path.exists(result)
    
    # === VTT Creation Tests ===
    
    def test_create_vtt_success(self, subtitle_agent, sample_subtitles):
        """Test successful VTT file creation"""
        # Act
        result = subtitle_agent.create_vtt(sample_subtitles)
        
        # Assert
        assert result is not None
        assert result.endswith('.vtt')
        assert os.path.exists(result)
        
        # Verify content
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'WEBVTT' in content
            assert 'Hello world' in content
            assert '00:00:00.000 --> 00:00:03.000' in content  # VTT uses dots
    
    def test_create_vtt_with_custom_path(self, subtitle_agent, sample_subtitles, tmp_path):
        """Test VTT creation with custom output path"""
        # Arrange
        output_path = str(tmp_path / 'custom.vtt')
        
        # Act
        result = subtitle_agent.create_vtt(sample_subtitles, output_path)
        
        # Assert
        assert result == output_path
        assert os.path.exists(output_path)
    
    # === Timestamp Formatting Tests ===
    
    @pytest.mark.parametrize("seconds,expected_srt", [
        (0.0, '00:00:00,000'),
        (1.5, '00:00:01,500'),
        (65.0, '00:01:05,000'),
        (3665.5, '01:01:05,500'),
    ])
    def test_format_timestamp_srt(self, subtitle_agent, seconds, expected_srt):
        """Test SRT timestamp formatting"""
        # Act
        result = subtitle_agent._format_timestamp(seconds, vtt=False)
        
        # Assert
        assert result == expected_srt
    
    @pytest.mark.parametrize("seconds,expected_vtt", [
        (0.0, '00:00:00.000'),
        (1.5, '00:00:01.500'),
        (65.0, '00:01:05.000'),
        (3665.5, '01:01:05.500'),
    ])
    def test_format_timestamp_vtt(self, subtitle_agent, seconds, expected_vtt):
        """Test VTT timestamp formatting"""
        # Act
        result = subtitle_agent._format_timestamp(seconds, vtt=True)
        
        # Assert
        assert result == expected_vtt
    
    # === Burn Subtitles Tests ===
    
    @patch('subprocess.run')
    def test_burn_subtitles_success(self, mock_run, subtitle_agent, tmp_path):
        """Test successful subtitle burning"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        subtitle_path = str(tmp_path / 'test.srt')
        with open(video_path, 'wb') as f:
            f.write(b'video')
        with open(subtitle_path, 'w') as f:
            f.write('1\n00:00:00,000 --> 00:00:03,000\nTest\n')
        
        mock_run.return_value = Mock(returncode=0)
        
        # Act
        result = subtitle_agent.burn_subtitles(video_path, subtitle_path)
        
        # Assert
        assert result is not None
        assert 'subtitled_' in result
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_burn_subtitles_with_style(self, mock_run, subtitle_agent, tmp_path):
        """Test subtitle burning with custom style"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        subtitle_path = str(tmp_path / 'test.srt')
        with open(video_path, 'wb') as f:
            f.write(b'video')
        with open(subtitle_path, 'w') as f:
            f.write('1\n00:00:00,000 --> 00:00:03,000\nTest\n')
        
        style = {
            'fontsize': 32,
            'fontcolor': 'yellow',
            'bordercolor': 'black',
            'borderwidth': 3
        }
        
        mock_run.return_value = Mock(returncode=0)
        
        # Act
        result = subtitle_agent.burn_subtitles(video_path, subtitle_path, style)
        
        # Assert
        assert result is not None
    
    def test_burn_subtitles_video_not_found(self, subtitle_agent, tmp_path):
        """Test subtitle burning with non-existent video"""
        # Arrange
        subtitle_path = str(tmp_path / 'test.srt')
        with open(subtitle_path, 'w') as f:
            f.write('1\n00:00:00,000 --> 00:00:03,000\nTest\n')
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            subtitle_agent.burn_subtitles('/nonexistent/video.mp4', subtitle_path)
    
    def test_burn_subtitles_subtitle_not_found(self, subtitle_agent, tmp_path):
        """Test subtitle burning with non-existent subtitle"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        with open(video_path, 'wb') as f:
            f.write(b'video')
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            subtitle_agent.burn_subtitles(video_path, '/nonexistent/subtitle.srt')
    
    # === Color Conversion Tests ===
    
    @pytest.mark.parametrize("color,expected", [
        ('white', '&HFFFFFF'),
        ('black', '&H000000'),
        ('red', '&H0000FF'),
        ('yellow', '&H00FFFF'),
        ('unknown', '&HFFFFFF'),  # Default to white
    ])
    def test_color_to_ass(self, subtitle_agent, color, expected):
        """Test color conversion to ASS format"""
        # Act
        result = subtitle_agent._color_to_ass(color)
        
        # Assert
        assert result == expected
    
    # === Soft Subtitles Tests ===
    
    @patch('subprocess.run')
    def test_add_soft_subtitles_success(self, mock_run, subtitle_agent, tmp_path):
        """Test successful soft subtitle addition"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        subtitle_path = str(tmp_path / 'test.srt')
        with open(video_path, 'wb') as f:
            f.write(b'video')
        with open(subtitle_path, 'w') as f:
            f.write('subtitle')
        
        mock_run.return_value = Mock(returncode=0)
        
        # Act
        result = subtitle_agent.add_soft_subtitles(video_path, subtitle_path)
        
        # Assert
        assert result is not None
        assert result.endswith('.mkv')
    
    # === SRT Parsing Tests ===
    
    def test_parse_srt_success(self, subtitle_agent, tmp_path, sample_srt_content):
        """Test successful SRT parsing"""
        # Arrange
        srt_path = str(tmp_path / 'test.srt')
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(sample_srt_content)
        
        # Act
        result = subtitle_agent._parse_srt(srt_path)
        
        # Assert
        assert len(result) == 3
        assert result[0]['text'] == 'Hello world'
        assert result[0]['start'] == 0.0
        assert result[0]['end'] == 3.0
    
    def test_parse_srt_malformed(self, subtitle_agent, tmp_path):
        """Test SRT parsing with malformed content"""
        # Arrange
        srt_path = str(tmp_path / 'malformed.srt')
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write('Not a valid SRT file\n')
        
        # Act
        result = subtitle_agent._parse_srt(srt_path)
        
        # Assert
        assert isinstance(result, list)
        # Should handle gracefully
    
    # === Timestamp Parsing Tests ===
    
    @pytest.mark.parametrize("timestamp,expected", [
        ('00:00:00,000', 0.0),
        ('00:00:01,500', 1.5),
        ('00:01:05,000', 65.0),
        ('01:01:05,500', 3665.5),
        ('00:00:00.000', 0.0),  # VTT format
    ])
    def test_parse_timestamp(self, subtitle_agent, timestamp, expected):
        """Test timestamp parsing"""
        # Act
        result = subtitle_agent._parse_timestamp(timestamp)
        
        # Assert
        assert result == expected
    
    def test_parse_timestamp_invalid(self, subtitle_agent):
        """Test parsing invalid timestamp"""
        # Act
        result = subtitle_agent._parse_timestamp('invalid')
        
        # Assert
        assert result == 0.0
    
    # === Subtitle Synchronization Tests ===
    
    def test_sync_subtitles_positive_offset(self, subtitle_agent, tmp_path, sample_srt_content):
        """Test subtitle synchronization with positive offset"""
        # Arrange
        srt_path = str(tmp_path / 'test.srt')
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(sample_srt_content)
        
        # Act
        result = subtitle_agent.sync_subtitles(srt_path, 2.0)
        
        # Assert
        assert os.path.exists(result)
        
        # Verify timing was adjusted
        synced_subs = subtitle_agent._parse_srt(result)
        assert synced_subs[0]['start'] == 2.0
        assert synced_subs[0]['end'] == 5.0
    
    def test_sync_subtitles_negative_offset(self, subtitle_agent, tmp_path, sample_srt_content):
        """Test subtitle synchronization with negative offset"""
        # Arrange
        srt_path = str(tmp_path / 'test.srt')
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(sample_srt_content)
        
        # Act
        result = subtitle_agent.sync_subtitles(srt_path, -1.0)
        
        # Assert
        assert os.path.exists(result)
        
        # Verify timing was adjusted (should not go below 0)
        synced_subs = subtitle_agent._parse_srt(result)
        assert synced_subs[0]['start'] == 0.0  # Clamped to 0
    
    def test_sync_subtitles_file_not_found(self, subtitle_agent):
        """Test subtitle sync with non-existent file"""
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            subtitle_agent.sync_subtitles('/nonexistent/subtitle.srt', 1.0)
    
    # === Subtitle Merging Tests ===
    
    def test_merge_subtitles_success(self, subtitle_agent, tmp_path):
        """Test successful subtitle merging"""
        # Arrange
        srt1_path = str(tmp_path / 'sub1.srt')
        srt2_path = str(tmp_path / 'sub2.srt')
        
        with open(srt1_path, 'w', encoding='utf-8') as f:
            f.write('1\n00:00:00,000 --> 00:00:03,000\nFirst\n\n')
        
        with open(srt2_path, 'w', encoding='utf-8') as f:
            f.write('1\n00:00:05,000 --> 00:00:08,000\nSecond\n\n')
        
        # Act
        result = subtitle_agent.merge_subtitles([srt1_path, srt2_path])
        
        # Assert
        assert os.path.exists(result)
        
        # Verify merged content
        merged_subs = subtitle_agent._parse_srt(result)
        assert len(merged_subs) == 2
        # Should be sorted by start time
        assert merged_subs[0]['start'] < merged_subs[1]['start']
    
    def test_merge_subtitles_empty_list(self, subtitle_agent):
        """Test merging with empty list"""
        # Act
        result = subtitle_agent.merge_subtitles([])
        
        # Assert
        assert os.path.exists(result)
    
    def test_merge_subtitles_with_missing_files(self, subtitle_agent, tmp_path):
        """Test merging with some missing files"""
        # Arrange
        srt1_path = str(tmp_path / 'sub1.srt')
        with open(srt1_path, 'w', encoding='utf-8') as f:
            f.write('1\n00:00:00,000 --> 00:00:03,000\nFirst\n\n')
        
        # Act
        result = subtitle_agent.merge_subtitles([srt1_path, '/nonexistent/sub2.srt'])
        
        # Assert
        assert os.path.exists(result)
        merged_subs = subtitle_agent._parse_srt(result)
        assert len(merged_subs) == 1  # Only the valid file
    
    # === Translation Tests ===
    
    def test_translate_subtitles(self, subtitle_agent, tmp_path):
        """Test subtitle translation (placeholder)"""
        # Arrange
        srt_path = str(tmp_path / 'test.srt')
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write('1\n00:00:00,000 --> 00:00:03,000\nHello\n\n')
        
        # Act
        result = subtitle_agent.translate_subtitles(srt_path, 'es')
        
        # Assert
        assert result is not None
        assert os.path.exists(result)
        assert 'translated_es_' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
