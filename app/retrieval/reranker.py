"""Reranker for improving retrieval results"""
import logging
from typing import List, Tuple

from app.schemas.documents import Chunk

logger = logging.getLogger(__name__)


class Reranker:
    """Rerank retrieval results using cross-encoder"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize reranking model"""
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name)
        except ImportError:
            logger.warning("sentence-transformers not available for reranking")
    
    async def rerank(
        self,
        query: str,
        candidates: List[Tuple[Chunk, float]],
        top_k: int = 5
    ) -> List[Tuple[Chunk, float]]:
        """Rerank candidates using cross-encoder"""
        if not candidates:
            return []
        
        if not self.model:
            return candidates[:top_k]
        
        # Prepare pairs for cross-encoder
        pairs = [[query, chunk.content] for chunk, _ in candidates]
        
        # Get reranking scores
        scores = self.model.predict(pairs)
        
        # Combine with original candidates
        reranked = [
            (candidates[i][0], float(scores[i]))
            for i in range(len(candidates))
        ]
        
        # Sort by new scores
        reranked.sort(key=lambda x: x[1], reverse=True)
        
        return reranked[:top_k]

