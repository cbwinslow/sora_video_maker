"""
SEO Optimization Tool

This tool helps optimize video metadata for search engines and platforms.
"""

import re
import logging
from typing import List, Dict, Optional
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOOptimizer:
    """Optimize video metadata for search engines"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.max_title_length = 100
        self.max_description_length = 5000
        self.max_tags = 30
        
    def optimize_title(self, title: str, keywords: Optional[List[str]] = None) -> str:
        """
        Optimize video title for SEO
        
        Args:
            title: Original title
            keywords: Optional list of keywords to include
            
        Returns:
            Optimized title
        """
        if not title:
            return "Untitled Video"
        
        # Clean title
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Add keywords if provided and space allows
        if keywords:
            for keyword in keywords[:2]:  # Add up to 2 keywords
                if keyword.lower() not in title.lower():
                    potential_title = f"{title} - {keyword}"
                    if len(potential_title) <= self.max_title_length:
                        title = potential_title
                        break
        
        # Truncate if too long
        if len(title) > self.max_title_length:
            title = title[:self.max_title_length - 3] + "..."
        
        logger.info(f"Optimized title: {title}")
        return title
    
    def optimize_description(self, description: str, keywords: Optional[List[str]] = None, 
                           links: Optional[List[str]] = None) -> str:
        """
        Optimize video description for SEO
        
        Args:
            description: Original description
            keywords: Optional keywords to incorporate
            links: Optional links to add
            
        Returns:
            Optimized description
        """
        if not description:
            description = "Check out this amazing video!"
        
        # Clean description
        description = re.sub(r'\s+', ' ', description).strip()
        
        # Add keyword section
        if keywords:
            keyword_section = "\n\n🔍 Topics covered:\n" + ", ".join(keywords)
            description += keyword_section
        
        # Add links section
        if links:
            links_section = "\n\n🔗 Links:\n" + "\n".join(links)
            description += links_section
        
        # Add call to action
        cta = "\n\n👍 Like, Subscribe, and Share!"
        description += cta
        
        # Truncate if too long
        if len(description) > self.max_description_length:
            description = description[:self.max_description_length - 3] + "..."
        
        logger.info(f"Optimized description ({len(description)} chars)")
        return description
    
    def generate_tags(self, title: str, description: str, 
                     custom_tags: Optional[List[str]] = None) -> List[str]:
        """
        Generate SEO-optimized tags
        
        Args:
            title: Video title
            description: Video description
            custom_tags: Optional custom tags
            
        Returns:
            List of optimized tags
        """
        tags = []
        
        # Add custom tags first
        if custom_tags:
            tags.extend(custom_tags[:10])
        
        # Extract keywords from title and description
        text = f"{title} {description}".lower()
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                     'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        # Extract words
        words = re.findall(r'\b\w+\b', text)
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count frequency
        word_freq = Counter(filtered_words)
        
        # Add most common words as tags
        for word, _ in word_freq.most_common(20):
            if word not in tags:
                tags.append(word)
        
        # Add generic relevant tags
        generic_tags = ['video', 'tutorial', 'howto', 'guide', 'tips']
        for tag in generic_tags:
            if tag not in tags and len(tags) < self.max_tags:
                tags.append(tag)
        
        # Limit to max tags
        tags = tags[:self.max_tags]
        
        logger.info(f"Generated {len(tags)} tags")
        return tags
    
    def generate_thumbnail_text(self, title: str, max_words: int = 5) -> str:
        """
        Generate short text for video thumbnail
        
        Args:
            title: Video title
            max_words: Maximum words in thumbnail text
            
        Returns:
            Short text for thumbnail
        """
        # Extract most important words
        words = title.split()
        
        # Remove articles and prepositions
        important_words = []
        skip_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        
        for word in words:
            if word.lower() not in skip_words:
                important_words.append(word)
        
        # Take first N important words
        thumbnail_text = ' '.join(important_words[:max_words]).upper()
        
        logger.info(f"Generated thumbnail text: {thumbnail_text}")
        return thumbnail_text
    
    def suggest_posting_time(self, target_audience: str = 'global') -> Dict[str, any]:
        """
        Suggest optimal posting time based on target audience
        
        Args:
            target_audience: Target audience region
            
        Returns:
            Dictionary with posting recommendations
        """
        posting_times = {
            'global': {
                'weekdays': ['Tuesday', 'Wednesday', 'Thursday'],
                'times': ['14:00-16:00 UTC', '18:00-20:00 UTC'],
                'avoid': ['Late Friday', 'Early Monday']
            },
            'us': {
                'weekdays': ['Wednesday', 'Thursday', 'Friday'],
                'times': ['09:00-11:00 EST', '17:00-19:00 EST'],
                'avoid': ['Weekend mornings']
            },
            'europe': {
                'weekdays': ['Tuesday', 'Wednesday', 'Thursday'],
                'times': ['10:00-12:00 CET', '18:00-20:00 CET'],
                'avoid': ['Sunday']
            }
        }
        
        return posting_times.get(target_audience.lower(), posting_times['global'])
    
    def analyze_title_quality(self, title: str) -> Dict[str, any]:
        """
        Analyze title quality and provide feedback
        
        Args:
            title: Video title to analyze
            
        Returns:
            Dictionary with quality metrics and suggestions
        """
        analysis = {
            'length': len(title),
            'word_count': len(title.split()),
            'has_numbers': bool(re.search(r'\d', title)),
            'has_special_chars': bool(re.search(r'[!?]', title)),
            'is_capitalized': title[0].isupper() if title else False,
            'score': 0,
            'suggestions': []
        }
        
        # Scoring
        if 40 <= analysis['length'] <= 70:
            analysis['score'] += 20
        else:
            analysis['suggestions'].append('Title should be 40-70 characters')
        
        if analysis['has_numbers']:
            analysis['score'] += 10
            
        if analysis['has_special_chars']:
            analysis['score'] += 5
            
        if analysis['is_capitalized']:
            analysis['score'] += 5
            
        if analysis['word_count'] >= 4:
            analysis['score'] += 10
        else:
            analysis['suggestions'].append('Add more descriptive words')
        
        # Check for power words
        power_words = ['amazing', 'ultimate', 'best', 'top', 'how', 'why', 'secret', 'proven']
        if any(word in title.lower() for word in power_words):
            analysis['score'] += 15
        else:
            analysis['suggestions'].append('Consider adding power words')
        
        analysis['quality'] = 'Excellent' if analysis['score'] >= 50 else \
                             'Good' if analysis['score'] >= 35 else \
                             'Needs Improvement'
        
        return analysis


def main():
    """Example usage"""
    optimizer = SEOOptimizer()
    
    # Example title optimization
    title = "AI Video Generation Tutorial"
    keywords = ["OpenAI", "Automation", "Content Creation"]
    
    optimized_title = optimizer.optimize_title(title, keywords)
    print(f"Optimized Title: {optimized_title}")
    
    # Example description optimization
    description = "Learn how to generate videos using AI."
    links = ["https://example.com/tutorial", "https://example.com/tools"]
    
    optimized_desc = optimizer.optimize_description(description, keywords, links)
    print(f"\nOptimized Description:\n{optimized_desc}")
    
    # Generate tags
    tags = optimizer.generate_tags(optimized_title, optimized_desc)
    print(f"\nGenerated Tags: {', '.join(tags[:10])}")
    
    # Thumbnail text
    thumb_text = optimizer.generate_thumbnail_text(optimized_title)
    print(f"\nThumbnail Text: {thumb_text}")
    
    # Analyze title quality
    analysis = optimizer.analyze_title_quality(optimized_title)
    print(f"\nTitle Quality: {analysis['quality']} (Score: {analysis['score']}/60)")
    if analysis['suggestions']:
        print(f"Suggestions: {', '.join(analysis['suggestions'])}")


if __name__ == '__main__':
    main()
