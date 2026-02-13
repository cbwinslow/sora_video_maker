"""
Tests for Prompt Enhancement Agent
"""

import pytest
from agents.prompt_enhancement_agent import PromptEnhancementAgent


@pytest.fixture
def config():
    """Test configuration"""
    return {
        'prompts': {
            'output_directory': 'test_output/prompts',
            'templates_directory': 'prompts'
        }
    }


@pytest.fixture
def agent(config):
    """Create PromptEnhancementAgent instance"""
    return PromptEnhancementAgent(config)


class TestPromptEnhancementAgent:
    """Test suite for PromptEnhancementAgent"""
    
    def test_init(self, agent, config):
        """Test agent initialization"""
        assert agent.config == config
        assert agent.templates is not None
        assert agent.style_presets is not None
    
    def test_load_templates(self, agent):
        """Test template loading"""
        templates = agent.templates
        
        assert 'cinematic' in templates
        assert 'artistic' in templates
        assert 'realistic' in templates
        assert 'animation' in templates
    
    def test_load_style_presets(self, agent):
        """Test style presets loading"""
        presets = agent.style_presets
        
        assert 'cameras' in presets
        assert 'lenses' in presets
        assert 'lighting' in presets
        assert 'moods' in presets
        
        assert len(presets['cameras']) > 0
        assert len(presets['lighting']) > 0
    
    def test_parse_prompt(self, agent):
        """Test prompt parsing"""
        prompt = "a warrior walking through a forest"
        elements = agent._parse_prompt(prompt)
        
        assert 'subject' in elements
        assert 'action' in elements
        assert 'setting' in elements
        assert elements['action'] == 'walking'
        assert elements['setting'] == 'forest'
    
    def test_enhance_prompt_cinematic(self, agent):
        """Test prompt enhancement with cinematic style"""
        simple_prompt = "a cat in a garden"
        
        result = agent.enhance_prompt(
            simple_prompt,
            style='cinematic',
            creativity=0.5
        )
        
        assert result['original'] == simple_prompt
        assert len(result['enhanced']) > len(simple_prompt)
        assert 'cinematic' in result['enhanced'].lower()
        assert result['negative'] != ""
        assert result['style'] == 'cinematic'
    
    def test_enhance_prompt_artistic(self, agent):
        """Test prompt enhancement with artistic style"""
        simple_prompt = "a mountain landscape"
        
        result = agent.enhance_prompt(
            simple_prompt,
            style='artistic',
            creativity=0.7
        )
        
        assert result['original'] == simple_prompt
        assert len(result['enhanced']) > len(simple_prompt)
        assert result['style'] == 'artistic'
    
    def test_enhance_prompt_no_negative(self, agent):
        """Test prompt enhancement without negative prompt"""
        result = agent.enhance_prompt(
            "test prompt",
            add_negative=False
        )
        
        assert result['negative'] == ""
    
    def test_generate_negative_prompt(self, agent):
        """Test negative prompt generation"""
        negative = agent._generate_negative_prompt('cinematic')
        
        assert len(negative) > 0
        assert 'low quality' in negative
        assert 'blurry' in negative
    
    def test_break_down_scene(self, agent):
        """Test scene breakdown into frames"""
        scene = "a spaceship landing on a planet"
        num_frames = 4
        
        frames = agent.break_down_scene(scene, num_frames=num_frames)
        
        assert len(frames) == num_frames
        
        for i, frame in enumerate(frames):
            assert frame['frame_number'] == i + 1
            assert 'prompt' in frame
            assert 'negative' in frame
            assert 'progress' in frame
            assert 0 <= frame['progress'] <= 1
    
    def test_break_down_scene_single_frame(self, agent):
        """Test scene breakdown into single frame"""
        scene = "a simple scene"
        frames = agent.break_down_scene(scene, num_frames=1)
        
        assert len(frames) == 1
        assert frames[0]['frame_number'] == 1
    
    def test_build_enhanced_prompt_technical(self, agent):
        """Test building enhanced prompt with technical details"""
        elements = {
            'subject': 'robot',
            'action': 'walking',
            'setting': 'city',
            'details': []
        }
        
        enhanced = agent._build_enhanced_prompt(
            elements,
            style='cinematic',
            add_technical=True,
            creativity=0.8
        )
        
        assert 'robot' in enhanced
        assert 'city' in enhanced
        assert len(enhanced) > 20
    
    def test_build_enhanced_prompt_no_technical(self, agent):
        """Test building enhanced prompt without technical details"""
        elements = {
            'subject': 'person',
            'action': '',
            'setting': '',
            'details': []
        }
        
        enhanced = agent._build_enhanced_prompt(
            elements,
            style='artistic',
            add_technical=False,
            creativity=0.5
        )
        
        assert 'person' in enhanced
    
    def test_creativity_levels(self, agent):
        """Test different creativity levels"""
        prompt = "a simple scene"
        
        low_creativity = agent.enhance_prompt(prompt, creativity=0.3)
        high_creativity = agent.enhance_prompt(prompt, creativity=0.9)
        
        # High creativity should generally produce longer, more detailed prompts
        assert len(high_creativity['enhanced']) >= len(low_creativity['enhanced'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
