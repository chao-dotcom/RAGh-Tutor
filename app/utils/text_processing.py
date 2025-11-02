"""Text processing utilities"""
import re
from typing import List


def clean_text(text: str) -> str:
    """Clean text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters (keep alphanumeric and common punctuation)
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-]', '', text)
    return text.strip()


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction (in production, use more sophisticated methods)
    words = text.lower().split()
    # Filter stop words (simplified)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    # Count frequency
    from collections import Counter
    return [word for word, _ in Counter(keywords).most_common(top_n)]

