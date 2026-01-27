"""
Unit tests for Content Moderator
"""

import pytest
from scripts.content_moderator import ContentModerator


@pytest.mark.unit
@pytest.mark.script
class TestContentModerator:
    """Test suite for Content Moderator"""
    
    def test_init(self):
        """Test initialization"""
        moderator = ContentModerator()
        
        assert moderator.profanity_list is not None
        assert moderator.banned_topics is not None
        assert len(moderator.profanity_list) > 0
        assert len(moderator.banned_topics) > 0
    
    def test_check_profanity_clean(self):
        """Test profanity check with clean text"""
        moderator = ContentModerator()
        
        text = "This is a clean and appropriate text"
        result = moderator.check_profanity(text)
        
        assert result['has_profanity'] is False
        assert result['count'] == 0
        assert result['severity'] == 'low'
    
    def test_check_profanity_found(self):
        """Test profanity detection"""
        moderator = ContentModerator()
        
        text = "This damn text has profanity"
        result = moderator.check_profanity(text)
        
        assert result['has_profanity'] is True
        assert result['count'] > 0
        assert len(result['found_words']) > 0
    
    def test_check_profanity_severity_high(self):
        """Test high severity profanity"""
        moderator = ContentModerator()
        
        # Text with multiple profanity instances
        text = "damn hell crap shit"
        result = moderator.check_profanity(text)
        
        assert result['severity'] == 'high'
        assert result['count'] >= 3
    
    def test_check_banned_topics_clean(self):
        """Test banned topics with clean content"""
        moderator = ContentModerator()
        
        text = "Learn about video editing"
        result = moderator.check_banned_topics(text)
        
        assert result['has_banned_topics'] is False
        assert result['severity'] == 'low'
    
    def test_check_banned_topics_found(self):
        """Test banned topic detection"""
        moderator = ContentModerator()
        
        text = "Content about illegal drugs"
        result = moderator.check_banned_topics(text)
        
        assert result['has_banned_topics'] is True
        assert result['severity'] == 'critical'
        assert len(result['found_topics']) > 0
    
    def test_check_suspicious_patterns_clean(self):
        """Test suspicious patterns with clean text"""
        moderator = ContentModerator()
        
        text = "Normal tutorial content"
        result = moderator.check_suspicious_patterns(text)
        
        assert result['has_suspicious_patterns'] is False
        assert result['severity'] == 'low'
    
    def test_check_personal_info_email(self):
        """Test PII detection for email"""
        moderator = ContentModerator()
        
        text = "Contact me at test@example.com"
        result = moderator.check_personal_info(text)
        
        assert result['has_personal_info'] is True
        assert 'email' in result['found_types']
        assert result['severity'] == 'critical'
    
    def test_check_personal_info_phone(self):
        """Test PII detection for phone number"""
        moderator = ContentModerator()
        
        text = "Call me at 123-456-7890"
        result = moderator.check_personal_info(text)
        
        assert result['has_personal_info'] is True
        assert 'phone' in result['found_types']
    
    def test_check_personal_info_clean(self):
        """Test PII check with clean text"""
        moderator = ContentModerator()
        
        text = "No personal information here"
        result = moderator.check_personal_info(text)
        
        assert result['has_personal_info'] is False
        assert result['severity'] == 'low'
    
    def test_check_spam_indicators_clean(self):
        """Test spam check with clean text"""
        moderator = ContentModerator()
        
        text = "Educational content about technology"
        result = moderator.check_spam_indicators(text)
        
        assert result['is_likely_spam'] is False
        assert result['spam_score'] < 3
    
    def test_check_spam_indicators_found(self):
        """Test spam detection"""
        moderator = ContentModerator()
        
        text = "CLICK HERE NOW! BUY NOW! LIMITED TIME! ACT NOW!"
        result = moderator.check_spam_indicators(text)
        
        assert result['is_likely_spam'] is True
        assert result['spam_score'] >= 3
    
    def test_moderate_content_approved(self):
        """Test moderation of clean content"""
        moderator = ContentModerator()
        
        text = "High quality educational content"
        result = moderator.moderate_content(text)
        
        assert result['is_approved'] is True
        assert result['moderation_score'] > 70
        assert len(result['issues']) == 0
    
    def test_moderate_content_rejected_banned(self):
        """Test rejection due to banned topics"""
        moderator = ContentModerator()
        
        text = "Content about illegal drugs"
        result = moderator.moderate_content(text)
        
        assert result['is_approved'] is False
        assert len(result['issues']) > 0
    
    def test_moderate_content_rejected_pii(self):
        """Test rejection due to PII"""
        moderator = ContentModerator()
        
        text = "My email is test@example.com"
        result = moderator.moderate_content(text)
        
        assert result['is_approved'] is False
        assert any('personal information' in issue.lower() for issue in result['issues'])
    
    def test_moderate_content_rejected_spam(self):
        """Test rejection due to spam"""
        moderator = ContentModerator()
        
        text = "BUY NOW! CLICK HERE! LIMITED TIME! ACT NOW! FREE MONEY!"
        result = moderator.moderate_content(text)
        
        assert result['is_approved'] is False
        assert any('spam' in issue.lower() for issue in result['issues'])
    
    def test_moderate_content_warning_profanity(self):
        """Test warning for minor profanity"""
        moderator = ContentModerator({'strict_mode': False})
        
        text = "This damn tutorial is great"
        result = moderator.moderate_content(text)
        
        # Should pass with warning in non-strict mode
        assert len(result['warnings']) > 0
    
    def test_moderate_content_strict_mode(self):
        """Test strict mode rejection"""
        moderator = ContentModerator({'strict_mode': True})
        
        text = "This damn tutorial"
        result = moderator.moderate_content(text)
        
        # Should be rejected in strict mode
        assert result['is_approved'] is False
    
    def test_sanitize_text_profanity(self):
        """Test text sanitization for profanity"""
        moderator = ContentModerator()
        
        text = "This damn text needs cleaning"
        sanitized = moderator.sanitize_text(text)
        
        assert "damn" not in sanitized.lower()
        assert "***" in sanitized
    
    def test_sanitize_text_email(self):
        """Test sanitization of email"""
        moderator = ContentModerator()
        
        text = "Contact me at test@example.com"
        sanitized = moderator.sanitize_text(text)
        
        assert "test@example.com" not in sanitized
        assert "[EMAIL]" in sanitized
    
    def test_sanitize_text_phone(self):
        """Test sanitization of phone number"""
        moderator = ContentModerator()
        
        text = "Call 123-456-7890"
        sanitized = moderator.sanitize_text(text)
        
        assert "123-456-7890" not in sanitized
        assert "[PHONE]" in sanitized
    
    def test_generate_moderation_report(self):
        """Test report generation"""
        moderator = ContentModerator()
        
        text = "Clean content"
        result = moderator.moderate_content(text)
        report = moderator.generate_moderation_report(result)
        
        assert isinstance(report, str)
        assert "MODERATION REPORT" in report
        assert "APPROVED" in report or "REJECTED" in report
    
    def test_moderation_score_calculation(self):
        """Test that moderation score is calculated correctly"""
        moderator = ContentModerator()
        
        clean_text = "Clean educational content"
        result_clean = moderator.moderate_content(clean_text)
        
        dirty_text = "This damn tutorial about illegal drugs contact test@example.com"
        result_dirty = moderator.moderate_content(dirty_text)
        
        # Clean content should have higher score
        assert result_clean['moderation_score'] > result_dirty['moderation_score']


@pytest.mark.unit
@pytest.mark.script
class TestContentModeratorEdgeCases:
    """Test edge cases"""
    
    def test_empty_text(self):
        """Test with empty text"""
        moderator = ContentModerator()
        
        result = moderator.moderate_content("")
        
        assert result['is_approved'] is True
    
    def test_very_long_text(self):
        """Test with very long text"""
        moderator = ContentModerator()
        
        long_text = "Clean content " * 1000
        result = moderator.moderate_content(long_text)
        
        # Should handle without errors
        assert 'moderation_score' in result
    
    def test_unicode_text(self):
        """Test with unicode characters"""
        moderator = ContentModerator()
        
        text = "Content with émojis 😀 and spëcial çharacters"
        result = moderator.moderate_content(text)
        
        # Should handle without errors
        assert 'moderation_score' in result
    
    def test_sanitize_text_no_issues(self):
        """Test sanitization of clean text"""
        moderator = ContentModerator()
        
        text = "Clean text"
        sanitized = moderator.sanitize_text(text)
        
        # Should remain unchanged
        assert sanitized == text
