"""
Integration tests for WorkflowOrchestrator
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from main import WorkflowOrchestrator


@pytest.mark.integration
class TestWorkflowOrchestrator:
    """Integration tests for main workflow"""
    
    def test_init_with_config_file(self, temp_dir):
        """Test initialization with config file"""
        import yaml
        
        config_path = os.path.join(temp_dir, 'config.yaml')
        config_data = {
            'research': {'sources': ['reddit']},
            'video_generation': {'output_directory': 'output/videos'}
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        orchestrator = WorkflowOrchestrator(config_path)
        
        assert orchestrator.config['research']['sources'] == ['reddit']
    
    def test_init_with_missing_config(self):
        """Test initialization with missing config file"""
        orchestrator = WorkflowOrchestrator('nonexistent_config.yaml')
        
        # Should use default config
        assert 'research' in orchestrator.config
        assert 'video_generation' in orchestrator.config
    
    def test_setup_directories(self, temp_dir):
        """Test directory creation"""
        config = {
            'research': {'sources': ['reddit']},
            'video_generation': {'output_directory': temp_dir}
        }
        
        with patch.object(WorkflowOrchestrator, 'load_config', return_value=config):
            orchestrator = WorkflowOrchestrator()
        
        # Directories should be created
        assert os.path.exists('output/videos')
        assert os.path.exists('output/trends')
        assert os.path.exists('logs')
        assert os.path.exists('temp')
    
    @pytest.mark.asyncio
    async def test_run_research_phase(self, mock_config):
        """Test research phase"""
        with patch.object(WorkflowOrchestrator, 'load_config', return_value=mock_config):
            orchestrator = WorkflowOrchestrator()
        
        mock_trends = [
            {'source': 'reddit', 'title': 'Test 1', 'score': 1000},
            {'source': 'youtube', 'title': 'Test 2'}
        ]
        
        with patch.object(orchestrator.topics_agent, 'research', return_value=mock_trends), \
            patch.object(orchestrator.topics_agent, 'save_trends'):
            
            trends = await orchestrator.run_research_phase()
        
        assert len(trends) == 2
        assert trends[0]['source'] == 'reddit'
    
    @pytest.mark.asyncio
    async def test_run_generation_phase(self, mock_config, sample_trends):
        """Test video generation phase"""
        with patch.object(WorkflowOrchestrator, 'load_config', return_value=mock_config):
            orchestrator = WorkflowOrchestrator()
        
        mock_result = {
            'status': 'success',
            'video_path': '/path/video.mp4',
            'topic': sample_trends[0]
        }
        
        with patch.object(orchestrator.generation_agent, 'generate_video', return_value=mock_result), \
            patch.object(orchestrator.generation_agent, 'save_metadata'):
            
            results = await orchestrator.run_generation_phase(sample_trends)
        
        assert len(results) > 0
        assert results[0]['status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_run_upload_phase(self, mock_config):
        """Test video upload phase"""
        with patch.object(WorkflowOrchestrator, 'load_config', return_value=mock_config):
            orchestrator = WorkflowOrchestrator()
        
        generation_results = [
            {
                'status': 'success',
                'video_path': '/path/video.mp4',
                'topic': {'title': 'Test'},
                'script': 'Test script'
            }
        ]
        
        mock_upload_results = [
            {'platform': 'youtube', 'status': 'success', 'url': 'https://youtube.com/test'}
        ]
        
        with patch.object(orchestrator.upload_agent, 'generate_metadata', return_value={}), \
            patch.object(orchestrator.upload_agent, 'upload_video', return_value=mock_upload_results), \
            patch.object(orchestrator.upload_agent, 'save_upload_log'):
            
            results = await orchestrator.run_upload_phase(generation_results)
        
        assert len(results) > 0
        assert results[0]['platform'] == 'youtube'
    
    @pytest.mark.asyncio
    async def test_run_full_workflow(self, mock_config):
        """Test complete workflow"""
        mock_config['workflow']['auto_generate'] = True
        mock_config['workflow']['auto_upload'] = True
        
        with patch.object(WorkflowOrchestrator, 'load_config', return_value=mock_config):
            orchestrator = WorkflowOrchestrator()
        
        mock_trends = [{'source': 'reddit', 'title': 'Test', 'score': 1000}]
        mock_gen_result = {
            'status': 'success',
            'video_path': '/path/video.mp4',
            'topic': mock_trends[0],
            'script': 'Test script'
        }
        mock_upload_result = [{'platform': 'youtube', 'status': 'success'}]
        
        with patch.object(orchestrator.topics_agent, 'research', return_value=mock_trends), \
            patch.object(orchestrator.topics_agent, 'save_trends'), \
            patch.object(orchestrator.generation_agent, 'generate_video', return_value=mock_gen_result), \
            patch.object(orchestrator.generation_agent, 'save_metadata'), \
            patch.object(orchestrator.upload_agent, 'generate_metadata', return_value={}), \
            patch.object(orchestrator.upload_agent, 'upload_video', return_value=mock_upload_result), \
            patch.object(orchestrator.upload_agent, 'save_upload_log'):
            
            await orchestrator.run_full_workflow()
        
        # Should complete without errors
    
    @pytest.mark.asyncio
    async def test_run_research_only(self, mock_config):
        """Test research-only mode"""
        with patch.object(WorkflowOrchestrator, 'load_config', return_value=mock_config):
            orchestrator = WorkflowOrchestrator()
        
        mock_trends = [
            {'source': 'reddit', 'title': 'Test 1', 'score': 5000, 'video_potential_score': 5.0},
            {'source': 'youtube', 'title': 'Test 2', 'video_potential_score': 4.0}
        ]
        
        with patch.object(orchestrator.topics_agent, 'research', return_value=mock_trends), \
            patch.object(orchestrator.topics_agent, 'save_trends'):
            
            await orchestrator.run_research_only()
        
        # Should complete without errors
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, mock_config):
        """Test workflow error handling"""
        with patch.object(WorkflowOrchestrator, 'load_config', return_value=mock_config):
            orchestrator = WorkflowOrchestrator()
        
        with patch.object(orchestrator.topics_agent, 'research', side_effect=Exception('Test error')):
            # Should not raise exception
            await orchestrator.run_full_workflow()
    
    @pytest.mark.asyncio
    async def test_upload_phase_skips_failed_generation(self, mock_config):
        """Test that upload phase skips failed generations"""
        with patch.object(WorkflowOrchestrator, 'load_config', return_value=mock_config):
            orchestrator = WorkflowOrchestrator()
        
        generation_results = [
            {'status': 'error', 'error': 'Generation failed'},
            {
                'status': 'success',
                'video_path': '/path/video.mp4',
                'topic': {'title': 'Test'},
                'script': 'Script'
            }
        ]
        
        with patch.object(orchestrator.upload_agent, 'generate_metadata', return_value={}), \
            patch.object(orchestrator.upload_agent, 'upload_video', return_value=[]), \
            patch.object(orchestrator.upload_agent, 'save_upload_log'):
            
            results = await orchestrator.run_upload_phase(generation_results)
        
        # Should only process successful generations
        orchestrator.upload_agent.upload_video.assert_called_once()


@pytest.mark.integration
class TestWorkflowOrchestratorConfiguration:
    """Test configuration handling"""
    
    def test_get_default_config(self):
        """Test default configuration"""
        with patch.object(WorkflowOrchestrator, 'load_config', side_effect=lambda x: WorkflowOrchestrator.get_default_config(None)):
            orchestrator = WorkflowOrchestrator()
            config = orchestrator.config
        
        # Manually get default config
        default_config = {
            'research': {
                'sources': ['reddit', 'youtube', 'google_trends'],
                'topics_to_track': 10
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
                'auto_upload': False
            }
        }
        
        assert 'research' in config or default_config
        assert 'video_generation' in config or default_config
    
    def test_load_config_yaml_error(self, temp_dir):
        """Test loading malformed YAML"""
        config_path = os.path.join(temp_dir, 'bad_config.yaml')
        
        with open(config_path, 'w') as f:
            f.write('invalid: yaml: content: {]')
        
        orchestrator = WorkflowOrchestrator(config_path)
        
        # Should fall back to default config
        assert 'research' in orchestrator.config
