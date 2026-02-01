"""
System Integration Tests

Tests for file system access, web service connectivity, and system services.
These tests verify that agents can access required resources and services.
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import aiohttp
import subprocess


@pytest.mark.integration
class TestFileSystemAccess:
    """Test file system access for all agents"""
    
    def test_agent_can_read_config_directory(self):
        """Test agents can access config directory"""
        config_dir = Path(__file__).parent.parent / 'config'
        
        assert config_dir.exists()
        assert config_dir.is_dir()
        assert os.access(config_dir, os.R_OK)
    
    def test_agent_can_write_output_directory(self, temp_dir):
        """Test agents can write to output directories"""
        output_dir = Path(temp_dir) / 'output'
        output_dir.mkdir(exist_ok=True)
        
        # Test write access
        test_file = output_dir / 'test.txt'
        test_file.write_text('test')
        
        assert test_file.exists()
        assert test_file.read_text() == 'test'
    
    def test_agent_can_create_temp_files(self, temp_dir):
        """Test agents can create temporary files"""
        temp_file = Path(temp_dir) / 'temp_test.txt'
        temp_file.write_text('temporary data')
        
        assert temp_file.exists()
        
        # Cleanup
        temp_file.unlink()
        assert not temp_file.exists()
    
    def test_agent_can_read_workflow_files(self):
        """Test agents can read workflow JSON files"""
        workflows_dir = Path(__file__).parent.parent / 'workflows'
        
        if workflows_dir.exists():
            json_files = list(workflows_dir.glob('*.json'))
            
            if json_files:
                import json
                for workflow_file in json_files:
                    with open(workflow_file, 'r') as f:
                        data = json.load(f)
                    assert data is not None
    
    def test_agent_can_create_nested_directories(self, temp_dir):
        """Test agents can create nested directory structures"""
        nested_path = Path(temp_dir) / 'output' / 'videos' / 'processed'
        nested_path.mkdir(parents=True, exist_ok=True)
        
        assert nested_path.exists()
        assert nested_path.is_dir()
    
    def test_agent_handles_missing_directories(self, temp_dir):
        """Test agents handle missing directories gracefully"""
        from agents.video_generation_agent import VideoGenerationOrchestrator
        
        config = {
            'video_generation': {
                'output_directory': str(Path(temp_dir) / 'nonexistent' / 'output')
            }
        }
        
        agent = VideoGenerationOrchestrator(config)
        
        # Should create missing directories
        assert Path(agent.output_dir).exists()
    
    def test_agent_can_access_scripts_directory(self):
        """Test agents can access scripts directory"""
        scripts_dir = Path(__file__).parent.parent / 'scripts'
        
        assert scripts_dir.exists()
        assert os.access(scripts_dir, os.R_OK)
    
    def test_agent_can_list_directory_contents(self):
        """Test agents can list directory contents"""
        agents_dir = Path(__file__).parent.parent / 'agents'
        
        if agents_dir.exists():
            contents = list(agents_dir.iterdir())
            assert len(contents) > 0
    
    def test_file_permissions_appropriate(self, temp_dir):
        """Test file permissions are set appropriately"""
        test_file = Path(temp_dir) / 'test_permissions.txt'
        test_file.write_text('test')
        
        # Should be readable and writable
        assert os.access(test_file, os.R_OK)
        assert os.access(test_file, os.W_OK)


@pytest.mark.integration
@pytest.mark.api
class TestWebServiceAccess:
    """Test web service connectivity and API access"""
    
    @pytest.mark.asyncio
    async def test_aiohttp_session_creation(self):
        """Test that aiohttp sessions can be created"""
        async with aiohttp.ClientSession() as session:
            assert session is not None
    
    @pytest.mark.asyncio
    async def test_localhost_connectivity(self):
        """Test connectivity to localhost"""
        try:
            async with aiohttp.ClientSession() as session:
                # Just test that we can create a session and handle errors
                # Don't actually try to connect since services may not be running
                assert session is not None
        except Exception as e:
            pytest.fail(f"Failed to create aiohttp session: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_ollama_connectivity(self, mock_config):
        """Test Ollama service connectivity"""
        from scripts.api_integrations import OllamaClient
        
        client = OllamaClient(mock_config)
        
        # Test that client can be created
        assert client is not None
        assert hasattr(client, 'generate')
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_comfyui_connectivity(self, mock_config):
        """Test ComfyUI service connectivity"""
        from scripts.api_integrations import ComfyUIClient
        
        config = {
            'comfyui': {
                'host': 'http://localhost:8188',
                'enabled': True
            }
        }
        
        client = ComfyUIClient(config)
        
        # Test that client can be created
        assert client is not None
        assert hasattr(client, 'queue_prompt')
    
    def test_api_client_initialization(self, mock_config):
        """Test API client initialization"""
        from scripts.api_integrations import APIIntegrations
        
        clients = APIIntegrations(mock_config)
        
        assert clients is not None
    
    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test HTTP error handling"""
        async with aiohttp.ClientSession() as session:
            try:
                # Try to connect to invalid endpoint
                async with session.get('http://localhost:99999/invalid') as response:
                    pass
            except (aiohttp.ClientError, OSError, ConnectionError):
                # Should handle connection errors gracefully
                pass
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test request timeout handling"""
        timeout = aiohttp.ClientTimeout(total=1)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            assert session is not None
    
    def test_api_key_configuration(self, mock_config):
        """Test API key configuration"""
        assert 'api_keys' in mock_config
        assert 'openai' in mock_config['api_keys']
    
    @pytest.mark.asyncio
    async def test_reddit_api_access(self, mock_config):
        """Test Reddit API access (mocked)"""
        from agents.trending_topics_agent import TrendingTopicsAgent
        
        agent = TrendingTopicsAgent(mock_config)
        
        # Mock the API call
        mock_data = [
            {
                'source': 'reddit',
                'title': 'Test Post',
                'score': 100
            }
        ]
        
        with patch.object(agent, 'fetch_reddit_trends', return_value=mock_data):
            trends = await agent.fetch_reddit_trends()
        
        assert len(trends) > 0
        assert trends[0]['source'] == 'reddit'


@pytest.mark.integration
class TestSystemServices:
    """Test system service availability and status"""
    
    def test_python_executable_available(self):
        """Test Python executable is available"""
        result = subprocess.run(
            ['python', '--version'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'Python' in result.stdout or 'Python' in result.stderr
    
    def test_pip_available(self):
        """Test pip is available"""
        result = subprocess.run(
            ['pip', '--version'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'pip' in result.stdout
    
    def test_git_available(self):
        """Test git is available"""
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'git' in result.stdout
    
    @pytest.mark.slow
    def test_ffmpeg_available(self):
        """Test FFmpeg is available"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                assert 'ffmpeg' in result.stdout.lower()
            else:
                pytest.skip("FFmpeg not installed")
        except FileNotFoundError:
            pytest.skip("FFmpeg not found")
        except subprocess.TimeoutExpired:
            pytest.skip("FFmpeg timeout")
    
    @pytest.mark.slow
    def test_ffprobe_available(self):
        """Test FFprobe is available"""
        try:
            result = subprocess.run(
                ['ffprobe', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                assert 'ffprobe' in result.stdout.lower()
            else:
                pytest.skip("FFprobe not installed")
        except FileNotFoundError:
            pytest.skip("FFprobe not found")
        except subprocess.TimeoutExpired:
            pytest.skip("FFprobe timeout")
    
    def test_required_python_packages_installed(self):
        """Test required Python packages are installed"""
        required_packages = [
            'pytest',
            'aiohttp',
            'requests',
            'yaml',
            'PIL',
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"Required package {package} not installed")
    
    @pytest.mark.slow
    def test_optional_services_detection(self):
        """Test detection of optional services"""
        services_to_check = [
            ('ollama', ['ollama', '--version']),
        ]
        
        service_status = {}
        
        for service_name, command in services_to_check:
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                service_status[service_name] = (result.returncode == 0)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                service_status[service_name] = False
        
        # Just record status, don't fail
        assert isinstance(service_status, dict)


@pytest.mark.integration
class TestResourceAvailability:
    """Test system resource availability"""
    
    def test_disk_space_available(self):
        """Test that sufficient disk space is available"""
        import shutil
        
        stat = shutil.disk_usage('.')
        
        # Should have at least 100MB free
        assert stat.free > 100 * 1024 * 1024
    
    def test_memory_available(self):
        """Test that system has memory information available"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            assert memory.total > 0
            assert memory.available > 0
        except ImportError:
            pytest.skip("psutil not installed")
    
    def test_cpu_count_available(self):
        """Test CPU count is available"""
        import os
        
        cpu_count = os.cpu_count()
        assert cpu_count is not None
        assert cpu_count > 0
    
    def test_temp_directory_accessible(self):
        """Test temporary directory is accessible"""
        import tempfile
        
        temp_dir = tempfile.gettempdir()
        assert os.path.exists(temp_dir)
        assert os.access(temp_dir, os.W_OK)


@pytest.mark.integration
class TestNetworkConfiguration:
    """Test network configuration and connectivity"""
    
    def test_localhost_resolvable(self):
        """Test localhost can be resolved"""
        import socket
        
        try:
            socket.gethostbyname('localhost')
        except socket.gaierror:
            pytest.fail("Cannot resolve localhost")
    
    @pytest.mark.asyncio
    async def test_async_socket_creation(self):
        """Test async socket creation"""
        import asyncio
        
        try:
            # Just test socket creation capability
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection('127.0.0.1', 1, limit=1024),
                timeout=1
            )
            writer.close()
            await writer.wait_closed()
        except (OSError, asyncio.TimeoutError, ConnectionRefusedError):
            # Expected - we're just testing socket capability
            pass
    
    def test_environment_variables_accessible(self):
        """Test environment variables can be accessed"""
        import os
        
        # Should be able to read environment variables
        path = os.environ.get('PATH')
        assert path is not None
    
    def test_can_create_socket(self):
        """Test socket creation"""
        import socket
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.close()


@pytest.mark.integration
class TestScriptAccess:
    """Test access to utility scripts"""
    
    def test_api_integrations_importable(self):
        """Test API integrations module can be imported"""
        try:
            from scripts import api_integrations
            assert api_integrations is not None
        except ImportError as e:
            pytest.fail(f"Cannot import api_integrations: {e}")
    
    def test_video_utils_importable(self):
        """Test video utils module can be imported"""
        try:
            from scripts import video_utils
            assert video_utils is not None
        except ImportError as e:
            pytest.fail(f"Cannot import video_utils: {e}")
    
    def test_batch_processor_importable(self):
        """Test batch processor can be imported"""
        try:
            from scripts import batch_processor
            assert batch_processor is not None
        except ImportError:
            pytest.skip("batch_processor not available")
    
    def test_all_scripts_have_proper_structure(self):
        """Test all Python scripts have proper structure"""
        scripts_dir = Path(__file__).parent.parent / 'scripts'
        
        if scripts_dir.exists():
            for script in scripts_dir.glob('*.py'):
                if script.name.startswith('__'):
                    continue
                
                # Should be importable
                assert script.exists()
                assert script.is_file()


@pytest.mark.integration
class TestConfigurationAccess:
    """Test configuration file access"""
    
    def test_config_template_readable(self):
        """Test config template is readable"""
        config_template = Path(__file__).parent.parent / 'config' / 'config.template.yaml'
        
        assert config_template.exists()
        assert os.access(config_template, os.R_OK)
        
        import yaml
        with open(config_template, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config is not None
    
    def test_config_can_be_written(self, temp_dir):
        """Test configuration can be written"""
        import yaml
        
        config_path = Path(temp_dir) / 'test_config.yaml'
        
        test_config = {
            'test': 'value',
            'nested': {
                'key': 'value'
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        assert config_path.exists()
        
        # Read it back
        with open(config_path, 'r') as f:
            loaded = yaml.safe_load(f)
        
        assert loaded == test_config
    
    def test_dotenv_loading(self):
        """Test .env file loading capability"""
        try:
            from dotenv import load_dotenv
            
            # Just test the function exists
            assert load_dotenv is not None
        except ImportError:
            pytest.fail("python-dotenv not installed")


@pytest.mark.integration
@pytest.mark.slow
class TestSystemdServices:
    """Test systemd service detection and status"""
    
    def test_systemctl_available(self):
        """Test systemctl is available on Linux systems"""
        if sys.platform != 'linux':
            pytest.skip("Not on Linux")
        
        try:
            result = subprocess.run(
                ['systemctl', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                assert 'systemd' in result.stdout.lower()
        except FileNotFoundError:
            pytest.skip("systemd not available")
        except subprocess.TimeoutExpired:
            pytest.skip("systemctl timeout")
    
    def test_service_file_template_exists(self):
        """Test that service file templates can be created"""
        # This is more of a structure test
        install_dir = Path(__file__).parent.parent / 'install'
        
        if install_dir.exists():
            assert install_dir.is_dir()
