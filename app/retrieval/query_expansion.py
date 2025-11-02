"""Query expansion for better retrieval"""
import logging
import re
from typing import List

logger = logging.getLogger(__name__)


class QueryExpander:
    """Expand queries with synonyms and variations"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    def expand_query(self, query: str) -> List[str]:
        """Generate query variations"""
        variations = [query]  # Original query
        
        # Add simple variations
        variations.append(self._to_question(query))
        variations.append(self._add_context_words(query))
        
        return variations
    
    def _to_question(self, query: str) -> str:
        """Convert statement to question"""
        if '?' in query:
            return query
        
        # Simple heuristic
        question_words = ['what', 'how', 'why', 'when', 'where', 'who']
        if any(query.lower().startswith(w) for w in question_words):
            return query + '?'
        
        return f"What is {query}?"
    
    def _add_context_words(self, query: str) -> str:
        """Add contextual words"""
        return f"explain {query}"
    
    async def expand_with_llm(self, query: str) -> List[str]:
        """Use LLM to generate query variations"""
        if not self.llm_client:
            return self.expand_query(query)
        
        prompt = f"""Generate 3 alternative phrasings of this query:
Query: {query}

Alternative phrasings:
1."""
        
        try:
            response = await self.llm_client.generate(prompt, max_tokens=200)
            
            # Parse response to extract variations
            variations = [query]  # Include original
            lines = response.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('Alternative'):
                    # Remove numbering
                    variation = re.sub(r'^\d+\.\s*', '', line).strip()
                    if variation:
                        variations.append(variation)
            
            return variations[:4]  # Limit to 4 total
        except Exception as e:
            logger.warning(f"LLM query expansion failed: {e}")
            return self.expand_query(query)
    
    async def expand(self, query: str) -> str:
        """Expand query (backward compatibility)"""
        variations = self.expand_query(query)
        return variations[0] if variations else query

