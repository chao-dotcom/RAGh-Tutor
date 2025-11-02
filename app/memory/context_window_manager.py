"""Context window manager"""
import logging
from typing import List, Dict
from app.schemas.documents import Chunk

logger = logging.getLogger(__name__)


class ContextWindowManager:
    """Manage context window for LLM"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def fit_in_window(
        self,
        chunks: List[Chunk],
        query: str,
        system_prompt: str = "",
        max_chunks: int = None
    ) -> List[Chunk]:
        """Select chunks that fit in context window"""
        
        query_tokens = self.estimate_tokens(query)
        system_tokens = self.estimate_tokens(system_prompt)
        reserved_tokens = 500  # For response
        
        available_tokens = self.max_tokens - query_tokens - system_tokens - reserved_tokens
        
        selected_chunks = []
        current_tokens = 0
        
        for chunk in chunks:
            chunk_tokens = self.estimate_tokens(chunk.content)
            
            if current_tokens + chunk_tokens <= available_tokens:
                selected_chunks.append(chunk)
                current_tokens += chunk_tokens
            else:
                break
            
            if max_chunks and len(selected_chunks) >= max_chunks:
                break
        
        return selected_chunks

