"""
Unit tests for SEO Optimizer
"""

import pytest
from scripts.seo_optimizer import SEOOptimizer


@pytest.mark.unit
@pytest.mark.script
class TestSEOOptimizer:
    """Test suite for SEO Optimizer"""
    
    def test_init(self):
        """Test initialization"""
        optimizer = SEOOptimizer()
        
        assert optimizer.max_title_length == 100
        assert optimizer.max_description_length == 5000
        assert optimizer.max_tags == 30
    
    def test_optimize_title_basic(self):
        """Test basic title optimization"""
        optimizer = SEOOptimizer()
        
        title = "AI Video Generation"
        optimized = optimizer.optimize_title(title)
        
        assert len(optimized) <= optimizer.max_title_length
        assert "AI Video Generation" in optimized
    
    def test_optimize_title_with_keywords(self):
        """Test title optimization with keywords"""
        optimizer = SEOOptimizer()
        
        title = "Tutorial"
        keywords = ["AI", "OpenAI"]
        optimized = optimizer.optimize_title(title, keywords)
        
        assert "Tutorial" in optimized
        assert any(kw in optimized for kw in keywords)
    
    def test_optimize_title_truncation(self):
        """Test that long titles are truncated"""
        optimizer = SEOOptimizer()
        
        long_title = "A" * 150
        optimized = optimizer.optimize_title(long_title)
        
        assert len(optimized) <= optimizer.max_title_length
        assert optimized.endswith("...")
    
    def test_optimize_title_empty(self):
        """Test with empty title"""
        optimizer = SEOOptimizer()
        
        optimized = optimizer.optimize_title("")
        
        assert optimized == "Untitled Video"
    
    def test_optimize_description_basic(self):
        """Test basic description optimization"""
        optimizer = SEOOptimizer()
        
        desc = "Learn about AI video generation"
        optimized = optimizer.optimize_description(desc)
        
        assert "Learn about AI video generation" in optimized
        assert len(optimized) <= optimizer.max_description_length
    
    def test_optimize_description_with_keywords(self):
        """Test description with keywords"""
        optimizer = SEOOptimizer()
        
        desc = "Learn about video creation"
        keywords = ["AI", "Automation", "Tutorial"]
        optimized = optimizer.optimize_description(desc, keywords)
        
        assert "Learn about video creation" in optimized
        assert "Topics covered" in optimized
        assert all(kw in optimized for kw in keywords)
    
    def test_optimize_description_with_links(self):
        """Test description with links"""
        optimizer = SEOOptimizer()
        
        desc = "Check out this tutorial"
        links = ["https://example.com", "https://test.com"]
        optimized = optimizer.optimize_description(desc, links=links)
        
        assert "Check out this tutorial" in optimized
        assert "Links" in optimized
        assert all(link in optimized for link in links)
    
    def test_optimize_description_has_cta(self):
        """Test that description includes call to action"""
        optimizer = SEOOptimizer()
        
        desc = "Test description"
        optimized = optimizer.optimize_description(desc)
        
        assert "Like" in optimized or "Subscribe" in optimized
    
    def test_generate_tags_basic(self):
        """Test basic tag generation"""
        optimizer = SEOOptimizer()
        
        title = "AI Video Generation Tutorial"
        desc = "Learn how to generate videos using AI technology"
        
        tags = optimizer.generate_tags(title, desc)
        
        assert isinstance(tags, list)
        assert len(tags) <= optimizer.max_tags
        assert len(tags) > 0
    
    def test_generate_tags_with_custom(self):
        """Test tag generation with custom tags"""
        optimizer = SEOOptimizer()
        
        title = "Tutorial"
        desc = "Description"
        custom_tags = ["custom1", "custom2", "custom3"]
        
        tags = optimizer.generate_tags(title, desc, custom_tags)
        
        # Custom tags should be included
        assert all(tag in tags for tag in custom_tags)
    
    def test_generate_tags_filters_stopwords(self):
        """Test that common words are filtered"""
        optimizer = SEOOptimizer()
        
        title = "The Best Tutorial"
        desc = "This is a great tutorial"
        
        tags = optimizer.generate_tags(title, desc)
        
        # Common words should not be tags
        assert "the" not in [t.lower() for t in tags]
        assert "is" not in [t.lower() for t in tags]
        assert "a" not in [t.lower() for t in tags]
    
    def test_generate_thumbnail_text(self):
        """Test thumbnail text generation"""
        optimizer = SEOOptimizer()
        
        title = "How to Create Amazing Videos with AI"
        thumb_text = optimizer.generate_thumbnail_text(title)
        
        assert isinstance(thumb_text, str)
        assert len(thumb_text) > 0
        assert thumb_text.isupper()
    
    def test_generate_thumbnail_text_max_words(self):
        """Test thumbnail text with word limit"""
        optimizer = SEOOptimizer()
        
        title = "One Two Three Four Five Six Seven Eight"
        thumb_text = optimizer.generate_thumbnail_text(title, max_words=3)
        
        words = thumb_text.split()
        assert len(words) <= 3
    
    def test_suggest_posting_time_global(self):
        """Test posting time suggestions for global audience"""
        optimizer = SEOOptimizer()
        
        suggestions = optimizer.suggest_posting_time('global')
        
        assert 'weekdays' in suggestions
        assert 'times' in suggestions
        assert 'avoid' in suggestions
        assert isinstance(suggestions['weekdays'], list)
    
    def test_suggest_posting_time_us(self):
        """Test posting time for US audience"""
        optimizer = SEOOptimizer()
        
        suggestions = optimizer.suggest_posting_time('us')
        
        assert 'weekdays' in suggestions
        assert len(suggestions['weekdays']) > 0
    
    def test_suggest_posting_time_invalid(self):
        """Test with invalid audience (should default to global)"""
        optimizer = SEOOptimizer()
        
        suggestions = optimizer.suggest_posting_time('invalid_region')
        
        # Should return global suggestions
        assert 'weekdays' in suggestions
    
    def test_analyze_title_quality(self):
        """Test title quality analysis"""
        optimizer = SEOOptimizer()
        
        title = "10 Amazing AI Video Tips!"
        analysis = optimizer.analyze_title_quality(title)
        
        assert 'length' in analysis
        assert 'word_count' in analysis
        assert 'score' in analysis
        assert 'quality' in analysis
        assert 'suggestions' in analysis
    
    def test_analyze_title_quality_good_title(self):
        """Test analysis of a good title"""
        optimizer = SEOOptimizer()
        
        # Good title with numbers, proper length, power word
        title = "The Ultimate Guide to AI Video Creation in 2024"
        analysis = optimizer.analyze_title_quality(title)
        
        assert analysis['score'] > 35
        assert analysis['has_numbers']
        assert analysis['is_capitalized']
    
    def test_analyze_title_quality_short_title(self):
        """Test analysis of a short title"""
        optimizer = SEOOptimizer()
        
        title = "AI"
        analysis = optimizer.analyze_title_quality(title)
        
        assert analysis['score'] < 50
        assert len(analysis['suggestions']) > 0
    
    def test_analyze_title_quality_provides_suggestions(self):
        """Test that suggestions are provided"""
        optimizer = SEOOptimizer()
        
        title = "test"
        analysis = optimizer.analyze_title_quality(title)
        
        assert isinstance(analysis['suggestions'], list)


@pytest.mark.unit
@pytest.mark.script
class TestSEOOptimizerEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_optimize_title_whitespace(self):
        """Test title with excessive whitespace"""
        optimizer = SEOOptimizer()
        
        title = "Test    Title   With   Spaces"
        optimized = optimizer.optimize_title(title)
        
        # Should normalize whitespace
        assert "  " not in optimized
    
    def test_generate_tags_empty_text(self):
        """Test tag generation with empty text"""
        optimizer = SEOOptimizer()
        
        tags = optimizer.generate_tags("", "")
        
        assert isinstance(tags, list)
        # Should still generate some generic tags
        assert len(tags) > 0
    
    def test_optimize_description_very_long(self):
        """Test description that exceeds max length"""
        optimizer = SEOOptimizer()
        
        long_desc = "A" * 6000
        optimized = optimizer.optimize_description(long_desc)
        
        assert len(optimized) <= optimizer.max_description_length
    
    def test_generate_thumbnail_text_empty_title(self):
        """Test thumbnail generation with empty title"""
        optimizer = SEOOptimizer()
        
        thumb_text = optimizer.generate_thumbnail_text("")
        
        # Should handle gracefully
        assert isinstance(thumb_text, str)
