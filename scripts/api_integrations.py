"""
API Integration Scripts for Various Video Generation Platforms
"""

import os
import requests
import aiohttp
import logging
from typing import Dict, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenRouterAPI:
    """OpenRouter API client for free models"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_text(self, prompt: str, model: str = "meta-llama/llama-2-70b-chat") -> str:
        """Generate text using OpenRouter models"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        logger.error(f"OpenRouter API error: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return ""


class SoraAPI:
    """Sora API client (placeholder - API not publicly available yet)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
    
    async def generate_video(self, prompt: str, duration: int = 10) -> Optional[str]:
        """Generate video using Sora (when API is available)"""
        logger.warning("Sora API is not publicly available yet. This is a placeholder.")
        
        # When Sora API is released, implementation would be:
        # 1. Make API call to OpenAI
        # 2. Wait for video generation
        # 3. Download generated video
        # 4. Return local path
        
        return None


class OllamaAPI:
    """Ollama API client for local LLM inference"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
    
    async def generate_text(self, prompt: str, model: str = "llama2") -> str:
        """Generate text using Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
                
                async with session.post(
                    f"{self.host}/api/generate",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', '')
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return ""
    
    async def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.host}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model['name'] for model in data.get('models', [])]
                    else:
                        return []
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []


class ComfyUIAPI:
    """ComfyUI API client"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8188):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
    
    async def queue_prompt(self, workflow: Dict) -> Optional[str]:
        """Queue a prompt in ComfyUI"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/prompt",
                    json={"prompt": workflow}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('prompt_id')
                    else:
                        logger.error(f"ComfyUI API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error calling ComfyUI API: {e}")
            return None
    
    async def get_history(self, prompt_id: str) -> Optional[Dict]:
        """Get execution history for a prompt"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/history/{prompt_id}"
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
        except Exception as e:
            logger.error(f"Error getting ComfyUI history: {e}")
            return None


async def test_apis():
    """Test API connections"""
    print("\n=== Testing API Connections ===\n")
    
    # Test Ollama
    print("Testing Ollama...")
    ollama = OllamaAPI()
    models = await ollama.list_models()
    print(f"Available Ollama models: {models}")
    
    if models:
        response = await ollama.generate_text("Hello, how are you?", models[0])
        print(f"Ollama response: {response[:100]}...")
    
    print("\nAPI tests complete!")


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_apis())
