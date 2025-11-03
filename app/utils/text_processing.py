"""Text processing utilities"""
import re
from typing import List, Dict, Optional
from collections import Counter


def clean_text(text: str) -> str:
    """Clean text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters (keep alphanumeric and common punctuation)
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-]', '', text)
    return text.strip()


def count_words(text: str) -> int:
    """Count words in text"""
    if not text or not text.strip():
        return 0
    return len(text.split())


def count_characters(text: str, include_spaces: bool = True) -> int:
    """Count characters in text"""
    if not text:
        return 0
    if include_spaces:
        return len(text)
    return len(text.replace(' ', '').replace('\n', '').replace('\t', ''))


def estimate_tokens(text: str, method: str = "word") -> int:
    """
    Estimate token count for text
    
    Args:
        text: Input text
        method: Estimation method
            - "word": ~1.3 tokens per word (common approximation)
            - "char": ~4 characters per token (rough approximation)
            - "simple": word count (1:1)
    
    Returns:
        Estimated token count
    """
    if not text or not text.strip():
        return 0
    
    if method == "word":
        # Common approximation: ~1.3 tokens per word
        return int(len(text.split()) * 1.3)
    elif method == "char":
        # Rough approximation: ~4 characters per token
        return int(len(text) / 4)
    elif method == "simple":
        # Simple 1:1 word to token
        return len(text.split())
    else:
        # Default to word-based estimation
        return int(len(text.split()) * 1.3)


def get_word_statistics(text: str) -> Dict[str, int]:
    """
    Get comprehensive word statistics
    
    Returns:
        Dictionary with word count, character count, sentence count, etc.
    """
    if not text or not text.strip():
        return {
            'word_count': 0,
            'character_count': 0,
            'character_count_no_spaces': 0,
            'sentence_count': 0,
            'paragraph_count': 0,
            'unique_words': 0,
            'estimated_tokens': 0
        }
    
    words = text.split()
    sentences = re.split(r'[.!?]+\s+', text)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    return {
        'word_count': len(words),
        'character_count': len(text),
        'character_count_no_spaces': len(text.replace(' ', '')),
        'sentence_count': len([s for s in sentences if s.strip()]),
        'paragraph_count': len(paragraphs),
        'unique_words': len(set(word.lower() for word in words)),
        'estimated_tokens': estimate_tokens(text)
    }


def count_words_by_category(text: str) -> Dict[str, int]:
    """
    Count words by category (numbers, uppercase, lowercase, etc.)
    
    Returns:
        Dictionary with counts by category
    """
    if not text:
        return {
            'total_words': 0,
            'uppercase_words': 0,
            'lowercase_words': 0,
            'numbers': 0,
            'mixed_case': 0
        }
    
    words = text.split()
    
    stats = {
        'total_words': len(words),
        'uppercase_words': 0,
        'lowercase_words': 0,
        'numbers': 0,
        'mixed_case': 0
    }
    
    for word in words:
        # Remove punctuation for checking
        clean_word = re.sub(r'[^\w]', '', word)
        
        if clean_word.isdigit():
            stats['numbers'] += 1
        elif clean_word.isupper() and len(clean_word) > 1:
            stats['uppercase_words'] += 1
        elif clean_word.islower():
            stats['lowercase_words'] += 1
        elif any(c.isupper() for c in clean_word) and any(c.islower() for c in clean_word):
            stats['mixed_case'] += 1
    
    return stats


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction (in production, use more sophisticated methods)
    words = text.lower().split()
    # Filter stop words (simplified)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    # Count frequency
    return [word for word, _ in Counter(keywords).most_common(top_n)]


def get_word_frequency(text: str, top_n: Optional[int] = None) -> Dict[str, int]:
    """
    Get word frequency distribution
    
    Args:
        text: Input text
        top_n: Return only top N words (None for all)
    
    Returns:
        Dictionary mapping words to their frequencies
    """
    if not text:
        return {}
    
    # Clean and normalize words
    words = re.findall(r'\b\w+\b', text.lower())
    word_counts = Counter(words)
    
    if top_n:
        return dict(word_counts.most_common(top_n))
    
    return dict(word_counts)

