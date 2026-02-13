"""
Content Moderation Tool

This tool helps moderate and filter content before video generation.
"""

import re
import logging
from typing import List, Dict, Optional, Set
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentModerator:
    """Moderate content for inappropriate or problematic material"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

        # Load filter lists
        self.profanity_list = self._load_profanity_list()
        self.banned_topics = self._load_banned_topics()
        self.suspicious_patterns = self._load_suspicious_patterns()

        # Moderation settings
        self.strict_mode = self.config.get('strict_mode', False)
        self.allow_controversial = self.config.get('allow_controversial', False)

    def _load_profanity_list(self) -> Set[str]:
        """Load profanity word list"""
        # Basic profanity list (simplified for example)
        return {
            'damn', 'hell', 'crap', 'shit', 'fuck', 'bitch', 'ass', 'bastard',
            'piss', 'dick', 'cock', 'pussy', 'whore', 'slut'
        }

    def _load_banned_topics(self) -> Set[str]:
        """Load list of banned topics"""
        return {
            'illegal drugs', 'weapons', 'violence', 'hate speech',
            'terrorism', 'self-harm', 'child abuse', 'animal abuse',
            'piracy', 'hacking', 'doxxing', 'harassment'
        }

    def _load_suspicious_patterns(self) -> List[str]:
        """Load suspicious regex patterns"""
        return [
            r'\b(buy|sell|purchase)\s+(drugs?|weapons?|fake)\b',
            r'\b(hack|crack|pirate)\s+(account|software|game)\b',
            r'\b(how\s+to)\s+(make|build)\s+(bomb|explosive|weapon)\b',
            r'\b(ssn|social\s+security)\s+number\b',
            r'\b(credit\s+card|bank\s+account)\s+(number|info)\b',
        ]

    def check_profanity(self, text: str) -> Dict:
        """
        Check for profanity in text

        Args:
            text: Text to check

        Returns:
            Dictionary with profanity check results
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        found_profanity = []
        for word in words:
            if word in self.profanity_list:
                found_profanity.append(word)

        has_profanity = len(found_profanity) > 0

        return {
            'has_profanity': has_profanity,
            'found_words': found_profanity,
            'count': len(found_profanity),
            'severity': 'high' if len(found_profanity) > 3 else 'medium' if found_profanity else 'low'
        }

    def check_banned_topics(self, text: str) -> Dict:
        """
        Check for banned topics

        Args:
            text: Text to check

        Returns:
            Dictionary with banned topic check results
        """
        text_lower = text.lower()

        found_topics = []
        for topic in self.banned_topics:
            if topic in text_lower:
                found_topics.append(topic)

        has_banned = len(found_topics) > 0

        return {
            'has_banned_topics': has_banned,
            'found_topics': found_topics,
            'severity': 'critical' if has_banned else 'low'
        }

    def check_suspicious_patterns(self, text: str) -> Dict:
        """
        Check for suspicious patterns

        Args:
            text: Text to check

        Returns:
            Dictionary with pattern check results
        """
        text_lower = text.lower()

        matches = []
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_lower):
                matches.append(pattern)

        has_suspicious = len(matches) > 0

        return {
            'has_suspicious_patterns': has_suspicious,
            'matched_patterns': len(matches),
            'severity': 'high' if has_suspicious else 'low'
        }

    def check_personal_info(self, text: str) -> Dict:
        """
        Check for personal information

        Args:
            text: Text to check

        Returns:
            Dictionary with PII check results
        """
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }

        found_pii = {}
        for pii_type, pattern in pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                found_pii[pii_type] = len(matches)

        has_pii = len(found_pii) > 0

        return {
            'has_personal_info': has_pii,
            'found_types': found_pii,
            'severity': 'critical' if has_pii else 'low'
        }

    def check_spam_indicators(self, text: str) -> Dict:
        """
        Check for spam indicators

        Args:
            text: Text to check

        Returns:
            Dictionary with spam check results
        """
        spam_keywords = [
            'click here', 'buy now', 'limited time', 'act now', 'free money',
            'make money fast', 'work from home', 'get rich', 'no risk',
            'double your', '100% free', 'as seen on', 'winner', 'congratulations'
        ]

        text_lower = text.lower()

        spam_score = 0
        found_keywords = []

        for keyword in spam_keywords:
            if keyword in text_lower:
                spam_score += 1
                found_keywords.append(keyword)

        # Check for excessive caps
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.5:
            spam_score += 2

        # Check for excessive punctuation
        punct_count = sum(1 for c in text if c in '!?')
        if punct_count > 5:
            spam_score += 1

        is_spam = spam_score >= 3

        return {
            'is_likely_spam': is_spam,
            'spam_score': spam_score,
            'found_keywords': found_keywords,
            'caps_ratio': caps_ratio,
            'severity': 'high' if is_spam else 'medium' if spam_score > 0 else 'low'
        }

    def moderate_content(self, text: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Perform comprehensive content moderation

        Args:
            text: Text to moderate
            metadata: Optional metadata about the content

        Returns:
            Dictionary with moderation results
        """
        results = {
            'text': text,
            'timestamp': datetime.now().isoformat(),
            'is_approved': True,
            'moderation_score': 100,
            'issues': [],
            'warnings': [],
            'checks': {}
        }

        if metadata:
            results['metadata'] = metadata

        # Run all checks
        profanity_check = self.check_profanity(text)
        results['checks']['profanity'] = profanity_check

        banned_check = self.check_banned_topics(text)
        results['checks']['banned_topics'] = banned_check

        suspicious_check = self.check_suspicious_patterns(text)
        results['checks']['suspicious_patterns'] = suspicious_check

        pii_check = self.check_personal_info(text)
        results['checks']['personal_info'] = pii_check

        spam_check = self.check_spam_indicators(text)
        results['checks']['spam'] = spam_check

        # Calculate moderation score
        score_penalties = {
            'profanity': 10 * profanity_check['count'],
            'banned_topics': 50 if banned_check['has_banned_topics'] else 0,
            'suspicious': 30 if suspicious_check['has_suspicious_patterns'] else 0,
            'pii': 40 if pii_check['has_personal_info'] else 0,
            'spam': spam_check['spam_score'] * 5
        }

        total_penalty = sum(score_penalties.values())
        results['moderation_score'] = max(0, 100 - total_penalty)

        # Determine approval status
        if banned_check['has_banned_topics']:
            results['is_approved'] = False
            results['issues'].append("Content contains banned topics")

        if pii_check['has_personal_info']:
            results['is_approved'] = False
            results['issues'].append("Content contains personal information")

        if suspicious_check['has_suspicious_patterns']:
            if self.strict_mode:
                results['is_approved'] = False
                results['issues'].append("Content matches suspicious patterns")
            else:
                results['warnings'].append("Content matches suspicious patterns - review recommended")

        if profanity_check['has_profanity']:
            if self.strict_mode or profanity_check['count'] > 3:
                results['is_approved'] = False
                results['issues'].append(f"Content contains profanity ({profanity_check['count']} instances)")
            else:
                results['warnings'].append(f"Content contains profanity ({profanity_check['count']} instances)")

        if spam_check['is_likely_spam']:
            results['is_approved'] = False
            results['issues'].append("Content appears to be spam")

        # Log results
        if not results['is_approved']:
            logger.warning(f"Content moderation FAILED: {results['issues']}")
        elif results['warnings']:
            logger.info(f"Content moderation PASSED with warnings: {results['warnings']}")
        else:
            logger.info(f"Content moderation PASSED (score: {results['moderation_score']}/100)")

        return results

    def sanitize_text(self, text: str, replacement: str = '***') -> str:
        """
        Remove or replace inappropriate content

        Args:
            text: Text to sanitize
            replacement: Replacement string for profanity

        Returns:
            Sanitized text
        """
        sanitized = text

        # Replace profanity
        for word in self.profanity_list:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            sanitized = pattern.sub(replacement, sanitized)

        # Remove personal info
        pii_patterns = [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
            (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]'),
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
            (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]'),
        ]

        for pattern, replace_with in pii_patterns:
            sanitized = re.sub(pattern, replace_with, sanitized)

        logger.info("Text sanitized")
        return sanitized

    def generate_moderation_report(self, results: Dict) -> str:
        """
        Generate a human-readable moderation report

        Args:
            results: Moderation results dictionary

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 50)
        report.append("CONTENT MODERATION REPORT")
        report.append("=" * 50)
        report.append(f"Timestamp: {results['timestamp']}")
        report.append(f"Status: {'APPROVED' if results['is_approved'] else 'REJECTED'}")
        report.append(f"Moderation Score: {results['moderation_score']}/100")
        report.append("")

        if results['issues']:
            report.append("ISSUES:")
            for issue in results['issues']:
                report.append(f"  ✗ {issue}")
            report.append("")

        if results['warnings']:
            report.append("WARNINGS:")
            for warning in results['warnings']:
                report.append(f"  ⚠ {warning}")
            report.append("")

        report.append("DETAILED CHECKS:")
        for check_name, check_result in results['checks'].items():
            report.append(f"  {check_name}: {check_result.get('severity', 'unknown')}")

        report.append("=" * 50)

        return "\n".join(report)


def main():
    """Example usage"""
    moderator = ContentModerator({
        'strict_mode': False,
        'allow_controversial': False
    })

    # Example 1: Clean content
    clean_text = "Learn how to create amazing videos with AI technology!"
    result = moderator.moderate_content(clean_text)
    print(moderator.generate_moderation_report(result))

    print("\n")

    # Example 2: Content with issues
    problematic_text = "Buy cheap drugs now! Contact me at test@example.com"
    result = moderator.moderate_content(problematic_text)
    print(moderator.generate_moderation_report(result))

    # Example 3: Sanitization
    print("\n" + "=" * 50)
    print("SANITIZATION EXAMPLE")
    print("=" * 50)
    dirty_text = "This is a damn good tutorial! Email me at user@test.com"
    clean = moderator.sanitize_text(dirty_text)
    print(f"Original: {dirty_text}")
    print(f"Sanitized: {clean}")


if __name__ == '__main__':
    main()
