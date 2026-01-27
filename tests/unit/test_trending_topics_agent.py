"""
Unit tests for TrendingTopicsAgent
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from agents.trending_topics_agent import TrendingTopicsAgent


@pytest.mark.unit
@pytest.mark.agent
class TestTrendingTopicsAgent:
    """Test suite for TrendingTopicsAgent"""
    
    def test_init(self, mock_config):
        """Test agent initialization"""
        agent = TrendingTopicsAgent(mock_config)
        
        assert agent.config == mock_config
        assert agent.sources == mock_config['research']['sources']
        assert agent.topics_to_track == mock_config['research']['topics_to_track']
    
    def test_init_with_empty_config(self):
        """Test initialization with minimal config"""
        agent = TrendingTopicsAgent({})
        
        assert agent.config == {}
        assert agent.sources == []
        assert agent.topics_to_track == 10
    
    @pytest.mark.asyncio
    async def test_fetch_reddit_trends_success(self, mock_config):
        """Test successful Reddit API call"""
        agent = TrendingTopicsAgent(mock_config)
        
        mock_response_data = {
            'data': {
                'children': [
                    {
                        'data': {
                            'title': 'Test Reddit Post',
                            'subreddit': 'technology',
                            'score': 5000,
                            'url': 'https://reddit.com/test'
                        }
                    }
                ]
            }
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            
            mock_get = Mock(return_value=mock_context)
            mock_session.return_value.__aenter__.return_value.get = mock_get
            
            trends = await agent.fetch_reddit_trends()
        
        assert len(trends) == 1
        assert trends[0]['source'] == 'reddit'
        assert trends[0]['title'] == 'Test Reddit Post'
        assert trends[0]['score'] == 5000
    
    @pytest.mark.asyncio
    async def test_fetch_reddit_trends_api_error(self, mock_config):
        """Test Reddit API error handling"""
        agent = TrendingTopicsAgent(mock_config)
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 500
            
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            
            mock_get = Mock(return_value=mock_context)
            mock_session.return_value.__aenter__.return_value.get = mock_get
            
            trends = await agent.fetch_reddit_trends()
        
        assert trends == []
    
    @pytest.mark.asyncio
    async def test_fetch_reddit_trends_exception(self, mock_config):
        """Test Reddit API exception handling"""
        agent = TrendingTopicsAgent(mock_config)
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.side_effect = Exception('Network error')
            
            trends = await agent.fetch_reddit_trends()
        
        assert trends == []
    
    @pytest.mark.asyncio
    async def test_fetch_youtube_trends(self, mock_config):
        """Test YouTube trends fetching"""
        agent = TrendingTopicsAgent(mock_config)
        
        trends = await agent.fetch_youtube_trends()
        
        assert isinstance(trends, list)
        assert len(trends) > 0
        assert all(t['source'] == 'youtube' for t in trends)
    
    @pytest.mark.asyncio
    async def test_fetch_google_trends(self, mock_config):
        """Test Google Trends fetching"""
        agent = TrendingTopicsAgent(mock_config)
        
        trends = await agent.fetch_google_trends()
        
        assert isinstance(trends, list)
        assert len(trends) > 0
        assert all(t['source'] == 'google_trends' for t in trends)
    
    @pytest.mark.asyncio
    async def test_analyze_trends(self, mock_config, sample_trends):
        """Test trend analysis and scoring"""
        agent = TrendingTopicsAgent(mock_config)
        
        scored_trends = await agent.analyze_trends(sample_trends)
        
        assert len(scored_trends) <= agent.topics_to_track
        assert all('video_potential_score' in t for t in scored_trends)
        
        # Check that trends are sorted by score
        scores = [t['video_potential_score'] for t in scored_trends]
        assert scores == sorted(scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_analyze_trends_empty_list(self, mock_config):
        """Test analysis with empty trends list"""
        agent = TrendingTopicsAgent(mock_config)
        
        scored_trends = await agent.analyze_trends([])
        
        assert scored_trends == []
    
    @pytest.mark.asyncio
    async def test_research_full_workflow(self, mock_config):
        """Test full research workflow"""
        agent = TrendingTopicsAgent(mock_config)
        
        with patch.object(agent, 'fetch_reddit_trends', return_value=[
            {'source': 'reddit', 'title': 'Test 1', 'score': 1000}
        ]), \
        patch.object(agent, 'fetch_youtube_trends', return_value=[
            {'source': 'youtube', 'title': 'Test 2', 'category': 'Tech'}
        ]), \
        patch.object(agent, 'fetch_google_trends', return_value=[
            {'source': 'google_trends', 'query': 'Test 3', 'interest': 100}
        ]):
            
            trends = await agent.research()
        
        assert len(trends) > 0
        assert all('video_potential_score' in t for t in trends)
    
    @pytest.mark.asyncio
    async def test_research_with_single_source(self, mock_config):
        """Test research with only one source enabled"""
        mock_config['research']['sources'] = ['reddit']
        agent = TrendingTopicsAgent(mock_config)
        
        with patch.object(agent, 'fetch_reddit_trends', return_value=[
            {'source': 'reddit', 'title': 'Test', 'score': 1000}
        ]):
            trends = await agent.research()
        
        assert len(trends) > 0
        assert all(t['source'] == 'reddit' for t in trends)
    
    def test_save_trends(self, mock_config, temp_dir, sample_trends):
        """Test saving trends to file"""
        import os
        agent = TrendingTopicsAgent(mock_config)
        
        filename = os.path.join(temp_dir, 'test_trends.json')
        agent.save_trends(sample_trends, filename)
        
        assert os.path.exists(filename)
        
        # Verify content
        import json
        with open(filename, 'r') as f:
            loaded_trends = json.load(f)
        
        assert len(loaded_trends) == len(sample_trends)
        assert loaded_trends[0]['source'] == sample_trends[0]['source']
    
    def test_save_trends_invalid_path(self, mock_config, sample_trends):
        """Test saving trends to invalid path"""
        agent = TrendingTopicsAgent(mock_config)
        
        # Should not raise exception, just log error
        agent.save_trends(sample_trends, '/invalid/path/trends.json')
    
    @pytest.mark.asyncio
    async def test_research_handles_exceptions(self, mock_config):
        """Test that research handles individual source failures gracefully"""
        agent = TrendingTopicsAgent(mock_config)
        
        with patch.object(agent, 'fetch_reddit_trends', side_effect=Exception('Reddit error')), \
            patch.object(agent, 'fetch_youtube_trends', return_value=[
                {'source': 'youtube', 'title': 'Test', 'category': 'Tech'}
            ]), \
            patch.object(agent, 'fetch_google_trends', return_value=[]):
            
            trends = await agent.research()
        
        # Should still get results from working sources
        assert len(trends) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_trends_with_large_dataset(self, mock_config):
        """Test trend analysis with more trends than limit"""
        agent = TrendingTopicsAgent(mock_config)
        agent.topics_to_track = 5
        
        large_dataset = [
            {'source': 'reddit', 'title': f'Test {i}', 'score': i * 100}
            for i in range(20)
        ]
        
        scored_trends = await agent.analyze_trends(large_dataset)
        
        assert len(scored_trends) == 5
        assert all('video_potential_score' in t for t in scored_trends)


@pytest.mark.unit
@pytest.mark.agent
class TestTrendingTopicsAgentEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_fetch_reddit_with_missing_fields(self, mock_config):
        """Test handling of Reddit posts with missing fields"""
        agent = TrendingTopicsAgent(mock_config)
        
        mock_response_data = {
            'data': {
                'children': [
                    {
                        'data': {
                            'title': 'Incomplete Post'
                            # Missing score, url, subreddit
                        }
                    }
                ]
            }
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            
            mock_get = Mock(return_value=mock_context)
            mock_session.return_value.__aenter__.return_value.get = mock_get
            
            trends = await agent.fetch_reddit_trends()
        
        assert len(trends) == 1
        assert trends[0]['score'] == 0  # Default value
    
    @pytest.mark.asyncio
    async def test_analyze_trends_scoring_reddit(self, mock_config):
        """Test Reddit trend scoring calculation"""
        agent = TrendingTopicsAgent(mock_config)
        
        trends = [
            {'source': 'reddit', 'score': 10000}
        ]
        
        scored = await agent.analyze_trends(trends)
        
        assert scored[0]['video_potential_score'] == 10000 / 1000  # 10.0
    
    @pytest.mark.asyncio
    async def test_analyze_trends_scoring_youtube(self, mock_config):
        """Test YouTube trend scoring calculation"""
        agent = TrendingTopicsAgent(mock_config)
        
        trends = [
            {'source': 'youtube', 'title': 'Test', 'category': 'Tech'}
        ]
        
        scored = await agent.analyze_trends(trends)
        
        assert scored[0]['video_potential_score'] == 5  # Base score
    
    @pytest.mark.asyncio
    async def test_analyze_trends_scoring_google(self, mock_config):
        """Test Google Trends scoring calculation"""
        agent = TrendingTopicsAgent(mock_config)
        
        trends = [
            {'source': 'google_trends', 'query': 'Test', 'interest': 80}
        ]
        
        scored = await agent.analyze_trends(trends)
        
        assert scored[0]['video_potential_score'] == 80 / 10  # 8.0
