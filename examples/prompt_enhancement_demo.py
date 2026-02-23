"""
Example: Prompt Enhancement Workflow

Demonstrates how to use the Prompt Enhancement Agent to:
1. Enhance simple prompts into detailed ones
2. Break down scenes into frames
3. Generate video scripts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.prompt_enhancement_agent import PromptEnhancementAgent
import json


def demo_prompt_enhancement():
    """Demonstrate prompt enhancement"""
    config = {
        'prompts': {
            'output_directory': 'output/prompts',
            'templates_directory': 'prompts'
        }
    }
    
    agent = PromptEnhancementAgent(config)
    
    print("=" * 70)
    print("Prompt Enhancement Demo")
    print("=" * 70)
    print()
    
    # Example 1: Simple character prompt
    print("Example 1: Character Scene")
    print("-" * 70)
    simple_prompt = "a warrior standing on a mountain"
    
    result = agent.enhance_prompt(
        simple_prompt,
        style='cinematic',
        creativity=0.8
    )
    
    print(f"Original: {result['original']}")
    print()
    print(f"Enhanced: {result['enhanced']}")
    print()
    print(f"Negative: {result['negative']}")
    print()
    print()
    
    # Example 2: Scene breakdown
    print("Example 2: Scene Breakdown into Frames")
    print("-" * 70)
    scene = "a spaceship landing on an alien planet at sunrise"
    
    frames = agent.break_down_scene(scene, num_frames=4)
    
    print(f"Scene: {scene}")
    print()
    print("Frame breakdown:")
    for i, frame in enumerate(frames, 1):
        print(f"\nFrame {i}:")
        print(f"  {frame['prompt'][:150]}...")
    print()
    print()
    
    # Example 3: Different styles
    print("Example 3: Same Prompt, Different Styles")
    print("-" * 70)
    base_prompt = "a magical forest at night"
    
    styles = ['cinematic', 'artistic', 'realistic']
    
    for style in styles:
        result = agent.enhance_prompt(base_prompt, style=style, creativity=0.6)
        print(f"\nStyle: {style}")
        print(f"Enhanced: {result['enhanced'][:120]}...")
    
    print()
    print()


def interactive_prompt_enhancement():
    """Interactive prompt enhancement"""
    config = {
        'prompts': {
            'output_directory': 'output/prompts',
            'templates_directory': 'prompts'
        }
    }
    
    agent = PromptEnhancementAgent(config)
    
    print("=" * 70)
    print("Interactive Prompt Enhancement")
    print("=" * 70)
    print()
    
    while True:
        print("\nOptions:")
        print("  1. Enhance a prompt")
        print("  2. Break down a scene into frames")
        print("  3. Exit")
        print()
        
        choice = input("Choose (1-3): ").strip()
        
        if choice == '1':
            prompt = input("\nEnter your prompt: ").strip()
            if not prompt:
                print("❌ No prompt entered")
                continue
            
            print("\nChoose style:")
            print("  1. Cinematic")
            print("  2. Artistic")
            print("  3. Realistic")
            print("  4. Animation")
            
            style_choice = input("Style (1-4, default 1): ").strip() or '1'
            styles = {'1': 'cinematic', '2': 'artistic', '3': 'realistic', '4': 'animation'}
            style = styles.get(style_choice, 'cinematic')
            
            creativity = input("Creativity level (0.0-1.0, default 0.7): ").strip()
            try:
                creativity = float(creativity) if creativity else 0.7
                creativity = max(0.0, min(1.0, creativity))
            except ValueError:
                creativity = 0.7
            
            print("\nEnhancing...")
            result = agent.enhance_prompt(prompt, style=style, creativity=creativity)
            
            print("\n" + "=" * 70)
            print(f"Original: {result['original']}")
            print()
            print(f"Enhanced:\n{result['enhanced']}")
            print()
            print(f"Negative:\n{result['negative']}")
            print("=" * 70)
            
            # Save option
            save = input("\nSave this prompt? (y/n): ").strip().lower()
            if save == 'y':
                filename = f"enhanced_{result['timestamp']}.json"
                filepath = os.path.join('output/prompts', filename)
                os.makedirs('output/prompts', exist_ok=True)
                
                with open(filepath, 'w') as f:
                    json.dump(result, f, indent=2)
                
                print(f"✓ Saved to: {filepath}")
        
        elif choice == '2':
            scene = input("\nEnter scene description: ").strip()
            if not scene:
                print("❌ No scene entered")
                continue
            
            num_frames = input("Number of frames (default 4): ").strip()
            try:
                num_frames = int(num_frames) if num_frames else 4
            except ValueError:
                num_frames = 4
            
            print(f"\nBreaking down scene into {num_frames} frames...")
            frames = agent.break_down_scene(scene, num_frames=num_frames)
            
            print("\n" + "=" * 70)
            print(f"Scene: {scene}")
            print()
            
            for frame in frames:
                print(f"\n{'='*70}")
                print(f"Frame {frame['frame_number']} ({frame['description']})")
                print(f"{'='*70}")
                print(f"\nPrompt:\n{frame['prompt']}")
                print(f"\nNegative:\n{frame['negative']}")
            
            print("\n" + "=" * 70)
        
        elif choice == '3':
            print("\nGoodbye!")
            break
        
        else:
            print("❌ Invalid choice")


def main():
    """Main example"""
    print("\nPrompt Enhancement Examples")
    print("=" * 70)
    print()
    print("Choose mode:")
    print("  1. Run demo")
    print("  2. Interactive mode")
    print()
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == '1':
        demo_prompt_enhancement()
    elif choice == '2':
        interactive_prompt_enhancement()
    else:
        print("❌ Invalid choice")


if __name__ == '__main__':
    main()
