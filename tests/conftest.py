"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide a mock configuration for testing"""
    return {
        'research': {
            'sources': ['reddit', 'youtube', 'google_trends'],
            'topics_to_track': 10,
            'depth': 'comprehensive'
        },
        'video_generation': {
            'output_directory': 'output/videos',
            'default_resolution': '1920x1080',
            'default_fps': 30
        },
        'upload': {
            'enabled': False,
            'platforms': ['youtube'],
            'max_videos_per_day': 5
        },
        'workflow': {
            'auto_generate': False,
            'auto_upload': False,
            'temp_directory': 'temp'
        },
        'api_keys': {
            'openai': 'test_key',
            'anthropic': 'test_key'
        },
        'ollama': {
            'host': 'http://localhost:11434',
            'model': 'llama2'
        }
    }


@pytest.fixture
def sample_topic() -> Dict[str, Any]:
    """Provide a sample topic for testing"""
    return {
        'source': 'reddit',
        'title': 'Test Topic Title',
        'subreddit': 'test',
        'score': 1000,
        'url': 'https://reddit.com/test',
        'timestamp': '2024-01-01T00:00:00',
        'video_potential_score': 5.0
    }


@pytest.fixture
def sample_trends() -> list:
    """Provide sample trending topics"""
    return [
        {
            'source': 'reddit',
            'title': 'AI Breakthrough',
            'score': 5000,
            'video_potential_score': 8.5
        },
        {
            'source': 'youtube',
            'title': 'Tech Review',
            'category': 'Technology',
            'video_potential_score': 7.0
        },
        {
            'source': 'google_trends',
            'query': 'AI video generation',
            'interest': 100,
            'video_potential_score': 9.0
        }
    ]


@pytest.fixture
def mock_video_path(temp_dir):
    """Create a mock video file path"""
    video_path = os.path.join(temp_dir, 'test_video.mp4')
    # Create an empty file
    Path(video_path).touch()
    return video_path


@pytest.fixture
def mock_audio_path(temp_dir):
    """Create a mock audio file path"""
    audio_path = os.path.join(temp_dir, 'test_audio.mp3')
    Path(audio_path).touch()
    return audio_path


@pytest.fixture
def mock_image_path(temp_dir):
    """Create a mock image file path"""
    image_path = os.path.join(temp_dir, 'test_image.png')
    Path(image_path).touch()
    return image_path


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp session for API calls"""
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'data': {
                'children': [
                    {
                        'data': {
                            'title': 'Test Post',
                            'subreddit': 'test',
                            'score': 1000,
                            'url': 'https://test.com'
                        }
                    }
                ]
            }
        })

        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        yield mock_session


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for ffmpeg/ffprobe calls"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b'{"format": {"duration": "10.0"}}'
        mock_run.return_value.stderr = b''
        yield mock_run


@pytest.fixture
def sample_video_info():
    """Sample video information"""
    return {
        'format': {
            'duration': '60.0',
            'size': '10000000',
            'bit_rate': '1000000',
            'format_name': 'mp4'
        },
        'streams': [
            {
                'codec_type': 'video',
                'codec_name': 'h264',
                'width': 1920,
                'height': 1080,
                'r_frame_rate': '30/1'
            },
            {
                'codec_type': 'audio',
                'codec_name': 'aac',
                'sample_rate': '44100'
            }
        ]
    }


@pytest.fixture(autouse=True)
def setup_test_directories(temp_dir):
    """Setup test directories before each test"""
    test_dirs = [
        'output/videos',
        'output/trends',
        'logs',
        'temp'
    ]

    for directory in test_dirs:
        os.makedirs(os.path.join(temp_dir, directory), exist_ok=True)

    yield

    # Cleanup after test
    for directory in test_dirs:
        dir_path = os.path.join(temp_dir, directory)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)


@pytest.fixture
def mock_llm_response():
    """Mock LLM API response"""
    return {
        'choices': [
            {
                'message': {
                    'content': 'This is a test script for video generation.'
                }
            }
        ]
    }


@pytest.fixture
def sample_script():
    """Sample video script"""
    return """
    Title: Test Video

    Introduction:
    Welcome to this test video!

    Main Content:
    This is the main content of the video.

    Conclusion:
    Thanks for watching!
    """


@pytest.fixture
def sample_metadata():
    """Sample video metadata"""
    return {
        'title': 'Test Video Title',
        'description': 'Test video description',
        'tags': ['test', 'video', 'automated'],
        'category': 'Technology',
        'privacy': 'public'
    }
