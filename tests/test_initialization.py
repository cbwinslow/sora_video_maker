"""
Comprehensive Initialization Tests

Tests for 100% coverage of agent initialization and basic functionality.
These tests verify that all components can be properly initialized and
that the system is ready for operation.
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
class TestAgentInitialization:
    """Test initialization of all agents"""
    
    def test_trending_topics_agent_init(self, mock_config):
        """Test TrendingTopicsAgent initialization"""
        from agents.trending_topics_agent import TrendingTopicsAgent
        
        agent = TrendingTopicsAgent(mock_config)
        
        assert agent is not None
        assert agent.config == mock_config
        assert hasattr(agent, 'research')
    
    def test_video_generation_agent_init(self, mock_config):
        """Test VideoGenerationOrchestrator initialization"""
        from agents.video_generation_agent import VideoGenerationOrchestrator
        
        agent = VideoGenerationOrchestrator(mock_config)
        
        assert agent is not None
        assert agent.config == mock_config
        assert hasattr(agent, 'generate_video')
    
    def test_video_upload_agent_init(self, mock_config):
        """Test VideoUploadAgent initialization"""
        from agents.video_upload_agent import VideoUploadAgent
        
        agent = VideoUploadAgent(mock_config)
        
        assert agent is not None
        assert agent.config == mock_config
        assert hasattr(agent, 'upload_video')
    
    def test_deep_research_agent_init(self, mock_config):
        """Test DeepResearchAgent initialization"""
        from agents.deep_research_agent import DeepResearchAgent
        
        agent = DeepResearchAgent(mock_config)
        
        assert agent is not None
        assert agent.config == mock_config
        assert hasattr(agent, 'research_topic')
    
    def test_video_editing_agent_init(self, mock_config):
        """Test VideoEditingAgent initialization"""
        from agents.video_editing_agent import VideoEditingAgent
        
        agent = VideoEditingAgent(mock_config)
        
        assert agent is not None
        assert agent.config == mock_config
        assert hasattr(agent, 'edit_video')
    
    def test_multiplatform_upload_agent_init(self, mock_config):
        """Test MultiPlatformUploadAgent initialization"""
        from agents.multiplatform_upload_agent import MultiPlatformUploadAgent
        
        agent = MultiPlatformUploadAgent(mock_config)
        
        assert agent is not None
        assert agent.config == mock_config
        assert hasattr(agent, 'upload_to_all_platforms')


@pytest.mark.unit
class TestCrewInitialization:
    """Test initialization of crew modules"""
    
    def test_video_production_crew_init(self, mock_config):
        """Test VideoProductionCrew initialization"""
        from crews.video_production_crew import VideoProductionCrew
        
        crew = VideoProductionCrew(mock_config)
        
        assert crew is not None
        assert crew.config == mock_config
        assert hasattr(crew, 'research_agent')
        assert hasattr(crew, 'deep_research_agent')
        assert hasattr(crew, 'generation_agent')
        assert hasattr(crew, 'editing_agent')
        assert hasattr(crew, 'upload_agent')
    
    def test_short_form_crew_init(self, mock_config):
        """Test ShortFormCrew initialization"""
        from crews.video_production_crew import ShortFormCrew
        
        crew = ShortFormCrew(mock_config)
        
        assert crew is not None
        assert crew.config == mock_config
        assert hasattr(crew, 'research_agent')
        assert hasattr(crew, 'generation_agent')
        assert hasattr(crew, 'editing_agent')
        assert hasattr(crew, 'upload_agent')


@pytest.mark.unit
class TestWorkflowOrchestratorInitialization:
    """Test workflow orchestrator initialization"""
    
    def test_workflow_orchestrator_init(self, temp_dir):
        """Test WorkflowOrchestrator initialization"""
        from main import WorkflowOrchestrator
        
        config_path = os.path.join(temp_dir, 'test_config.yaml')
        
        # Create a test config file
        import yaml
        test_config = {
            'research': {'sources': ['reddit']},
            'video_generation': {'output_directory': temp_dir},
            'upload': {'enabled': False}
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        orchestrator = WorkflowOrchestrator(config_path)
        
        assert orchestrator is not None
        assert orchestrator.config is not None
        assert hasattr(orchestrator, 'topics_agent')
        assert hasattr(orchestrator, 'generation_agent')
        assert hasattr(orchestrator, 'upload_agent')
    
    def test_workflow_orchestrator_default_config(self):
        """Test WorkflowOrchestrator with default config"""
        from main import WorkflowOrchestrator
        
        # Use non-existent path to trigger default config
        orchestrator = WorkflowOrchestrator('/nonexistent/config.yaml')
        
        assert orchestrator is not None
        assert orchestrator.config is not None
        assert 'research' in orchestrator.config
        assert 'video_generation' in orchestrator.config
    
    def test_workflow_orchestrator_directory_creation(self, temp_dir):
        """Test that orchestrator creates necessary directories"""
        from main import WorkflowOrchestrator
        import shutil
        
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            orchestrator = WorkflowOrchestrator('/nonexistent/config.yaml')
            orchestrator.setup_directories()
            
            assert os.path.exists('output/videos')
            assert os.path.exists('output/trends')
            assert os.path.exists('logs')
            assert os.path.exists('temp')
        finally:
            os.chdir(original_dir)


@pytest.mark.unit
class TestDirectoryStructure:
    """Test that required directories exist or can be created"""
    
    def test_agents_directory_exists(self):
        """Test that agents directory exists"""
        agents_dir = Path(__file__).parent.parent / 'agents'
        assert agents_dir.exists()
        assert agents_dir.is_dir()
    
    def test_scripts_directory_exists(self):
        """Test that scripts directory exists"""
        scripts_dir = Path(__file__).parent.parent / 'scripts'
        assert scripts_dir.exists()
        assert scripts_dir.is_dir()
    
    def test_crews_directory_exists(self):
        """Test that crews directory exists"""
        crews_dir = Path(__file__).parent.parent / 'crews'
        assert crews_dir.exists()
        assert crews_dir.is_dir()
    
    def test_tests_directory_exists(self):
        """Test that tests directory exists"""
        tests_dir = Path(__file__).parent
        assert tests_dir.exists()
        assert tests_dir.is_dir()
    
    def test_config_directory_exists(self):
        """Test that config directory exists"""
        config_dir = Path(__file__).parent.parent / 'config'
        assert config_dir.exists()
        assert config_dir.is_dir()
    
    def test_workflows_directory_exists(self):
        """Test that workflows directory exists"""
        workflows_dir = Path(__file__).parent.parent / 'workflows'
        assert workflows_dir.exists()
        assert workflows_dir.is_dir()


@pytest.mark.unit
class TestPythonEnvironment:
    """Test Python environment and dependencies"""
    
    def test_python_version(self):
        """Test Python version is 3.8+"""
        import sys
        assert sys.version_info >= (3, 8)
    
    def test_required_modules_importable(self):
        """Test that required modules can be imported"""
        required_modules = [
            'yaml',
            'requests',
            'aiohttp',
            'pytest',
            'PIL',
            'cv2',
        ]
        
        for module_name in required_modules:
            try:
                __import__(module_name)
            except ImportError:
                pytest.fail(f"Required module {module_name} cannot be imported")
    
    def test_optional_modules_available(self):
        """Test that optional modules are available (skip if not)"""
        optional_modules = [
            'torch',
            'transformers',
            'openai',
            'anthropic',
        ]
        
        for module_name in optional_modules:
            try:
                __import__(module_name)
            except ImportError:
                pytest.skip(f"Optional module {module_name} not installed")


@pytest.mark.unit
class TestConfigurationLoading:
    """Test configuration loading functionality"""
    
    def test_config_template_exists(self):
        """Test that config template exists"""
        config_template = Path(__file__).parent.parent / 'config' / 'config.template.yaml'
        assert config_template.exists()
    
    def test_config_template_valid_yaml(self):
        """Test that config template is valid YAML"""
        import yaml
        
        config_template = Path(__file__).parent.parent / 'config' / 'config.template.yaml'
        
        with open(config_template, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_config_has_required_sections(self):
        """Test that config has all required sections"""
        import yaml
        
        config_template = Path(__file__).parent.parent / 'config' / 'config.template.yaml'
        
        with open(config_template, 'r') as f:
            config = yaml.safe_load(f)
        
        required_sections = [
            'research',
            'video_generation',
            'upload',
        ]
        
        for section in required_sections:
            assert section in config, f"Config missing required section: {section}"


@pytest.mark.unit
class TestLogging:
    """Test logging configuration"""
    
    def test_logging_module_available(self):
        """Test that logging module is available"""
        import logging
        assert logging is not None
    
    def test_logger_creation(self):
        """Test that loggers can be created"""
        import logging
        
        logger = logging.getLogger('test_logger')
        assert logger is not None
        assert logger.name == 'test_logger'
    
    def test_log_directory_creation(self, temp_dir):
        """Test that log directory can be created"""
        log_dir = os.path.join(temp_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        assert os.path.exists(log_dir)
        assert os.path.isdir(log_dir)


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in initialization"""
    
    def test_agent_init_with_invalid_config(self):
        """Test agent initialization with invalid config"""
        from agents.trending_topics_agent import TrendingTopicsAgent
        
        # Should handle None config gracefully
        invalid_config = None
        
        with pytest.raises(Exception):
            agent = TrendingTopicsAgent(invalid_config)
    
    def test_agent_init_with_empty_config(self):
        """Test agent initialization with empty config"""
        from agents.trending_topics_agent import TrendingTopicsAgent
        
        # Should handle empty dict
        empty_config = {}
        
        agent = TrendingTopicsAgent(empty_config)
        assert agent is not None
    
    def test_workflow_orchestrator_with_missing_config(self):
        """Test orchestrator handles missing config file"""
        from main import WorkflowOrchestrator
        
        orchestrator = WorkflowOrchestrator('/nonexistent/path/config.yaml')
        
        # Should use default config
        assert orchestrator is not None
        assert orchestrator.config is not None
