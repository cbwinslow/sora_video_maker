"""
Deep Research Agent

This agent performs in-depth research on topics, gathering detailed information,
analyzing trends, and creating comprehensive reports for video content creation.
"""

import asyncio
import aiohttp
import json
import logging
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepResearchAgent:
    """Agent for performing deep research on topics"""

    def __init__(self, config: Dict):
        self.config = config
        self.ollama_host = config.get('ollama', {}).get('host', 'http://localhost:11434')
        self.research_depth = config.get('research', {}).get('depth', 'comprehensive')
        self.cache_enabled = config.get('cache_enabled', True)
        self.cache_dir = config.get('cache_dir', '.cache/research')
        self.cache_ttl = config.get('cache_ttl', 86400)  # 24 hours default

        # Create cache directory
        if self.cache_enabled:
            Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, topic: str) -> str:
        """Generate cache key for a topic"""
        return hashlib.md5(topic.lower().encode()).hexdigest()

    def _get_cached_research(self, topic: str) -> Optional[Dict]:
        """Get cached research if available and not expired"""
        if not self.cache_enabled:
            return None

        cache_key = self._get_cache_key(topic)
        cache_file = Path(self.cache_dir) / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            # Check if cache is still valid
            file_age = datetime.now().timestamp() - cache_file.stat().st_mtime
            if file_age > self.cache_ttl:
                logger.info(f"Cache expired for topic: {topic}")
                return None

            with open(cache_file, 'r') as f:
                cached_data = json.load(f)

            logger.info(f"Using cached research for: {topic}")
            return cached_data

        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None

    def _save_to_cache(self, topic: str, research: Dict):
        """Save research to cache"""
        if not self.cache_enabled:
            return

        try:
            cache_key = self._get_cache_key(topic)
            cache_file = Path(self.cache_dir) / f"{cache_key}.json"

            with open(cache_file, 'w') as f:
                json.dump(research, f, indent=2)

            logger.debug(f"Research cached for: {topic}")

        except Exception as e:
            logger.error(f"Error saving to cache: {e}")

    def validate_research_result(self, research: Dict) -> bool:
        """Validate that research result contains required fields"""
        required_fields = ['topic', 'summary', 'key_points', 'sources']

        for field in required_fields:
            if field not in research:
                logger.error(f"Missing required field: {field}")
                return False

            # Check non-empty values
            if field == 'summary' and not research[field]:
                logger.error("Summary is empty")
                return False

            if field in ['key_points', 'sources'] and not research[field]:
                logger.warning(f"{field} is empty")

        return True

    async def research_topic(self, topic: str) -> Dict:
        """Perform deep research on a specific topic"""

        # Input validation
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty")

        topic = topic.strip()
        logger.info(f"Starting deep research on: {topic}")

        # Check cache first
        cached = self._get_cached_research(topic)
        if cached:
            return cached

        research_result = {
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'summary': '',
            'key_points': [],
            'sources': [],
            'video_angles': [],
            'target_audience': '',
            'estimated_interest': 0,
            'related_topics': [],
            'research_quality_score': 0
        }

        try:
            # Step 1: Gather background information
            background = await self._gather_background(topic)
            research_result['summary'] = background

            # Step 2: Extract key points
            key_points = await self._extract_key_points(topic, background)
            research_result['key_points'] = key_points

            # Step 3: Find sources
            sources = await self._find_sources(topic)
            research_result['sources'] = sources

            # Step 4: Analyze video angles
            video_angles = await self._analyze_video_angles(topic, key_points)
            research_result['video_angles'] = video_angles

            # Step 5: Determine target audience
            audience = await self._determine_audience(topic)
            research_result['target_audience'] = audience

            # Step 6: Find related topics
            related = await self._find_related_topics(topic)
            research_result['related_topics'] = related

            # Step 7: Calculate research quality score
            research_result['research_quality_score'] = self._calculate_quality_score(research_result)

            # Validate results
            if not self.validate_research_result(research_result):
                logger.warning("Research validation failed, using fallback data")

            # Cache the results
            self._save_to_cache(topic, research_result)

            logger.info(f"Deep research complete for: {topic} (quality score: {research_result['research_quality_score']}/100)")
            return research_result

        except Exception as e:
            logger.error(f"Error during research: {e}", exc_info=True)
            research_result['error'] = str(e)
            return research_result

    def _calculate_quality_score(self, research: Dict) -> int:
        """Calculate quality score for research (0-100)"""
        score = 0

        # Summary quality (0-30 points)
        if research.get('summary'):
            word_count = len(research['summary'].split())
            if word_count >= 200:
                score += 30
            elif word_count >= 100:
                score += 20
            elif word_count >= 50:
                score += 10

        # Key points (0-25 points)
        key_points = research.get('key_points', [])
        if len(key_points) >= 5:
            score += 25
        elif len(key_points) >= 3:
            score += 15
        elif len(key_points) >= 1:
            score += 5

        # Sources (0-20 points)
        sources = research.get('sources', [])
        if len(sources) >= 3:
            score += 20
        elif len(sources) >= 2:
            score += 10
        elif len(sources) >= 1:
            score += 5

        # Video angles (0-15 points)
        if len(research.get('video_angles', [])) >= 3:
            score += 15
        elif len(research.get('video_angles', [])) >= 1:
            score += 10

        # Related topics (0-10 points)
        if len(research.get('related_topics', [])) >= 3:
            score += 10
        elif len(research.get('related_topics', [])) >= 1:
            score += 5

        return min(score, 100)

    async def _gather_background(self, topic: str) -> str:
        """Gather background information using LLM"""
        prompt = f"""Provide a comprehensive background summary on the topic: {topic}

Include:
- Historical context
- Current state
- Key developments
- Why it matters now

Keep it concise but informative (200-300 words)."""

        try:
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                payload = {
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                }

                async with session.post(f"{self.ollama_host}/api/generate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', '')
                    else:
                        logger.error(f"Ollama API returned status {response.status}")
        except asyncio.TimeoutError:
            logger.error("Ollama API timeout")
        except Exception as e:
            logger.error(f"Error gathering background: {e}")

        return f"Background research on {topic}"

    async def _extract_key_points(self, topic: str, background: str) -> List[str]:
        """Extract key points from research"""
        prompt = f"""Based on this topic: {topic}

And this background: {background}

Extract 5-7 key points that would be most interesting for a video. Format as a numbered list."""

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                }

                async with session.post(f"{self.ollama_host}/api/generate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get('response', '')
                        # Parse numbered list
                        points = [line.strip() for line in response_text.split('\n')
                                 if line.strip() and any(c.isdigit() for c in line[:3])]
                        return points[:7]
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")

        return [
            "Introduction to the topic",
            "Key developments and trends",
            "Impact and significance",
            "Future implications",
            "Conclusion and takeaways"
        ]

    async def _find_sources(self, topic: str) -> List[Dict]:
        """Find credible sources for the topic"""
        # In production, this would search various sources
        sources = [
            {
                'type': 'article',
                'title': f'Comprehensive guide to {topic}',
                'url': f'https://example.com/{topic.replace(" ", "-")}',
                'credibility': 'high'
            },
            {
                'type': 'video',
                'title': f'{topic} explained',
                'url': f'https://youtube.com/watch?v=example',
                'credibility': 'medium'
            }
        ]

        return sources

    async def _analyze_video_angles(self, topic: str, key_points: List[str]) -> List[Dict]:
        """Analyze different video angles for the topic"""
        angles = []

        # Educational angle
        angles.append({
            'angle': 'educational',
            'title': f'Everything You Need to Know About {topic}',
            'hook': f'Want to understand {topic}? Here\'s what you need to know.',
            'target_length': '5-10 minutes',
            'format': 'explainer'
        })

        # Trending angle
        angles.append({
            'angle': 'trending',
            'title': f'Why Everyone is Talking About {topic}',
            'hook': f'{topic} is taking over the internet. Here\'s why.',
            'target_length': '3-5 minutes',
            'format': 'news/commentary'
        })

        # How-to angle
        angles.append({
            'angle': 'tutorial',
            'title': f'How to Use {topic} (Complete Guide)',
            'hook': f'Master {topic} with this step-by-step guide.',
            'target_length': '8-15 minutes',
            'format': 'tutorial'
        })

        return angles

    async def _determine_audience(self, topic: str) -> str:
        """Determine target audience for the topic"""
        prompt = f"Who is the target audience for content about: {topic}? Describe in 1-2 sentences."

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                }

                async with session.post(f"{self.ollama_host}/api/generate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', '').strip()
        except Exception as e:
            logger.error(f"Error determining audience: {e}")

        return "General audience interested in technology and innovation"

    async def _find_related_topics(self, topic: str) -> List[str]:
        """Find related topics for content series"""
        prompt = f"List 5 topics closely related to: {topic}. One per line, no numbers."

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                }

                async with session.post(f"{self.ollama_host}/api/generate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get('response', '')
                        topics = [line.strip() for line in response_text.split('\n')
                                 if line.strip() and len(line.strip()) > 5]
                        return topics[:5]
        except Exception as e:
            logger.error(f"Error finding related topics: {e}")

        return []

    def save_research(self, research: Dict, filename: str = None):
        """Save research results to file"""
        if filename is None:
            topic_slug = research['topic'].replace(' ', '_').lower()
            filename = f"output/research/{topic_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        try:
            with open(filename, 'w') as f:
                json.dump(research, f, indent=2)
            logger.info(f"Research saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving research: {e}")


async def main():
    """Example usage"""
    config = {
        'ollama': {
            'host': 'http://localhost:11434'
        },
        'research': {
            'depth': 'comprehensive'
        }
    }

    agent = DeepResearchAgent(config)

    # Example topic
    topic = "AI Video Generation Technology"

    research = await agent.research_topic(topic)

    print("\n=== Deep Research Results ===")
    print(f"Topic: {research['topic']}")
    print(f"\nSummary:\n{research['summary'][:200]}...")
    print(f"\nKey Points:")
    for point in research['key_points']:
        print(f"  - {point}")
    print(f"\nVideo Angles:")
    for angle in research['video_angles']:
        print(f"  - {angle['angle']}: {angle['title']}")

    agent.save_research(research)


if __name__ == '__main__':
    asyncio.run(main())
