"""
Unit tests for VideoGenerationOrchestrator
"""

import pytest
import os
from unittest.mock import patch
from agents.video_generation_agent import VideoGenerationOrchestrator


@pytest.mark.unit
@pytest.mark.agent
class TestVideoGenerationOrchestrator:
    """Test suite for VideoGenerationOrchestrator"""

    def test_init(self, mock_config):
        """Test orchestrator initialization"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        assert orchestrator.config == mock_config
        assert orchestrator.output_dir == mock_config['video_generation']['output_directory']

    def test_init_creates_output_directory(self, mock_config, temp_dir):
        """Test that output directory is created"""
        mock_config['video_generation']['output_directory'] = os.path.join(temp_dir, 'test_output')

        orchestrator = VideoGenerationOrchestrator(mock_config)

        assert os.path.exists(orchestrator.output_dir)

    @pytest.mark.asyncio
    async def test_generate_script(self, mock_config, sample_topic):
        """Test script generation from topic"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        script = await orchestrator.generate_script(sample_topic)

        assert isinstance(script, str)
        assert len(script) > 0
        assert sample_topic['title'] in script

    @pytest.mark.asyncio
    async def test_generate_script_with_missing_title(self, mock_config):
        """Test script generation with missing title"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        topic = {'source': 'test'}  # No title
        script = await orchestrator.generate_script(topic)

        assert isinstance(script, str)
        assert 'Untitled' in script or 'this topic' in script

    @pytest.mark.asyncio
    async def test_generate_prompts(self, mock_config, sample_script):
        """Test visual prompt generation"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        prompts = await orchestrator.generate_prompts(sample_script)

        assert isinstance(prompts, list)
        assert len(prompts) > 0
        assert all(isinstance(p, str) for p in prompts)

    @pytest.mark.asyncio
    async def test_generate_with_comfyui(self, mock_config):
        """Test ComfyUI generation"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        prompt = "Test prompt for ComfyUI"
        workflow_path = "workflows/test.json"

        output_path = await orchestrator.generate_with_comfyui(prompt, workflow_path)

        assert isinstance(output_path, str)
        assert output_path.endswith('.png')

    @pytest.mark.asyncio
    async def test_generate_with_sora(self, mock_config):
        """Test Sora API generation (placeholder)"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        prompt = "Test prompt for Sora"

        output_path = await orchestrator.generate_with_sora(prompt)

        assert isinstance(output_path, str)
        assert output_path.endswith('.mp4')

    @pytest.mark.asyncio
    async def test_generate_with_openrouter(self, mock_config):
        """Test OpenRouter API generation"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        prompt = "Test prompt for OpenRouter"

        result = await orchestrator.generate_with_openrouter(prompt)

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_assemble_video(self, mock_config, temp_dir):
        """Test video assembly from frames"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        frames = [
            os.path.join(temp_dir, 'frame1.png'),
            os.path.join(temp_dir, 'frame2.png')
        ]

        output_path = await orchestrator.assemble_video(frames)

        assert isinstance(output_path, str)
        assert output_path.endswith('.mp4')

    @pytest.mark.asyncio
    async def test_assemble_video_with_audio(self, mock_config, temp_dir, mock_audio_path):
        """Test video assembly with audio"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        frames = [os.path.join(temp_dir, f'frame{i}.png') for i in range(3)]

        output_path = await orchestrator.assemble_video(frames, audio_path=mock_audio_path)

        assert isinstance(output_path, str)
        assert output_path.endswith('.mp4')

    @pytest.mark.asyncio
    async def test_generate_video_success(self, mock_config, sample_topic):
        """Test complete video generation workflow"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        with patch.object(orchestrator, 'generate_script', return_value='Test script'), \
            patch.object(orchestrator, 'generate_prompts', return_value=['prompt1', 'prompt2']), \
            patch.object(orchestrator, 'generate_with_comfyui', return_value='/path/frame.png'), \
            patch.object(orchestrator, 'assemble_video', return_value='/path/video.mp4'):

            result = await orchestrator.generate_video(sample_topic)

        assert result['status'] == 'success'
        assert 'video_path' in result
        assert 'script' in result
        assert 'duration' in result
        assert result['topic'] == sample_topic

    @pytest.mark.asyncio
    async def test_generate_video_with_openai_key(self, mock_config, sample_topic):
        """Test video generation when OpenAI key is present"""
        mock_config['api_keys']['openai'] = 'test_key'
        orchestrator = VideoGenerationOrchestrator(mock_config)

        with patch.object(orchestrator, 'generate_script', return_value='Test script'), \
            patch.object(orchestrator, 'generate_prompts', return_value=['prompt1']), \
            patch.object(orchestrator, 'generate_with_sora', return_value='/path/video.mp4'), \
            patch.object(orchestrator, 'assemble_video', return_value='/path/final.mp4'):

            result = await orchestrator.generate_video(sample_topic)

        assert result['status'] == 'success'

    @pytest.mark.asyncio
    async def test_generate_video_error_handling(self, mock_config, sample_topic):
        """Test error handling in video generation"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        with patch.object(orchestrator, 'generate_script', side_effect=Exception('Test error')):
            result = await orchestrator.generate_video(sample_topic)

        assert result['status'] == 'error'
        assert 'error' in result
        assert result['error'] == 'Test error'
        assert result['topic'] == sample_topic

    def test_save_metadata(self, mock_config, temp_dir):
        """Test metadata saving"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        result = {
            'status': 'success',
            'video_path': '/path/video.mp4',
            'topic': {'title': 'Test'}
        }

        filename = os.path.join(temp_dir, 'metadata.json')
        orchestrator.save_metadata(result, filename)

        assert os.path.exists(filename)

        import json
        with open(filename, 'r') as f:
            loaded = json.load(f)

        assert loaded['status'] == 'success'
        assert loaded['video_path'] == '/path/video.mp4'

    def test_save_metadata_auto_filename(self, mock_config, temp_dir):
        """Test metadata saving with auto-generated filename"""
        mock_config['video_generation']['output_directory'] = temp_dir
        orchestrator = VideoGenerationOrchestrator(mock_config)

        result = {'status': 'success', 'test': 'data'}

        orchestrator.save_metadata(result)

        # Should create a file in the output directory
        files = os.listdir(temp_dir)
        metadata_files = [f for f in files if f.startswith('metadata_')]

        assert len(metadata_files) > 0

    def test_save_metadata_error(self, mock_config):
        """Test metadata saving with invalid path"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        result = {'status': 'success'}

        # Should not raise exception, just log error
        orchestrator.save_metadata(result, '/invalid/path/metadata.json')


@pytest.mark.unit
@pytest.mark.agent
class TestVideoGenerationOrchestratorEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_generate_prompts_empty_script(self, mock_config):
        """Test prompt generation with empty script"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        prompts = await orchestrator.generate_prompts("")

        assert isinstance(prompts, list)
        assert len(prompts) > 0

    @pytest.mark.asyncio
    async def test_assemble_video_empty_frames(self, mock_config):
        """Test video assembly with no frames"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        output_path = await orchestrator.assemble_video([])

        assert isinstance(output_path, str)

    @pytest.mark.asyncio
    async def test_generate_video_minimal_topic(self, mock_config):
        """Test video generation with minimal topic data"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        minimal_topic = {}

        with patch.object(orchestrator, 'generate_script', return_value='script'), \
            patch.object(orchestrator, 'generate_prompts', return_value=['p1']), \
            patch.object(orchestrator, 'generate_with_comfyui', return_value='/frame.png'), \
            patch.object(orchestrator, 'assemble_video', return_value='/video.mp4'):

            result = await orchestrator.generate_video(minimal_topic)

        assert result['status'] == 'success'

    @pytest.mark.asyncio
    async def test_generate_with_openrouter_custom_model(self, mock_config):
        """Test OpenRouter with custom model"""
        orchestrator = VideoGenerationOrchestrator(mock_config)

        result = await orchestrator.generate_with_openrouter(
            "test prompt",
            model="custom-model"
        )

        assert isinstance(result, str)
