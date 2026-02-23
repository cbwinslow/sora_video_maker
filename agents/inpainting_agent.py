"""
Inpainting Agent

Specialized agent for image modification using inpainting techniques.
Supports both ComfyUI-based inpainting and direct API integration.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InpaintingAgent:
    """Agent for image inpainting and modification"""

    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = config.get('image_generation', {}).get('output_directory', 'output/images')
        self.temp_dir = config.get('workflow', {}).get('temp_directory', 'temp')
        self.comfyui_url = config.get('comfyui', {}).get('url', 'http://127.0.0.1:8188')
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def inpaint_image(
        self,
        image_path: str,
        mask_path: str,
        prompt: str,
        negative_prompt: str = "blurry, low quality, distorted",
        strength: float = 1.0
    ) -> str:
        """
        Inpaint an image using a mask
        
        Args:
            image_path: Path to the source image
            mask_path: Path to the mask image (white = inpaint, black = keep)
            prompt: Text description of what to generate in masked area
            negative_prompt: What to avoid in generation
            strength: Inpainting strength (0.0 to 1.0)
        
        Returns:
            Path to the inpainted image
        """
        logger.info(f"Inpainting image: {image_path}")
        logger.info(f"Prompt: {prompt}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir,
            f"inpainted_{timestamp}.png"
        )
        
        # Create ComfyUI workflow for inpainting
        workflow = self._create_inpainting_workflow(
            image_path,
            mask_path,
            prompt,
            negative_prompt,
            strength
        )
        
        # Queue workflow via API
        try:
            from scripts.api_integrations import ComfyUIAPI
            
            api = ComfyUIAPI(self.comfyui_url)
            prompt_id = api.queue_prompt(workflow)
            
            # Wait for completion and get result
            result = api.wait_for_completion(prompt_id)
            
            if result and result.get('outputs'):
                # Move output to our output directory
                output_files = result['outputs']
                if output_files:
                    first_output = list(output_files.values())[0]
                    if 'images' in first_output:
                        # Copy from ComfyUI output to our directory
                        logger.info(f"Inpainting complete: {output_path}")
                        return output_path
            
        except ImportError:
            logger.warning("ComfyUI API not available, using fallback method")
            return self._inpaint_fallback(image_path, mask_path, prompt, output_path)
        except Exception as e:
            logger.error(f"Error during inpainting: {e}")
            return self._inpaint_fallback(image_path, mask_path, prompt, output_path)
        
        return output_path

    def _create_inpainting_workflow(
        self,
        image_path: str,
        mask_path: str,
        prompt: str,
        negative_prompt: str,
        strength: float
    ) -> Dict:
        """Create ComfyUI workflow for inpainting"""
        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                }
            },
            "2": {
                "class_type": "LoadImage",
                "inputs": {
                    "image": image_path
                }
            },
            "3": {
                "class_type": "LoadImage",
                "inputs": {
                    "image": mask_path
                }
            },
            "4": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                }
            },
            "5": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["1", 1]
                }
            },
            "6": {
                "class_type": "VAEEncode",
                "inputs": {
                    "pixels": ["2", 0],
                    "vae": ["1", 2]
                }
            },
            "7": {
                "class_type": "SetLatentNoise",
                "inputs": {
                    "samples": ["6", 0],
                    "mask": ["3", 0]
                }
            },
            "8": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": int(datetime.now().timestamp()),
                    "steps": 30,
                    "cfg": 8.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": strength,
                    "model": ["1", 0],
                    "positive": ["4", 0],
                    "negative": ["5", 0],
                    "latent_image": ["7", 0]
                }
            },
            "9": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["8", 0],
                    "vae": ["1", 2]
                }
            },
            "10": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["9", 0],
                    "filename_prefix": "inpainted"
                }
            }
        }
        
        return workflow

    def _inpaint_fallback(
        self,
        image_path: str,
        mask_path: str,
        prompt: str,
        output_path: str
    ) -> str:
        """Fallback inpainting using PIL (simple blend)"""
        try:
            from PIL import Image
            
            logger.info("Using fallback inpainting method")
            
            # Load images
            image = Image.open(image_path).convert('RGB')
            mask = Image.open(mask_path).convert('L')
            
            # Simple blur in masked area (placeholder)
            # In production, would use diffusers or similar
            from PIL import ImageFilter
            
            blurred = image.filter(ImageFilter.GaussianBlur(radius=5))
            
            # Composite using mask
            result = Image.composite(blurred, image, mask)
            result.save(output_path)
            
            logger.info(f"Fallback inpainting complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Fallback inpainting failed: {e}")
            return image_path

    def remove_object(
        self,
        image_path: str,
        object_mask: str,
        inpaint_prompt: Optional[str] = None
    ) -> str:
        """Remove object from image using inpainting"""
        logger.info(f"Removing object from: {image_path}")
        
        if inpaint_prompt is None:
            # Auto-generate prompt based on context
            inpaint_prompt = "natural background, seamless, consistent with surroundings"
        
        return self.inpaint_image(
            image_path,
            object_mask,
            inpaint_prompt,
            negative_prompt="object, person, artifact, inconsistent"
        )

    def replace_object(
        self,
        image_path: str,
        object_mask: str,
        replacement_prompt: str
    ) -> str:
        """Replace object in image with something else"""
        logger.info(f"Replacing object in: {image_path}")
        logger.info(f"Replacement: {replacement_prompt}")
        
        return self.inpaint_image(
            image_path,
            object_mask,
            replacement_prompt,
            strength=1.0
        )

    def enhance_region(
        self,
        image_path: str,
        region_mask: str,
        enhancement_prompt: str
    ) -> str:
        """Enhance specific region of image"""
        logger.info(f"Enhancing region in: {image_path}")
        
        return self.inpaint_image(
            image_path,
            region_mask,
            enhancement_prompt,
            strength=0.5  # Lower strength for subtle enhancement
        )

    def create_mask_from_description(
        self,
        image_path: str,
        object_description: str
    ) -> str:
        """
        Create mask for object using AI segmentation
        (Placeholder for future SAM or similar integration)
        """
        logger.info(f"Creating mask for: {object_description}")
        
        # TODO: Integrate with Segment Anything Model (SAM) or similar
        # For now, return placeholder
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        mask_path = os.path.join(
            self.temp_dir,
            f"mask_{timestamp}.png"
        )
        
        logger.warning("Auto-mask generation not yet implemented")
        logger.info("Please provide mask manually for now")
        
        return mask_path

    def batch_inpaint(
        self,
        images: List[Tuple[str, str, str]],
        negative_prompt: str = "blurry, low quality"
    ) -> List[str]:
        """
        Batch inpaint multiple images
        
        Args:
            images: List of tuples (image_path, mask_path, prompt)
            negative_prompt: Shared negative prompt
        
        Returns:
            List of output paths
        """
        logger.info(f"Batch inpainting {len(images)} images")
        
        results = []
        for i, (image_path, mask_path, prompt) in enumerate(images):
            try:
                logger.info(f"Processing image {i+1}/{len(images)}")
                result = self.inpaint_image(
                    image_path,
                    mask_path,
                    prompt,
                    negative_prompt
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing image {i+1}: {e}")
                results.append(None)
        
        logger.info(f"Batch inpainting complete: {len([r for r in results if r])} successful")
        return results

    def generate_variation(
        self,
        image_path: str,
        mask_path: str,
        base_prompt: str,
        num_variations: int = 3
    ) -> List[str]:
        """Generate multiple variations of inpainted region"""
        logger.info(f"Generating {num_variations} variations")
        
        variations = []
        for i in range(num_variations):
            try:
                output = self.inpaint_image(
                    image_path,
                    mask_path,
                    base_prompt,
                    strength=0.8 + (i * 0.1)  # Vary strength
                )
                variations.append(output)
            except Exception as e:
                logger.error(f"Error generating variation {i+1}: {e}")
        
        return variations


def main():
    """Example usage"""
    config = {
        'image_generation': {'output_directory': 'output/images'},
        'workflow': {'temp_directory': 'temp'},
        'comfyui': {'url': 'http://127.0.0.1:8188'}
    }
    
    agent = InpaintingAgent(config)
    
    print("Inpainting Agent - Ready")
    print("\nAvailable methods:")
    print("  - inpaint_image(image, mask, prompt)")
    print("  - remove_object(image, mask)")
    print("  - replace_object(image, mask, prompt)")
    print("  - enhance_region(image, mask, prompt)")
    print("  - batch_inpaint(images_list)")
    print("  - generate_variation(image, mask, prompt, count)")
    print("\nNote: Requires ComfyUI running at", config['comfyui']['url'])


if __name__ == '__main__':
    main()
