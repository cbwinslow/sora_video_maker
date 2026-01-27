"""
Test API Connections

This script tests connections to all configured APIs and services.
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.api_integrations import OllamaAPI, ComfyUIAPI


async def test_ollama():
    """Test Ollama connection"""
    print("\n1. Testing Ollama...")
    print("-" * 40)
    
    try:
        ollama = OllamaAPI()
        models = await ollama.list_models()
        
        if models:
            print(f"✓ Ollama is running")
            print(f"  Available models: {', '.join(models)}")
            
            # Test text generation
            response = await ollama.generate_text(
                "Say hello in one sentence.",
                models[0]
            )
            print(f"  Test response: {response[:100]}...")
        else:
            print("✗ Ollama is not running or no models installed")
            print("  Run: ollama serve")
            print("  Then: ollama pull llama2")
    except Exception as e:
        print(f"✗ Error connecting to Ollama: {e}")


async def test_comfyui():
    """Test ComfyUI connection"""
    print("\n2. Testing ComfyUI...")
    print("-" * 40)
    
    try:
        comfyui = ComfyUIAPI()
        
        # Try to connect
        import aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{comfyui.base_url}/system_stats") as response:
                    if response.status == 200:
                        print("✓ ComfyUI is running")
                        print(f"  URL: {comfyui.base_url}")
                    else:
                        print(f"✗ ComfyUI returned status {response.status}")
            except aiohttp.ClientError:
                print("✗ ComfyUI is not running")
                print("  Start with: cd ComfyUI && python main.py")
    except Exception as e:
        print(f"✗ Error connecting to ComfyUI: {e}")


async def test_ffmpeg():
    """Test ffmpeg installation"""
    print("\n3. Testing FFmpeg...")
    print("-" * 40)
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg is installed")
            print(f"  {version_line}")
        else:
            print("✗ FFmpeg is not working properly")
    except FileNotFoundError:
        print("✗ FFmpeg is not installed")
        print("  Install with: apt-get install ffmpeg (Linux)")
        print("  Or: brew install ffmpeg (macOS)")
    except Exception as e:
        print(f"✗ Error checking FFmpeg: {e}")


async def test_python_packages():
    """Test Python package installations"""
    print("\n4. Testing Python Packages...")
    print("-" * 40)
    
    required_packages = [
        'requests',
        'aiohttp',
        'yaml',
        'PIL',
    ]
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
                print(f"✓ Pillow is installed")
            elif package == 'yaml':
                import yaml
                print(f"✓ PyYAML is installed")
            else:
                __import__(package)
                print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is not installed")
            print(f"  Install with: pip install {package}")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Video Generation Toolkit - Connection Tests")
    print("=" * 60)
    
    await test_ollama()
    await test_comfyui()
    await test_ffmpeg()
    await test_python_packages()
    
    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)
    print("\nNote: It's normal for some services to be offline.")
    print("Start them as needed for your workflow.")


if __name__ == '__main__':
    asyncio.run(main())
