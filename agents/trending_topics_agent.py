"""
Trending Topics Research Agent

This agent researches trending topics from various sources to identify
content opportunities for video generation.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict
import json
import logging
from functools import wraps
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry failed async operations"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {e}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
                    await asyncio.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator


class TrendingTopicsAgent:
    """Agent for researching trending topics across multiple platforms"""

    def __init__(self, config: Dict):
        self.config = config
        self.sources = config.get('research', {}).get('sources', [])
        self.topics_to_track = config.get('research', {}).get('topics_to_track', 10)
        self._request_count = 0
        self._last_request_time = 0
        self._rate_limit_delay = 1.0  # Minimum delay between requests

    async def _rate_limit(self):
        """Implement rate limiting for API calls"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time

        if time_since_last < self._rate_limit_delay:
            await asyncio.sleep(self._rate_limit_delay - time_since_last)

        self._last_request_time = time.time()
        self._request_count += 1

    def _validate_trend(self, trend: Dict) -> bool:
        """Validate trend data structure"""
        required_fields = ['source', 'timestamp']
        return all(field in trend for field in required_fields)

    @retry_on_failure(max_retries=3, delay=2.0)
    async def fetch_reddit_trends(self) -> List[Dict]:
        """Fetch trending topics from Reddit with retry logic"""
        await self._rate_limit()

        try:
            url = "https://www.reddit.com/r/all/hot.json?limit=25"
            headers = {'User-Agent': 'VideoGenerationToolkit/1.0'}

            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data.get('data', {}).get('children', [])

                        trends = []
                        for post in posts[:self.topics_to_track]:
                            post_data = post.get('data', {})
                            trend = {
                                'source': 'reddit',
                                'title': post_data.get('title', ''),
                                'subreddit': post_data.get('subreddit', ''),
                                'score': post_data.get('score', 0),
                                'url': post_data.get('url', ''),
                                'timestamp': datetime.now().isoformat(),
                                'num_comments': post_data.get('num_comments', 0),
                                'upvote_ratio': post_data.get('upvote_ratio', 0.0)
                            }

                            if self._validate_trend(trend):
                                trends.append(trend)

                        logger.info(f"Fetched {len(trends)} trends from Reddit")
                        return trends
                    else:
                        logger.error(f"Reddit API returned status {response.status}")
                        return []
        except asyncio.TimeoutError:
            logger.error("Reddit API request timed out")
            return []
        except Exception as e:
            logger.error(f"Error fetching Reddit trends: {e}")
            return []

    async def fetch_youtube_trends(self) -> List[Dict]:
        """Fetch trending topics from YouTube (using public data)"""
        try:
            # This is a simplified version - in production, use YouTube Data API
            trends = [
                {
                    'source': 'youtube',
                    'title': 'AI Generated Videos',
                    'category': 'Technology',
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'source': 'youtube',
                    'title': 'Latest Tech Reviews',
                    'category': 'Technology',
                    'timestamp': datetime.now().isoformat()
                }
            ]
            logger.info(f"Fetched {len(trends)} trends from YouTube")
            return trends
        except Exception as e:
            logger.error(f"Error fetching YouTube trends: {e}")
            return []

    async def fetch_google_trends(self) -> List[Dict]:
        """Fetch trending searches from Google Trends"""
        try:
            # This is a placeholder - in production, use pytrends library
            trends = [
                {
                    'source': 'google_trends',
                    'query': 'AI video generation',
                    'interest': 100,
                    'timestamp': datetime.now().isoformat()
                }
            ]
            logger.info(f"Fetched {len(trends)} trends from Google Trends")
            return trends
        except Exception as e:
            logger.error(f"Error fetching Google Trends: {e}")
            return []

    async def analyze_trends(self, all_trends: List[Dict]) -> List[Dict]:
        """Analyze and rank trends for video generation potential"""
        # Simple scoring based on engagement metrics
        scored_trends = []

        for trend in all_trends:
            score = 0

            # Score based on source
            if trend['source'] == 'reddit':
                score += trend.get('score', 0) / 1000
            elif trend['source'] == 'youtube':
                score += 5
            elif trend['source'] == 'google_trends':
                score += trend.get('interest', 0) / 10

            trend['video_potential_score'] = score
            scored_trends.append(trend)

        # Sort by score
        scored_trends.sort(key=lambda x: x['video_potential_score'], reverse=True)

        return scored_trends[:self.topics_to_track]

    async def research(self) -> List[Dict]:
        """Main research function to gather trending topics"""
        logger.info("Starting trending topics research...")

        all_trends = []
        tasks = []

        if 'reddit' in self.sources:
            tasks.append(self.fetch_reddit_trends())
        if 'youtube' in self.sources:
            tasks.append(self.fetch_youtube_trends())
        if 'google_trends' in self.sources:
            tasks.append(self.fetch_google_trends())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_trends.extend(result)

        # Analyze and rank trends
        top_trends = await self.analyze_trends(all_trends)

        logger.info(f"Research complete. Found {len(top_trends)} top trends.")
        return top_trends

    def save_trends(self, trends: List[Dict], filename: str = 'output/trends.json'):
        """Save trends to a file"""
        try:
            with open(filename, 'w') as f:
                json.dump(trends, f, indent=2)
            logger.info(f"Trends saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving trends: {e}")


async def main():
    """Example usage"""
    config = {
        'research': {
            'sources': ['reddit', 'youtube', 'google_trends'],
            'topics_to_track': 10
        }
    }

    agent = TrendingTopicsAgent(config)
    trends = await agent.research()

    print("\n=== Top Trending Topics ===")
    for i, trend in enumerate(trends, 1):
        print(f"{i}. [{trend['source']}] {trend.get('title', trend.get('query', 'N/A'))}")
        print(f"   Score: {trend['video_potential_score']:.2f}")

    agent.save_trends(trends)


if __name__ == '__main__':
    asyncio.run(main())
