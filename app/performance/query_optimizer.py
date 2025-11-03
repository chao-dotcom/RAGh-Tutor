"""Optimize queries for better retrieval"""
from typing import List
import re


class QueryOptimizer:
    """Optimize queries for better retrieval"""
    
    def __init__(self):
        self.stop_words = set([
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for',
            'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on',
            'that', 'the', 'to', 'was', 'will', 'with'
        ])
    
    def optimize(self, query: str) -> str:
        """Optimize query for better retrieval"""
        # Clean and normalize
        query = self._clean_query(query)
        
        # Remove stop words for very long queries
        if len(query.split()) > 10:
            query = self._remove_stop_words(query)
        
        # Extract key terms
        key_terms = self._extract_key_terms(query)
        if key_terms:
            query = ' '.join(key_terms[:20])  # Limit length
        
        return query
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize query"""
        # Remove special characters
        query = re.sub(r'[^\w\s]', ' ', query)
        
        # Normalize whitespace
        query = ' '.join(query.split())
        
        return query.lower()
    
    def _remove_stop_words(self, query: str) -> str:
        """Remove stop words from query"""
        words = query.split()
        filtered = [w for w in words if w not in self.stop_words]
        return ' '.join(filtered)
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract important terms from query"""
        words = query.split()
        
        # Prioritize longer words and capitalized words
        scored_words = []
        for word in words:
            score = len(word)
            if word[0].isupper():
                score += 5
            if word not in self.stop_words:
                score += 3
            scored_words.append((word, score))
        
        # Sort by score
        scored_words.sort(key=lambda x: x[1], reverse=True)
        
        return [word for word, score in scored_words]
    
    def suggest_query_improvements(self, query: str) -> List[str]:
        """Suggest improved query formulations"""
        suggestions = []
        
        # Add question form
        if '?' not in query:
            suggestions.append(f"What is {query}?")
            suggestions.append(f"How does {query} work?")
        
        # Add specificity
        suggestions.append(f"Explain {query} in detail")
        
        # Add context
        suggestions.append(f"{query} examples")
        suggestions.append(f"{query} use cases")
        
        return suggestions[:3]

