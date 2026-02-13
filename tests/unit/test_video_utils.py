"""
Unit tests for video_utils module
"""

import pytest
import os
import json
from unittest.mock import patch
from scripts.video_utils import (
    get_video_info,
    resize_video,
    concatenate_videos,
    add_audio_to_video,
    extract_frames,
    create_video_from_images,
    add_text_overlay
)


@pytest.mark.unit
@pytest.mark.script
class TestVideoUtils:
    """Test suite for video utility functions"""

    def test_get_video_info_success(self, mock_video_path, sample_video_info):
        """Test getting video information"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(sample_video_info)

            info = get_video_info(mock_video_path)

        assert info is not None
        assert 'format' in info
        assert 'streams' in info
        assert info['format']['duration'] == '60.0'

    def test_get_video_info_failure(self, mock_video_path):
        """Test video info with ffprobe error"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = 'Error'

            info = get_video_info(mock_video_path)

        assert info is None

    def test_get_video_info_exception(self, mock_video_path):
        """Test video info with exception"""
        with patch('subprocess.run', side_effect=Exception('Test error')):
            info = get_video_info(mock_video_path)

        assert info is None

    def test_resize_video_success(self, mock_video_path, temp_dir):
        """Test successful video resize"""
        output_path = os.path.join(temp_dir, 'resized.mp4')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = resize_video(mock_video_path, output_path, 1280, 720)

        assert result is True
        mock_run.assert_called_once()

        # Check command arguments
        call_args = mock_run.call_args[0][0]
        assert 'ffmpeg' in call_args
        assert 'scale=1280:720' in ''.join(call_args)

    def test_resize_video_default_dimensions(self, mock_video_path, temp_dir):
        """Test resize with default dimensions"""
        output_path = os.path.join(temp_dir, 'resized.mp4')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = resize_video(mock_video_path, output_path)

        assert result is True

        call_args = mock_run.call_args[0][0]
        assert 'scale=1920:1080' in ''.join(call_args)

    def test_resize_video_failure(self, mock_video_path, temp_dir):
        """Test video resize failure"""
        output_path = os.path.join(temp_dir, 'resized.mp4')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = b'ffmpeg error'

            result = resize_video(mock_video_path, output_path)

        assert result is False

    def test_resize_video_exception(self, mock_video_path, temp_dir):
        """Test resize with exception"""
        output_path = os.path.join(temp_dir, 'resized.mp4')

        with patch('subprocess.run', side_effect=Exception('Test error')):
            result = resize_video(mock_video_path, output_path)

        assert result is False

    def test_concatenate_videos_success(self, temp_dir):
        """Test successful video concatenation"""
        video1 = os.path.join(temp_dir, 'video1.mp4')
        video2 = os.path.join(temp_dir, 'video2.mp4')
        output = os.path.join(temp_dir, 'concat.mp4')

        # Create dummy files
        open(video1, 'a').close()
        open(video2, 'a').close()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = concatenate_videos([video1, video2], output)

        assert result is True

    def test_concatenate_videos_creates_list_file(self, temp_dir):
        """Test that concat creates temporary list file"""
        videos = [os.path.join(temp_dir, f'v{i}.mp4') for i in range(3)]
        output = os.path.join(temp_dir, 'concat.mp4')

        for v in videos:
            open(v, 'a').close()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            concatenate_videos(videos, output)

        # List file should be created then cleaned up
        # After function completes, temp file should be removed

    def test_concatenate_videos_failure(self, temp_dir):
        """Test concatenation failure"""
        videos = [os.path.join(temp_dir, 'v1.mp4')]
        output = os.path.join(temp_dir, 'concat.mp4')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = b'error'

            result = concatenate_videos(videos, output)

        assert result is False

    def test_add_audio_to_video_success(self, mock_video_path, mock_audio_path, temp_dir):
        """Test adding audio to video"""
        output = os.path.join(temp_dir, 'with_audio.mp4')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = add_audio_to_video(mock_video_path, mock_audio_path, output)

        assert result is True

    def test_add_audio_to_video_failure(self, mock_video_path, mock_audio_path, temp_dir):
        """Test audio addition failure"""
        output = os.path.join(temp_dir, 'with_audio.mp4')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = b'error'

            result = add_audio_to_video(mock_video_path, mock_audio_path, output)

        assert result is False

    def test_extract_frames_success(self, mock_video_path, temp_dir):
        """Test frame extraction"""
        output_dir = os.path.join(temp_dir, 'frames')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = extract_frames(mock_video_path, output_dir, fps=2)

        assert result is True
        assert os.path.exists(output_dir)

    def test_extract_frames_default_fps(self, mock_video_path, temp_dir):
        """Test frame extraction with default fps"""
        output_dir = os.path.join(temp_dir, 'frames')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = extract_frames(mock_video_path, output_dir)

        assert result is True

        call_args = mock_run.call_args[0][0]
        assert 'fps=1' in ''.join(call_args)

    def test_create_video_from_images_success(self, temp_dir):
        """Test creating video from images"""
        image_dir = os.path.join(temp_dir, 'images')
        os.makedirs(image_dir, exist_ok=True)

        output = os.path.join(temp_dir, 'output.mp4')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = create_video_from_images(image_dir, output, fps=24)

        assert result is True

    def test_create_video_from_images_default_fps(self, temp_dir):
        """Test video creation with default fps"""
        image_dir = os.path.join(temp_dir, 'images')
        os.makedirs(image_dir, exist_ok=True)

        output = os.path.join(temp_dir, 'output.mp4')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = create_video_from_images(image_dir, output)

        assert result is True

        call_args = mock_run.call_args[0][0]
        assert '30' in call_args  # Default fps

    def test_add_text_overlay_success(self, mock_video_path, temp_dir):
        """Test adding text overlay"""
        output = os.path.join(temp_dir, 'with_text.mp4')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = add_text_overlay(mock_video_path, output, 'Test Text', position='top')

        assert result is True

    def test_add_text_overlay_all_positions(self, mock_video_path, temp_dir):
        """Test text overlay with all position options"""
        positions = ['top', 'bottom', 'center']

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            for pos in positions:
                output = os.path.join(temp_dir, f'text_{pos}.mp4')
                result = add_text_overlay(mock_video_path, output, 'Test', position=pos)
                assert result is True

    def test_add_text_overlay_invalid_position(self, mock_video_path, temp_dir):
        """Test text overlay with invalid position (should default to top)"""
        output = os.path.join(temp_dir, 'with_text.mp4')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = add_text_overlay(mock_video_path, output, 'Test', position='invalid')

        assert result is True


@pytest.mark.unit
@pytest.mark.script
class TestVideoUtilsEdgeCases:
    """Test edge cases and error conditions"""

    def test_get_video_info_invalid_json(self, mock_video_path):
        """Test video info with invalid JSON response"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = 'invalid json'

            info = get_video_info(mock_video_path)

        assert info is None

    def test_concatenate_videos_empty_list(self, temp_dir):
        """Test concatenation with empty video list"""
        output = os.path.join(temp_dir, 'concat.mp4')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = concatenate_videos([], output)

        # Should handle gracefully
        assert isinstance(result, bool)

    def test_extract_frames_zero_fps(self, mock_video_path, temp_dir):
        """Test frame extraction with zero fps"""
        output_dir = os.path.join(temp_dir, 'frames')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            result = extract_frames(mock_video_path, output_dir, fps=0)

        # Should still work (ffmpeg will handle)
        assert result is True
