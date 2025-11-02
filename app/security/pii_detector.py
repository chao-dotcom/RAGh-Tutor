"""PII detection"""
import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)


class PIIDetector:
    """Detect personally identifiable information"""
    
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'phone': r'\b\d{3}-\d{3}-\d{4}\b',
        }
    
    def detect(self, text: str) -> Dict:
        """Detect PII in text"""
        findings = {}
        
        for pii_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                findings[pii_type] = matches
        
        return {
            'has_pii': len(findings) > 0,
            'findings': findings
        }
    
    def mask(self, text: str) -> str:
        """Mask PII in text"""
        masked = text
        findings = self.detect(text)
        
        for pii_type, matches in findings['findings'].items():
            for match in matches:
                if pii_type == 'email':
                    masked = masked.replace(match, '[EMAIL]')
                elif pii_type == 'ssn':
                    masked = masked.replace(match, '[SSN]')
                elif pii_type == 'phone':
                    masked = masked.replace(match, '[PHONE]')
        
        return masked

