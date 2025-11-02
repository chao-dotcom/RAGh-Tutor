"""Content moderation for queries and responses"""
import re
from typing import Tuple, List, Dict
import logging

logger = logging.getLogger(__name__)


class ContentModerator:
    """Content moderation for queries and responses"""
    
    def __init__(self):
        # PII patterns
        self.pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            'ip_address': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
        }
        
        # Harmful content patterns
        self.harmful_patterns = [
            r'\b(kill|murder|suicide|bomb|weapon)\b',
            r'\b(hack|exploit|vulnerability|bypass)\b',
            r'\b(drug|cocaine|heroin|meth)\b'
        ]
        
        # Prompt injection patterns
        self.injection_patterns = [
            r'ignore\s+(previous|above|prior)\s+instructions',
            r'forget\s+everything',
            r'system\s+prompt',
            r'you\s+are\s+now',
            r'act\s+as\s+if'
        ]
    
    async def moderate(self, text: str) -> Dict:
        """Check if content violates policies"""
        violations = []
        
        # Check for PII
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(text):
                logger.warning(f"PII detected: {pii_type}")
                violations.append(f"Contains {pii_type}")
        
        # Check for harmful content
        for pattern in self.harmful_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Harmful content detected")
                violations.append("Contains potentially harmful content")
                break
        
        # Check for prompt injection
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Prompt injection detected")
                violations.append("Potential prompt injection detected")
                break
        
        return {
            'safe': len(violations) == 0,
            'violations': violations
        }
    
    def check_content(self, text: str) -> Tuple[bool, str]:
        """
        Check if content is safe
        Returns: (is_safe, reason)
        """
        # Check for PII
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(text):
                logger.warning(f"PII detected: {pii_type}")
                return False, f"Contains {pii_type}"
        
        # Check for harmful content
        for pattern in self.harmful_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Harmful content detected")
                return False, "Contains potentially harmful content"
        
        # Check for prompt injection
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Prompt injection detected")
                return False, "Potential prompt injection detected"
        
        return True, ""
    
    def redact_pii(self, text: str) -> str:
        """Redact PII from text"""
        result = text
        
        for pii_type, pattern in self.pii_patterns.items():
            result = pattern.sub(f'[REDACTED_{pii_type.upper()}]', result)
        
        return result
    
    def detect_jailbreak_attempt(self, text: str) -> bool:
        """Detect jailbreak attempts"""
        jailbreak_indicators = [
            'ignore your instructions',
            'pretend you are',
            'roleplay as',
            'simulate being',
            'you must comply'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in jailbreak_indicators)

