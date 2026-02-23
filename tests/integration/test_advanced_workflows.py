"""
Advanced Integration Tests

Tests for complex workflows involving multiple agents.
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Import all agents
from agents.audio_processing_agent import AudioProcessingAgent
from agents.video_quality_agent import VideoQualityAgent
from agents.subtitle_agent import SubtitleAgent
from agents.youtube_shorts_agent import YouTubeShortsAgent
from agents.video_analysis_agent import VideoAnalysisAgent
from agents.prompt_enhancement_agent import PromptEnhancementAgent


@pytest.mark.integration
class TestVideoProductionWorkflow:
    """Integration tests for complete video production workflows"""
    
    @pytest.fixture
    def config(self):
        """Configuration for all agents"""
        return {
            'audio': {'output_directory': 'test_output/audio'},
            'quality': {'output_directory': 'test_output/qa'},
            'subtitles': {'output_directory': 'test_output/subtitles'},
            'video_generation': {'output_directory': 'test_output/videos'},
            'workflow': {'temp_directory': 'test_temp'}
        }
    
    @pytest.fixture
    def agents(self, config):
        """Create all agent instances"""
        return {
            'audio': AudioProcessingAgent(config),
            'quality': VideoQualityAgent(config),
            'subtitle': SubtitleAgent(config),
            'shorts': YouTubeShortsAgent(config),
            'analysis': VideoAnalysisAgent(config),
            'prompt': PromptEnhancementAgent(config)
        }
    
    def test_video_quality_and_audio_workflow(self, agents, tmp_path):
        """Test workflow: Quality check → Audio extraction → Audio enhancement"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        with open(video_path, 'wb') as f:
            f.write(b'x' * 10000)
        
        # Act - Step 1: Quality check
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout='{"format": {"duration": "60.0"}, "streams": [{"codec_type": "video", "width": 1920}]}',
                stderr='',
                returncode=0
            )
            quality_report = agents['quality'].validate_video(video_path)
        
        # Assert quality check
        assert quality_report is not None
        assert 'valid' in quality_report
        
        # Act - Step 2: Extract audio (if quality is good)
        if quality_report.get('valid', False):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0)
                audio_path = agents['audio'].extract_audio(video_path)
            
            # Assert audio extraction
            assert audio_path is not None
            
            # Act - Step 3: Normalize audio
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0)
                normalized_path = agents['audio'].normalize_audio(audio_path)
            
            # Assert normalization
            assert normalized_path is not None
    
    @patch('subprocess.run')
    def test_complete_video_enhancement_workflow(self, mock_run, agents, tmp_path):
        """Test complete video enhancement: Quality → Audio → Subtitles"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        with open(video_path, 'wb') as f:
            f.write(b'video data')
        
        mock_run.return_value = Mock(
            stdout='{"format": {"duration": "60.0"}, "streams": [{"codec_type": "video", "width": 1920}]}',
            stderr='',
            returncode=0
        )
        
        # Act - Complete workflow
        # Step 1: Quality check
        quality_report = agents['quality'].validate_video(video_path)
        
        # Step 2: Extract and enhance audio
        audio_path = agents['audio'].extract_audio(video_path)
        normalized_audio = agents['audio'].normalize_audio(audio_path)
        
        # Step 3: Generate subtitles
        subtitle_path = agents['subtitle'].generate_subtitles_from_audio(video_path)
        
        # Assert all steps completed
        assert quality_report is not None
        assert audio_path is not None
        assert normalized_audio is not None
        assert subtitle_path is not None
        assert os.path.exists(subtitle_path)
    
    def test_prompt_enhancement_workflow(self, agents):
        """Test prompt enhancement workflow"""
        # Arrange
        simple_prompt = "a cat in a garden"
        
        # Act - Enhance prompt
        enhanced = agents['prompt'].enhance_prompt(simple_prompt, style='cinematic')
        
        # Assert
        assert enhanced is not None
        assert 'enhanced' in enhanced
        assert 'negative' in enhanced
        assert len(enhanced['enhanced']) > len(simple_prompt)
    
    def test_scene_breakdown_workflow(self, agents):
        """Test scene breakdown for video generation"""
        # Arrange
        scene_description = "a person walking through a futuristic city"
        
        # Act - Break down into frames
        frames = agents['prompt'].break_down_scene(scene_description, num_frames=4)
        
        # Assert
        assert frames is not None
        assert len(frames) == 4
        assert all('prompt' in frame for frame in frames)
        assert all('progress' in frame for frame in frames)
    
    @patch('subprocess.run')
    def test_subtitle_and_audio_sync_workflow(self, mock_run, agents, tmp_path):
        """Test workflow: Generate subtitles → Sync → Add to video"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        with open(video_path, 'wb') as f:
            f.write(b'video')
        
        mock_run.return_value = Mock(returncode=0)
        
        # Act - Generate subtitles
        subtitle_path = agents['subtitle'].generate_subtitles_from_audio(video_path)
        
        # Act - Sync subtitles (adjust timing)
        synced_path = agents['subtitle'].sync_subtitles(subtitle_path, 0.5)
        
        # Act - Burn subtitles into video
        final_video = agents['subtitle'].burn_subtitles(video_path, synced_path)
        
        # Assert
        assert subtitle_path is not None
        assert synced_path is not None
        assert final_video is not None
    
    @patch('subprocess.run')
    def test_audio_mixing_workflow(self, mock_run, agents, tmp_path):
        """Test audio mixing workflow: Extract → Mix → Add back"""
        # Arrange
        video_path = str(tmp_path / 'test.mp4')
        music_path = str(tmp_path / 'music.mp3')
        with open(video_path, 'wb') as f:
            f.write(b'video')
        with open(music_path, 'wb') as f:
            f.write(b'music')
        
        mock_run.return_value = Mock(returncode=0)
        
        # Act - Extract original audio
        original_audio = agents['audio'].extract_audio(video_path)
        
        # Act - Mix with background music
        tracks = [
            (original_audio, 1.0),  # Original audio at 100%
            (music_path, 0.3)       # Music at 30%
        ]
        mixed_audio = agents['audio'].mix_audio_tracks(tracks)
        
        # Assert
        assert original_audio is not None
        assert mixed_audio is not None
    
    @patch('subprocess.run')
    def test_quality_batch_validation(self, mock_run, agents, tmp_path):
        """Test batch quality validation workflow"""
        # Arrange
        videos = []
        for i in range(3):
            video_path = str(tmp_path / f'video{i}.mp4')
            with open(video_path, 'wb') as f:
                f.write(b'video data')
            videos.append(video_path)
        
        mock_run.return_value = Mock(
            stdout='{"format": {"duration": "60.0"}, "streams": [{"codec_type": "video", "width": 1920}]}',
            stderr='',
            returncode=0
        )
        
        # Act - Batch validate
        reports = agents['quality'].batch_validate(videos)
        
        # Assert
        assert len(reports) == 3
        assert all('valid' in report for report in reports)
    
    def test_subtitle_format_conversion_workflow(self, agents, tmp_path):
        """Test subtitle format conversion workflow"""
        # Arrange
        subtitles = [
            {'start': 0.0, 'end': 3.0, 'text': 'Test 1'},
            {'start': 3.0, 'end': 6.0, 'text': 'Test 2'}
        ]
        
        # Act - Create SRT
        srt_path = agents['subtitle'].create_srt(subtitles)
        
        # Act - Create VTT from same data
        vtt_path = agents['subtitle'].create_vtt(subtitles)
        
        # Assert both formats created
        assert os.path.exists(srt_path)
        assert os.path.exists(vtt_path)
        assert srt_path.endswith('.srt')
        assert vtt_path.endswith('.vtt')


@pytest.mark.integration
class TestAgentCommunication:
    """Test communication and data flow between agents"""
    
    def test_quality_to_audio_pipeline(self, tmp_path):
        """Test quality agent output can be used by audio agent"""
        # Arrange
        config = {
            'audio': {'output_directory': 'test_output/audio'},
            'quality': {'output_directory': 'test_output/qa'},
            'workflow': {'temp_directory': 'test_temp'}
        }
        
        quality_agent = VideoQualityAgent(config)
        audio_agent = AudioProcessingAgent(config)
        
        video_path = str(tmp_path / 'test.mp4')
        with open(video_path, 'wb') as f:
            f.write(b'x' * 10000)
        
        # Act - Quality check
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout='{"format": {"duration": "60.0"}, "streams": [{"codec_type": "video"}]}',
                stderr='',
                returncode=0
            )
            quality_report = quality_agent.validate_video(video_path)
        
        # Assert - Quality report contains info useful for audio processing
        assert 'metrics' in quality_report
        
        # Act - Use video if quality is acceptable
        if quality_report.get('valid', False):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0)
                audio_path = audio_agent.extract_audio(video_path)
                assert audio_path is not None
    
    def test_prompt_to_subtitle_pipeline(self):
        """Test prompt enhancement can help with subtitle generation"""
        # Arrange
        config = {
            'subtitles': {'output_directory': 'test_output/subtitles'},
            'workflow': {'temp_directory': 'test_temp'}
        }
        
        prompt_agent = PromptEnhancementAgent(config)
        subtitle_agent = SubtitleAgent(config)
        
        # Act - Generate enhanced description
        scene = "a documentary about wildlife"
        enhanced = prompt_agent.enhance_prompt(scene, style='realistic')
        
        # Assert - Enhanced prompt could be used for subtitle script
        assert enhanced['enhanced'] is not None
        
        # Act - Create subtitles from enhanced description
        subtitles = [
            {'start': 0.0, 'end': 5.0, 'text': enhanced['enhanced'][:50]}
        ]
        srt_path = subtitle_agent.create_srt(subtitles)
        
        # Assert
        assert os.path.exists(srt_path)


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceWorkflows:
    """Performance and stress tests for workflows"""
    
    @pytest.mark.timeout(30)
    def test_batch_processing_performance(self, tmp_path):
        """Test performance of batch processing"""
        # Arrange
        config = {
            'quality': {'output_directory': 'test_output/qa'},
            'workflow': {'temp_directory': 'test_temp'}
        }
        
        quality_agent = VideoQualityAgent(config)
        
        # Create multiple test videos
        videos = []
        for i in range(10):
            video_path = str(tmp_path / f'video{i}.mp4')
            with open(video_path, 'wb') as f:
                f.write(b'x' * 5000)
            videos.append(video_path)
        
        # Act - Batch validate with mocked subprocess
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout='{"format": {"duration": "30.0"}, "streams": []}',
                stderr='',
                returncode=0
            )
            reports = quality_agent.batch_validate(videos)
        
        # Assert - All processed
        assert len(reports) == 10
    
    def test_large_subtitle_file_handling(self, tmp_path):
        """Test handling of large subtitle files"""
        # Arrange
        config = {
            'subtitles': {'output_directory': 'test_output/subtitles'},
            'workflow': {'temp_directory': 'test_temp'}
        }
        
        subtitle_agent = SubtitleAgent(config)
        
        # Create large subtitle dataset
        subtitles = []
        for i in range(1000):
            subtitles.append({
                'start': i * 3.0,
                'end': i * 3.0 + 2.5,
                'text': f'Subtitle line {i}'
            })
        
        # Act - Create SRT file
        srt_path = subtitle_agent.create_srt(subtitles)
        
        # Assert - File created successfully
        assert os.path.exists(srt_path)
        
        # Act - Parse it back
        parsed = subtitle_agent._parse_srt(srt_path)
        
        # Assert - All subtitles present
        assert len(parsed) == 1000


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])
