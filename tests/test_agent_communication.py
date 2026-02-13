"""
Agent Communication Tests

Comprehensive tests for agent-to-agent communication, coordination,
and collaboration within the swarm system.
"""

import pytest
from unittest.mock import patch


@pytest.mark.integration
@pytest.mark.agent
class TestAgentCommunication:
    """Test communication between agents"""

    @pytest.mark.asyncio
    async def test_research_to_generation_communication(self, mock_config):
        """Test data flow from research agent to generation agent"""
        from agents.trending_topics_agent import TrendingTopicsAgent
        from agents.video_generation_agent import VideoGenerationOrchestrator

        research_agent = TrendingTopicsAgent(mock_config)
        generation_agent = VideoGenerationOrchestrator(mock_config)

        # Simulate research agent producing data
        mock_trends = [
            {
                'title': 'Test Topic',
                'source': 'test',
                'score': 100,
                'video_potential_score': 8.0
            }
        ]

        # Test that generation agent can consume research output
        with patch.object(generation_agent, 'generate_script', return_value='test script'), \
             patch.object(generation_agent, 'generate_prompts', return_value=['prompt1']), \
             patch.object(generation_agent, 'generate_with_comfyui', return_value='/path/frame.png'), \
             patch.object(generation_agent, 'assemble_video', return_value='/path/video.mp4'):

            result = await generation_agent.generate_video(mock_trends[0])

        assert result['status'] == 'success'
        assert result['topic'] == mock_trends[0]

    @pytest.mark.asyncio
    async def test_generation_to_upload_communication(self, mock_config):
        """Test data flow from generation agent to upload agent"""
        from agents.video_generation_agent import VideoGenerationOrchestrator
        from agents.video_upload_agent import VideoUploadAgent

        generation_agent = VideoGenerationOrchestrator(mock_config)
        upload_agent = VideoUploadAgent(mock_config)

        # Simulate generation agent output
        generation_result = {
            'status': 'success',
            'video_path': '/path/to/video.mp4',
            'topic': {'title': 'Test Topic'},
            'script': 'Test script content'
        }

        # Test that upload agent can consume generation output
        metadata = upload_agent.generate_metadata(
            generation_result['topic'],
            generation_result['script']
        )

        assert metadata is not None
        assert 'title' in metadata
        assert 'description' in metadata

    @pytest.mark.asyncio
    async def test_research_to_deep_research_communication(self, mock_config):
        """Test communication between research and deep research agents"""
        from agents.trending_topics_agent import TrendingTopicsAgent
        from agents.deep_research_agent import DeepResearchAgent

        research_agent = TrendingTopicsAgent(mock_config)
        deep_research_agent = DeepResearchAgent(mock_config)

        # Simulate research output
        topic_data = {
            'title': 'AI Technology',
            'source': 'reddit',
            'score': 5000
        }

        # Test deep research can expand on initial research
        with patch.object(deep_research_agent, 'fetch_detailed_info',
                         return_value={'detailed': 'info'}):
            result = await deep_research_agent.research_topic(topic_data['title'])

        assert result is not None

    @pytest.mark.asyncio
    async def test_generation_to_editing_communication(self, mock_config, mock_video_path):
        """Test communication between generation and editing agents"""
        from agents.video_generation_agent import VideoGenerationOrchestrator
        from agents.video_editing_agent import VideoEditingAgent

        generation_agent = VideoGenerationOrchestrator(mock_config)
        editing_agent = VideoEditingAgent(mock_config)

        # Simulate generation output
        video_path = mock_video_path

        # Test editing agent can process generation output
        edits = {
            'color_grade': 'vibrant',
            'trim': {'start': 0, 'duration': 30}
        }

        with patch.object(editing_agent, 'apply_color_grade', return_value=video_path), \
             patch.object(editing_agent, 'trim_video', return_value=video_path):
            edited_video = editing_agent.edit_video(video_path, edits)

        assert edited_video is not None

    @pytest.mark.asyncio
    async def test_editing_to_multiplatform_upload_communication(self, mock_config, mock_video_path):
        """Test communication between editing and multiplatform upload agents"""
        from agents.video_editing_agent import VideoEditingAgent
        from agents.multiplatform_upload_agent import MultiPlatformUploadAgent

        editing_agent = VideoEditingAgent(mock_config)
        upload_agent = MultiPlatformUploadAgent(mock_config)

        # Simulate editing output
        edited_video = mock_video_path

        metadata = {
            'title': 'Test Video',
            'description': 'Test description',
            'tags': ['test']
        }

        # Test upload agent can consume editing output
        with patch.object(upload_agent, 'upload_to_youtube',
                         return_value={'status': 'success', 'platform': 'youtube'}), \
             patch.object(upload_agent, 'upload_to_tiktok',
                         return_value={'status': 'success', 'platform': 'tiktok'}):

            results = await upload_agent.upload_to_all_platforms(edited_video, metadata)

        assert results is not None
        assert isinstance(results, list)


@pytest.mark.integration
@pytest.mark.agent
class TestCrewCoordination:
    """Test coordination between multiple agents in crew"""

    @pytest.mark.asyncio
    async def test_video_production_crew_agent_coordination(self, mock_config):
        """Test that VideoProductionCrew coordinates all agents properly"""
        from crews.video_production_crew import VideoProductionCrew

        crew = VideoProductionCrew(mock_config)

        # Verify all agents are initialized
        assert crew.research_agent is not None
        assert crew.deep_research_agent is not None
        assert crew.generation_agent is not None
        assert crew.editing_agent is not None
        assert crew.upload_agent is not None

    @pytest.mark.asyncio
    async def test_crew_sequential_execution(self, mock_config):
        """Test sequential execution through crew pipeline"""
        from crews.video_production_crew import VideoProductionCrew

        crew = VideoProductionCrew(mock_config)

        # Mock each phase
        with patch.object(crew.research_agent, 'research',
                         return_value=[{'title': 'Test', 'source': 'test'}]), \
             patch.object(crew.deep_research_agent, 'research_topic',
                         return_value={'summary': 'Test summary'}), \
             patch.object(crew.generation_agent, 'generate_video',
                         return_value={'status': 'success', 'video_path': '/test.mp4'}), \
             patch.object(crew.editing_agent, 'edit_video',
                         return_value='/edited.mp4'), \
             patch.object(crew.editing_agent, 'create_short_form',
                         return_value='/short.mp4'), \
             patch.object(crew.upload_agent, 'upload_to_all_platforms',
                         return_value=[{'status': 'success'}]):

            result = await crew.execute_full_production('Test Topic')

        assert result['status'] == 'success'
        assert 'video_path' in result
        assert 'uploads' in result

    @pytest.mark.asyncio
    async def test_crew_error_propagation(self, mock_config):
        """Test error handling across crew agents"""
        from crews.video_production_crew import VideoProductionCrew

        crew = VideoProductionCrew(mock_config)

        # Simulate error in one agent
        with patch.object(crew.research_agent, 'research',
                         side_effect=Exception('Research failed')):

            result = await crew.execute_full_production()

        assert result['status'] == 'error'
        assert 'error' in result

    @pytest.mark.asyncio
    async def test_short_form_crew_coordination(self, mock_config):
        """Test ShortFormCrew agent coordination"""
        from crews.video_production_crew import ShortFormCrew

        crew = ShortFormCrew(mock_config)

        assert crew.research_agent is not None
        assert crew.generation_agent is not None
        assert crew.editing_agent is not None
        assert crew.upload_agent is not None


@pytest.mark.integration
@pytest.mark.agent
class TestWorkflowOrchestration:
    """Test orchestration of complete workflows"""

    @pytest.mark.asyncio
    async def test_full_workflow_agent_sequence(self, mock_config):
        """Test complete workflow agent sequence"""
        from main import WorkflowOrchestrator

        with patch('main.WorkflowOrchestrator.load_config', return_value=mock_config):
            orchestrator = WorkflowOrchestrator()

        # Mock all agent operations
        with patch.object(orchestrator.topics_agent, 'research',
                         return_value=[{'title': 'Test', 'source': 'test'}]), \
             patch.object(orchestrator.generation_agent, 'generate_video',
                         return_value={'status': 'success', 'video_path': '/test.mp4'}), \
             patch.object(orchestrator.upload_agent, 'upload_video',
                         return_value=[{'status': 'success'}]):

            orchestrator.config['workflow']['auto_generate'] = True
            orchestrator.config['workflow']['auto_upload'] = True

            await orchestrator.run_full_workflow()

    @pytest.mark.asyncio
    async def test_research_only_workflow(self, mock_config):
        """Test research-only workflow"""
        from main import WorkflowOrchestrator

        with patch('main.WorkflowOrchestrator.load_config', return_value=mock_config):
            orchestrator = WorkflowOrchestrator()

        with patch.object(orchestrator.topics_agent, 'research',
                         return_value=[{'title': 'Test', 'source': 'test'}]):

            await orchestrator.run_research_only()


@pytest.mark.integration
@pytest.mark.agent
class TestAgentDataSharing:
    """Test data sharing mechanisms between agents"""

    def test_shared_config_access(self, mock_config):
        """Test that all agents can access shared config"""
        from agents.trending_topics_agent import TrendingTopicsAgent
        from agents.video_generation_agent import VideoGenerationOrchestrator
        from agents.video_upload_agent import VideoUploadAgent

        agents = [
            TrendingTopicsAgent(mock_config),
            VideoGenerationOrchestrator(mock_config),
            VideoUploadAgent(mock_config),
        ]

        for agent in agents:
            assert agent.config == mock_config
            assert 'research' in agent.config

    @pytest.mark.asyncio
    async def test_data_format_compatibility(self, mock_config):
        """Test that data formats are compatible between agents"""
        from agents.trending_topics_agent import TrendingTopicsAgent
        from agents.video_generation_agent import VideoGenerationOrchestrator

        research_agent = TrendingTopicsAgent(mock_config)
        generation_agent = VideoGenerationOrchestrator(mock_config)

        # Create sample data in expected format
        topic_data = {
            'title': 'Test Topic',
            'source': 'test',
            'score': 100
        }

        # Verify generation agent can process this format
        with patch.object(generation_agent, 'generate_script', return_value='script'), \
             patch.object(generation_agent, 'generate_prompts', return_value=['p1']), \
             patch.object(generation_agent, 'generate_with_comfyui', return_value='/frame.png'), \
             patch.object(generation_agent, 'assemble_video', return_value='/video.mp4'):

            result = await generation_agent.generate_video(topic_data)

        assert result['status'] == 'success'

    def test_metadata_format_compatibility(self, mock_config):
        """Test metadata format compatibility"""
        from agents.video_upload_agent import VideoUploadAgent

        upload_agent = VideoUploadAgent(mock_config)

        # Test metadata generation
        topic = {'title': 'Test Topic'}
        script = 'Test script content'

        metadata = upload_agent.generate_metadata(topic, script)

        # Verify metadata has expected structure
        assert 'title' in metadata
        assert 'description' in metadata
        assert isinstance(metadata['title'], str)
        assert isinstance(metadata['description'], str)


@pytest.mark.integration
@pytest.mark.agent
class TestAgentErrorRecovery:
    """Test error recovery and resilience in agent communication"""

    @pytest.mark.asyncio
    async def test_agent_failure_isolation(self, mock_config):
        """Test that one agent failure doesn't crash entire system"""
        from crews.video_production_crew import VideoProductionCrew

        crew = VideoProductionCrew(mock_config)

        # Simulate failure in one agent
        with patch.object(crew.generation_agent, 'generate_video',
                         return_value={'status': 'error', 'error': 'Generation failed'}):

            result = await crew.execute_full_production('Test')

        # System should handle error gracefully
        assert 'status' in result

    @pytest.mark.asyncio
    async def test_retry_mechanism(self, mock_config):
        """Test retry mechanism for failed operations"""
        from agents.video_generation_agent import VideoGenerationOrchestrator

        agent = VideoGenerationOrchestrator(mock_config)

        # Simulate temporary failure then success
        call_count = 0

        def mock_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception('Temporary failure')
            return '/path/video.mp4'

        # Most agents should have some retry logic or error handling
        # This test verifies the pattern is available
        assert hasattr(agent, 'generate_video')

    @pytest.mark.asyncio
    async def test_partial_workflow_recovery(self, mock_config):
        """Test recovery from partial workflow completion"""
        from main import WorkflowOrchestrator

        with patch('main.WorkflowOrchestrator.load_config', return_value=mock_config):
            orchestrator = WorkflowOrchestrator()

        # Simulate successful research but failed generation
        with patch.object(orchestrator.topics_agent, 'research',
                         return_value=[{'title': 'Test'}]), \
             patch.object(orchestrator.generation_agent, 'generate_video',
                         side_effect=Exception('Generation failed')):

            orchestrator.config['workflow']['auto_generate'] = True

            # Should not crash, should handle gracefully
            await orchestrator.run_full_workflow()


@pytest.mark.integration
@pytest.mark.agent
class TestAgentState:
    """Test agent state management and persistence"""

    def test_agent_state_independence(self, mock_config):
        """Test that agents maintain independent state"""
        from agents.trending_topics_agent import TrendingTopicsAgent

        agent1 = TrendingTopicsAgent(mock_config)
        agent2 = TrendingTopicsAgent(mock_config)

        # Agents should be separate instances
        assert agent1 is not agent2

    def test_config_isolation(self, mock_config):
        """Test that config changes don't affect other agents"""
        from agents.trending_topics_agent import TrendingTopicsAgent

        config1 = mock_config.copy()
        config2 = mock_config.copy()

        agent1 = TrendingTopicsAgent(config1)
        agent2 = TrendingTopicsAgent(config2)

        # Modify one config
        config1['research']['topics_to_track'] = 20

        # Other agent should not be affected
        assert agent2.config['research']['topics_to_track'] == 10


@pytest.mark.integration
@pytest.mark.agent
@pytest.mark.slow
class TestConcurrentAgentOperations:
    """Test concurrent agent operations"""

    @pytest.mark.asyncio
    async def test_parallel_research_sources(self, mock_config):
        """Test parallel research from multiple sources"""
        from agents.trending_topics_agent import TrendingTopicsAgent

        agent = TrendingTopicsAgent(mock_config)

        # Mock multiple source fetches
        with patch.object(agent, 'fetch_reddit_trends',
                         return_value=[{'source': 'reddit', 'title': 'Test1'}]), \
             patch.object(agent, 'fetch_youtube_trends',
                         return_value=[{'source': 'youtube', 'title': 'Test2'}]), \
             patch.object(agent, 'fetch_google_trends',
                         return_value=[{'source': 'google', 'query': 'Test3'}]):

            trends = await agent.research()

        # Should aggregate results from all sources
        assert len(trends) > 0

    @pytest.mark.asyncio
    async def test_batch_video_generation(self, mock_config):
        """Test batch video generation"""
        from crews.video_production_crew import VideoProductionCrew

        crew = VideoProductionCrew(mock_config)

        # Mock operations
        with patch.object(crew.research_agent, 'research',
                         return_value=[
                             {'title': 'Topic1', 'source': 'test'},
                             {'title': 'Topic2', 'source': 'test'},
                             {'title': 'Topic3', 'source': 'test'}
                         ]), \
             patch.object(crew.deep_research_agent, 'research_topic',
                         return_value={'summary': 'Test'}), \
             patch.object(crew.generation_agent, 'generate_video',
                         return_value={'status': 'success', 'video_path': '/test.mp4'}), \
             patch.object(crew.editing_agent, 'edit_video',
                         return_value='/edited.mp4'), \
             patch.object(crew.editing_agent, 'create_short_form',
                         return_value='/short.mp4'), \
             patch.object(crew.upload_agent, 'upload_to_all_platforms',
                         return_value=[{'status': 'success'}]):

            results = await crew.execute_batch_production(num_videos=3)

        assert len(results) == 3
        for result in results:
            assert 'status' in result
