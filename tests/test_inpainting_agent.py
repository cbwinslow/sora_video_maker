"""
Tests for Inpainting Agent
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from agents.inpainting_agent import InpaintingAgent


@pytest.fixture
def config():
    """Test configuration"""
    return {
        'image_generation': {'output_directory': 'test_output/images'},
        'workflow': {'temp_directory': 'test_temp'},
        'comfyui': {'url': 'http://127.0.0.1:8188'}
    }


@pytest.fixture
def agent(config):
    """Create InpaintingAgent instance"""
    return InpaintingAgent(config)


class TestInpaintingAgent:
    """Test suite for InpaintingAgent"""
    
    def test_init(self, agent, config):
        """Test agent initialization"""
        assert agent.config == config
        assert agent.comfyui_url == config['comfyui']['url']
    
    def test_create_inpainting_workflow(self, agent):
        """Test workflow creation"""
        workflow = agent._create_inpainting_workflow(
            'image.png',
            'mask.png',
            'a beautiful landscape',
            'blurry, low quality',
            0.8
        )
        
        assert isinstance(workflow, dict)
        assert '1' in workflow  # CheckpointLoader
        assert '2' in workflow  # LoadImage
        assert '3' in workflow  # LoadMask
        assert '8' in workflow  # KSampler
        
        # Check KSampler has correct denoise strength
        assert workflow['8']['inputs']['denoise'] == 0.8
    
    @patch('agents.inpainting_agent.Image')
    def test_inpaint_fallback(self, mock_image, agent, tmp_path):
        """Test fallback inpainting method"""
        # Mock PIL Image operations
        mock_img = MagicMock()
        mock_mask = MagicMock()
        mock_blurred = MagicMock()
        mock_result = MagicMock()
        
        mock_image.open.side_effect = [mock_img, mock_mask]
        mock_img.convert.return_value = mock_img
        mock_mask.convert.return_value = mock_mask
        mock_img.filter.return_value = mock_blurred
        mock_image.composite.return_value = mock_result
        
        image_path = str(tmp_path / 'image.png')
        mask_path = str(tmp_path / 'mask.png')
        output_path = str(tmp_path / 'output.png')
        
        # Create fake files
        open(image_path, 'w').close()
        open(mask_path, 'w').close()
        
        result = agent._inpaint_fallback(
            image_path,
            mask_path,
            'test prompt',
            output_path
        )
        
        assert result == output_path
    
    def test_remove_object(self, agent):
        """Test object removal"""
        with patch.object(agent, 'inpaint_image') as mock_inpaint:
            mock_inpaint.return_value = 'output.png'
            
            result = agent.remove_object('image.png', 'mask.png')
            
            mock_inpaint.assert_called_once()
            call_args = mock_inpaint.call_args
            
            # Check that it uses appropriate inpainting prompt
            assert 'natural' in call_args[0][2].lower() or 'seamless' in call_args[0][2].lower()
    
    def test_replace_object(self, agent):
        """Test object replacement"""
        with patch.object(agent, 'inpaint_image') as mock_inpaint:
            mock_inpaint.return_value = 'output.png'
            
            result = agent.replace_object(
                'image.png',
                'mask.png',
                'a red car'
            )
            
            mock_inpaint.assert_called_once()
            call_args = mock_inpaint.call_args
            
            assert call_args[0][2] == 'a red car'
            assert call_args[1]['strength'] == 1.0
    
    def test_enhance_region(self, agent):
        """Test region enhancement"""
        with patch.object(agent, 'inpaint_image') as mock_inpaint:
            mock_inpaint.return_value = 'output.png'
            
            result = agent.enhance_region(
                'image.png',
                'mask.png',
                'better details, sharper'
            )
            
            mock_inpaint.assert_called_once()
            call_args = mock_inpaint.call_args
            
            # Enhancement should use lower strength
            assert call_args[1]['strength'] == 0.5
    
    def test_batch_inpaint(self, agent):
        """Test batch inpainting"""
        images = [
            ('image1.png', 'mask1.png', 'prompt1'),
            ('image2.png', 'mask2.png', 'prompt2'),
            ('image3.png', 'mask3.png', 'prompt3')
        ]
        
        with patch.object(agent, 'inpaint_image') as mock_inpaint:
            mock_inpaint.side_effect = ['out1.png', 'out2.png', 'out3.png']
            
            results = agent.batch_inpaint(images)
            
            assert len(results) == 3
            assert mock_inpaint.call_count == 3
    
    def test_batch_inpaint_with_errors(self, agent):
        """Test batch inpainting with some failures"""
        images = [
            ('image1.png', 'mask1.png', 'prompt1'),
            ('image2.png', 'mask2.png', 'prompt2'),
        ]
        
        with patch.object(agent, 'inpaint_image') as mock_inpaint:
            mock_inpaint.side_effect = ['out1.png', Exception('Error')]
            
            results = agent.batch_inpaint(images)
            
            assert len(results) == 2
            assert results[0] == 'out1.png'
            assert results[1] is None
    
    def test_generate_variation(self, agent):
        """Test variation generation"""
        with patch.object(agent, 'inpaint_image') as mock_inpaint:
            mock_inpaint.side_effect = ['var1.png', 'var2.png', 'var3.png']
            
            variations = agent.generate_variation(
                'image.png',
                'mask.png',
                'a tree',
                num_variations=3
            )
            
            assert len(variations) == 3
            assert mock_inpaint.call_count == 3
            
            # Check that different strengths were used
            call_args_list = mock_inpaint.call_args_list
            strengths = [call[1]['strength'] for call in call_args_list]
            
            # Strengths should be different
            assert len(set(strengths)) > 1
    
    def test_create_mask_from_description(self, agent):
        """Test mask creation (placeholder)"""
        mask_path = agent.create_mask_from_description(
            'image.png',
            'person in the center'
        )
        
        # Should return a path (even though not implemented yet)
        assert mask_path is not None
        assert 'mask_' in mask_path


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
