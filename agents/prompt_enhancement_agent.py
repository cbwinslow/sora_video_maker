"""
Prompt Enhancement Agent

AI agent that breaks down user prompts into detailed, production-ready prompts
with all necessary details for high-quality image and video generation.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptEnhancementAgent:
    """Agent for enhancing and expanding user prompts"""

    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = config.get('prompts', {}).get('output_directory', 'output/prompts')
        self.templates_dir = config.get('prompts', {}).get('templates_directory', 'prompts')
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Load templates and styles
        self.templates = self._load_templates()
        self.style_presets = self._load_style_presets()

    def _load_templates(self) -> Dict:
        """Load prompt templates"""
        templates = {
            'cinematic': {
                'prefix': 'cinematic, film grain, dramatic lighting',
                'technical': '8k, ultra detailed, professional photography',
                'camera': 'shot on {camera}, {lens}',
                'lighting': '{lighting_type} lighting, {time_of_day}'
            },
            'artistic': {
                'prefix': 'masterpiece, artistic, highly detailed',
                'technical': 'trending on artstation, award winning',
                'style': 'in the style of {artist}',
                'medium': '{medium}, {technique}'
            },
            'realistic': {
                'prefix': 'photorealistic, highly detailed, sharp focus',
                'technical': '8k resolution, RAW photo, professional',
                'quality': 'best quality, ultra high res'
            },
            'animation': {
                'prefix': 'animated, stylized, smooth motion',
                'technical': 'high frame rate, fluid animation',
                'style': '{animation_style}, {color_palette}'
            }
        }
        
        # Try to load custom templates
        template_file = os.path.join(self.templates_dir, 'templates.json')
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r') as f:
                    custom_templates = json.load(f)
                    templates.update(custom_templates)
            except Exception as e:
                logger.warning(f"Could not load custom templates: {e}")
        
        return templates

    def _load_style_presets(self) -> Dict:
        """Load style presets"""
        return {
            'cameras': [
                'ARRI Alexa', 'RED Dragon', 'Sony A7S III', 'Canon C300',
                'Blackmagic Pocket 6K', 'Panasonic GH5'
            ],
            'lenses': [
                '35mm f/1.4', '50mm f/1.8', '85mm f/1.2', '24-70mm f/2.8',
                'ultra wide angle', 'telephoto lens', 'macro lens'
            ],
            'lighting': [
                'natural', 'golden hour', 'blue hour', 'studio', 'dramatic',
                'soft diffused', 'hard light', 'rim lighting', 'volumetric',
                'neon', 'candlelight', 'moonlight'
            ],
            'times_of_day': [
                'sunrise', 'morning', 'midday', 'afternoon', 'sunset',
                'dusk', 'night', 'midnight'
            ],
            'weather': [
                'clear sky', 'cloudy', 'overcast', 'rainy', 'stormy',
                'foggy', 'snowy', 'misty'
            ],
            'moods': [
                'peaceful', 'dramatic', 'mysterious', 'energetic', 'melancholic',
                'joyful', 'tense', 'serene', 'chaotic', 'romantic'
            ],
            'colors': [
                'warm tones', 'cool tones', 'vibrant colors', 'muted palette',
                'monochromatic', 'complementary colors', 'high contrast',
                'desaturated', 'neon colors'
            ]
        }

    def enhance_prompt(
        self,
        user_prompt: str,
        style: str = 'cinematic',
        add_technical: bool = True,
        add_negative: bool = True,
        creativity: float = 0.7
    ) -> Dict:
        """
        Enhance a simple prompt into a detailed, production-ready prompt
        
        Args:
            user_prompt: The user's basic prompt
            style: Style template to use
            add_technical: Add technical quality terms
            add_negative: Generate negative prompt
            creativity: How creative to be (0.0 to 1.0)
        
        Returns:
            Dictionary with enhanced prompt and metadata
        """
        logger.info(f"Enhancing prompt: {user_prompt}")
        
        # Parse user prompt to extract key elements
        elements = self._parse_prompt(user_prompt)
        
        # Build enhanced prompt
        enhanced = self._build_enhanced_prompt(
            elements,
            style,
            add_technical,
            creativity
        )
        
        # Generate negative prompt
        negative = ""
        if add_negative:
            negative = self._generate_negative_prompt(style)
        
        result = {
            'original': user_prompt,
            'enhanced': enhanced,
            'negative': negative,
            'style': style,
            'elements': elements,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save for reference
        self._save_prompt(result)
        
        logger.info(f"Prompt enhanced successfully")
        return result

    def _parse_prompt(self, prompt: str) -> Dict:
        """Parse prompt to extract key elements"""
        elements = {
            'subject': '',
            'action': '',
            'setting': '',
            'mood': '',
            'details': []
        }
        
        # Simple keyword-based parsing
        words = prompt.lower().split()
        
        # Extract subject (first noun or noun phrase)
        # This is simplified - production would use NLP
        if len(words) > 0:
            elements['subject'] = words[0]
        
        # Look for action verbs
        action_verbs = ['walking', 'running', 'flying', 'sitting', 'standing', 'dancing', 'jumping']
        for verb in action_verbs:
            if verb in prompt.lower():
                elements['action'] = verb
                break
        
        # Look for setting keywords
        setting_keywords = ['forest', 'city', 'beach', 'mountain', 'space', 'room', 'street']
        for keyword in setting_keywords:
            if keyword in prompt.lower():
                elements['setting'] = keyword
                break
        
        # Store full prompt as details if no specific elements found
        if not any([elements['action'], elements['setting']]):
            elements['details'] = [prompt]
        
        return elements

    def _build_enhanced_prompt(
        self,
        elements: Dict,
        style: str,
        add_technical: bool,
        creativity: float
    ) -> str:
        """Build enhanced prompt from elements"""
        parts = []
        
        # Get template
        template = self.templates.get(style, self.templates['cinematic'])
        
        # Add style prefix
        if 'prefix' in template:
            parts.append(template['prefix'])
        
        # Add main subject and details
        if elements.get('subject'):
            parts.append(elements['subject'])
        
        if elements.get('action'):
            parts.append(elements['action'])
        
        if elements.get('setting'):
            parts.append(f"in a {elements['setting']}")
        
        # Add creative details based on creativity level
        if creativity > 0.5:
            # Add lighting
            lighting = self._random_choice(self.style_presets['lighting'])
            parts.append(f"{lighting} lighting")
            
            # Add mood
            mood = self._random_choice(self.style_presets['moods'])
            parts.append(f"{mood} atmosphere")
        
        if creativity > 0.7:
            # Add camera details
            camera = self._random_choice(self.style_presets['cameras'])
            lens = self._random_choice(self.style_presets['lenses'])
            parts.append(f"shot on {camera} with {lens}")
            
            # Add color grading
            colors = self._random_choice(self.style_presets['colors'])
            parts.append(colors)
        
        # Add technical quality terms
        if add_technical and 'technical' in template:
            parts.append(template['technical'])
        
        # Add any remaining details
        for detail in elements.get('details', []):
            if detail not in parts:
                parts.append(detail)
        
        # Join all parts
        enhanced = ', '.join(parts)
        
        return enhanced

    def _generate_negative_prompt(self, style: str) -> str:
        """Generate appropriate negative prompt"""
        base_negative = [
            "low quality", "blurry", "distorted", "disfigured",
            "poorly drawn", "bad anatomy", "artifacts", "watermark"
        ]
        
        style_specific = {
            'cinematic': ["amateur", "home video", "low resolution"],
            'realistic': ["cartoon", "anime", "painting", "drawing"],
            'artistic': ["photograph", "realistic", "plain"],
            'animation': ["photograph", "realistic", "live action"]
        }
        
        negative_parts = base_negative.copy()
        if style in style_specific:
            negative_parts.extend(style_specific[style])
        
        return ', '.join(negative_parts)

    def break_down_scene(
        self,
        scene_description: str,
        num_frames: int = 4
    ) -> List[Dict]:
        """Break down a scene into individual frames with detailed prompts"""
        logger.info(f"Breaking down scene into {num_frames} frames")
        
        frames = []
        
        # Parse scene
        elements = self._parse_prompt(scene_description)
        
        # Generate frame progression
        for i in range(num_frames):
            progress = i / (num_frames - 1) if num_frames > 1 else 0
            
            frame_prompt = self._generate_frame_prompt(
                elements,
                i,
                progress
            )
            
            frames.append({
                'frame_number': i + 1,
                'progress': progress,
                'prompt': frame_prompt['enhanced'],
                'negative': frame_prompt['negative'],
                'description': f"Frame {i+1} of {num_frames}"
            })
        
        logger.info(f"Scene broken down into {len(frames)} frames")
        return frames

    def _generate_frame_prompt(
        self,
        base_elements: Dict,
        frame_num: int,
        progress: float
    ) -> Dict:
        """Generate prompt for specific frame"""
        # Modify elements based on progress
        elements = base_elements.copy()
        
        # Add frame-specific details
        if progress < 0.25:
            elements['details'].append("establishing shot")
        elif progress < 0.75:
            elements['details'].append("mid shot, main action")
        else:
            elements['details'].append("closing shot")
        
        # Enhance for this frame
        return self.enhance_prompt(
            ' '.join([
                elements.get('subject', ''),
                elements.get('action', ''),
                elements.get('setting', ''),
                *elements.get('details', [])
            ]),
            style='cinematic'
        )

    def _random_choice(self, options: List[str]) -> str:
        """Randomly choose from options (deterministic based on time)"""
        import random
        random.seed(datetime.now().microsecond)
        return random.choice(options)

    def _save_prompt(self, prompt_data: Dict):
        """Save enhanced prompt for reference"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(self.output_dir, f"prompt_{timestamp}.json")
        
        try:
            with open(filename, 'w') as f:
                json.dump(prompt_data, f, indent=2)
            logger.debug(f"Prompt saved: {filename}")
        except Exception as e:
            logger.warning(f"Could not save prompt: {e}")

    def research_prompt(self, topic: str) -> str:
        """Research topic and generate informed prompt (placeholder)"""
        logger.info(f"Researching topic: {topic}")
        
        # TODO: Integrate with web search API
        # For now, use template-based approach
        
        return f"highly detailed {topic}, professional quality, cinematic lighting"

    def analyze_successful_prompts(self, examples_dir: str) -> Dict:
        """Analyze successful prompts to learn patterns"""
        logger.info(f"Analyzing prompts from: {examples_dir}")
        
        patterns = {
            'common_keywords': [],
            'technical_terms': [],
            'style_preferences': []
        }
        
        # TODO: Implement pattern analysis
        
        return patterns


def main():
    """Example usage"""
    config = {
        'prompts': {
            'output_directory': 'output/prompts',
            'templates_directory': 'prompts'
        }
    }
    
    agent = PromptEnhancementAgent(config)
    
    print("Prompt Enhancement Agent - Ready")
    print("\nExample: Enhance a simple prompt")
    print("=" * 50)
    
    # Example enhancement
    simple_prompt = "a cat in a garden"
    result = agent.enhance_prompt(simple_prompt, style='cinematic', creativity=0.8)
    
    print(f"Original: {result['original']}")
    print(f"\nEnhanced: {result['enhanced']}")
    print(f"\nNegative: {result['negative']}")
    
    print("\n" + "=" * 50)
    print("\nExample: Break down scene into frames")
    print("=" * 50)
    
    scene = "a hero walking through a futuristic city"
    frames = agent.break_down_scene(scene, num_frames=4)
    
    for frame in frames:
        print(f"\nFrame {frame['frame_number']}: {frame['description']}")
        print(f"Prompt: {frame['prompt'][:100]}...")


if __name__ == '__main__':
    main()
