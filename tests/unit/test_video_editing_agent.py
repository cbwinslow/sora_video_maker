"""
Unit tests for VideoEditingAgent
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from agents.video_editing_agent import VideoEditingAgent


@pytest.mark.unit
@pytest.mark.agent
class TestVideoEditingAgent:
    """Test suite for VideoEditingAgent"""
    
    def test_init(self, mock_config):
        """Test agent initialization"""
        agent = VideoEditingAgent(mock_config)
        
        assert agent.config == mock_config
        assert agent.output_dir == mock_config['video_generation']['output_directory']
        assert agent.temp_dir == mock_config['workflow']['temp_directory']
    
    def test_init_creates_directories(self, mock_config, temp_dir):
        """Test that directories are created"""
        mock_config['video_generation']['output_directory'] = os.path.join(temp_dir, 'output')
        mock_config['workflow']['temp_directory'] = os.path.join(temp_dir, 'temp')
        
        agent = VideoEditingAgent(mock_config)
        
        assert os.path.exists(agent.output_dir)
        assert os.path.exists(agent.temp_dir)
    
    def test_trim_video(self, mock_config, mock_video_path):
        """Test video trimming"""
        agent = VideoEditingAgent(mock_config)
        
        trim_config = {'start': 5, 'duration': 30}
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = agent.trim_video(mock_video_path, trim_config)
        
        assert result.endswith('.mp4')
        mock_run.assert_called_once()
    
    def test_trim_video_no_duration(self, mock_config, mock_video_path):
        """Test trimming without duration (trim to end)"""
        agent = VideoEditingAgent(mock_config)
        
        trim_config = {'start': 10}
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = agent.trim_video(mock_video_path, trim_config)
        
        assert result.endswith('.mp4')
    
    def test_trim_video_error(self, mock_config, mock_video_path):
        """Test trim error handling"""
        agent = VideoEditingAgent(mock_config)
        
        trim_config = {'start': 0, 'duration': 10}
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.side_effect = Exception('Test error')
            
            result = agent.trim_video(mock_video_path, trim_config)
        
        # Should return original path on error
        assert result == mock_video_path
    
    def test_add_intro(self, mock_config, mock_video_path, temp_dir):
        """Test adding intro"""
        agent = VideoEditingAgent(mock_config)
        
        intro_path = os.path.join(temp_dir, 'intro.mp4')
        open(intro_path, 'a').close()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = agent.add_intro(mock_video_path, intro_path)
        
        assert result.endswith('.mp4')
    
    def test_add_outro(self, mock_config, mock_video_path, temp_dir):
        """Test adding outro"""
        agent = VideoEditingAgent(mock_config)
        
        outro_path = os.path.join(temp_dir, 'outro.mp4')
        open(outro_path, 'a').close()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = agent.add_outro(mock_video_path, outro_path)
        
        assert result.endswith('.mp4')
    
    def test_add_background_music(self, mock_config, mock_video_path, mock_audio_path):
        """Test adding background music"""
        agent = VideoEditingAgent(mock_config)
        
        music_config = {
            'path': mock_audio_path,
            'volume': 0.5
        }
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = agent.add_background_music(mock_video_path, music_config)
        
        assert result.endswith('.mp4')
    
    def test_add_background_music_default_volume(self, mock_config, mock_video_path, mock_audio_path):
        """Test music with default volume"""
        agent = VideoEditingAgent(mock_config)
        
        music_config = {'path': mock_audio_path}
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = agent.add_background_music(mock_video_path, music_config)
        
        assert result.endswith('.mp4')
        
        # Check that default volume is used
        call_args = str(mock_run.call_args)
        assert '0.3' in call_args
    
    def test_add_subtitles(self, mock_config, mock_video_path):
        """Test adding subtitles"""
        agent = VideoEditingAgent(mock_config)
        
        subtitle_config = {
            'text': [
                {
                    'start': '00:00:00,000',
                    'end': '00:00:05,000',
                    'text': 'Hello World'
                },
                {
                    'start': '00:00:05,000',
                    'end': '00:00:10,000',
                    'text': 'Welcome'
                }
            ]
        }
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = agent.add_subtitles(mock_video_path, subtitle_config)
        
        assert result.endswith('.mp4')
    
    def test_apply_color_grade(self, mock_config, mock_video_path):
        """Test color grading"""
        agent = VideoEditingAgent(mock_config)
        
        grades = ['vibrant', 'cinematic', 'warm', 'cool', 'bw']
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            for grade in grades:
                result = agent.apply_color_grade(mock_video_path, grade)
                assert result.endswith('.mp4')
    
    def test_apply_color_grade_invalid(self, mock_config, mock_video_path):
        """Test color grade with invalid preset (should use default)"""
        agent = VideoEditingAgent(mock_config)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = agent.apply_color_grade(mock_video_path, 'invalid_preset')
        
        assert result.endswith('.mp4')
    
    def test_create_short_form(self, mock_config, mock_video_path):
        """Test creating short-form video"""
        agent = VideoEditingAgent(mock_config)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = agent.create_short_form(mock_video_path, duration=30)
        
        assert result.endswith('.mp4')
    
    def test_create_short_form_default_duration(self, mock_config, mock_video_path):
        """Test short-form with default duration"""
        agent = VideoEditingAgent(mock_config)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = agent.create_short_form(mock_video_path)
        
        assert result.endswith('.mp4')
        
        call_args = str(mock_run.call_args)
        assert '60' in call_args  # Default duration
    
    def test_edit_video_full_workflow(self, mock_config, mock_video_path, mock_audio_path):
        """Test complete editing workflow"""
        agent = VideoEditingAgent(mock_config)
        
        edits = {
            'trim': {'start': 0, 'duration': 60},
            'add_music': {'path': mock_audio_path, 'volume': 0.4},
            'color_grade': 'vibrant'
        }
        
        with patch.object(agent, 'trim_video', return_value='/tmp/trimmed.mp4'), \
            patch.object(agent, 'add_background_music', return_value='/tmp/music.mp4'), \
            patch.object(agent, 'apply_color_grade', return_value='/tmp/graded.mp4'), \
            patch('os.rename'):
            
            result = agent.edit_video(mock_video_path, edits)
        
        assert result.endswith('.mp4')
    
    def test_edit_video_with_all_edits(self, mock_config, mock_video_path, temp_dir):
        """Test editing with all possible edit types"""
        agent = VideoEditingAgent(mock_config)
        
        intro = os.path.join(temp_dir, 'intro.mp4')
        outro = os.path.join(temp_dir, 'outro.mp4')
        music = os.path.join(temp_dir, 'music.mp3')
        
        for f in [intro, outro, music]:
            open(f, 'a').close()
        
        edits = {
            'trim': {'start': 0, 'duration': 30},
            'add_intro': intro,
            'add_outro': outro,
            'add_music': {'path': music},
            'add_subtitles': {
                'text': [{'start': '00:00:00,000', 'end': '00:00:05,000', 'text': 'Test'}]
            },
            'color_grade': 'cinematic',
            'add_transitions': {}
        }
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            with patch('os.rename'):
                result = agent.edit_video(mock_video_path, edits)
        
        assert result.endswith('.mp4')
    
    def test_add_transitions(self, mock_config, mock_video_path):
        """Test transitions (simplified version)"""
        agent = VideoEditingAgent(mock_config)
        
        transition_config = {'type': 'fade'}
        
        result = agent.add_transitions(mock_video_path, transition_config)
        
        # Current implementation is simplified
        assert result == mock_video_path


@pytest.mark.unit
@pytest.mark.agent
class TestVideoEditingAgentErrorHandling:
    """Test error handling in video editing"""
    
    def test_add_intro_error(self, mock_config, mock_video_path):
        """Test intro addition error"""
        agent = VideoEditingAgent(mock_config)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.side_effect = Exception('Error')
            
            result = agent.add_intro(mock_video_path, '/nonexistent/intro.mp4')
        
        assert result == mock_video_path
    
    def test_add_outro_error(self, mock_config, mock_video_path):
        """Test outro addition error"""
        agent = VideoEditingAgent(mock_config)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.side_effect = Exception('Error')
            
            result = agent.add_outro(mock_video_path, '/nonexistent/outro.mp4')
        
        assert result == mock_video_path
    
    def test_create_short_form_error(self, mock_config, mock_video_path):
        """Test short-form creation error"""
        agent = VideoEditingAgent(mock_config)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.side_effect = Exception('Error')
            
            result = agent.create_short_form(mock_video_path)
        
        assert result == mock_video_path
