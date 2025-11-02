"""Hybrid search combining vector and keyword search"""
import logging
from typing import List, Tuple
import numpy as np

from app.retrieval.vector_store import InMemoryVectorStore
from app.schemas.documents import Chunk

logger = logging.getLogger(__name__)


class HybridSearchStore:
    """Combines vector search with BM25 keyword search"""
    
    def __init__(self, vector_store: InMemoryVectorStore):
        self.vector_store = vector_store
        self.bm25 = None
        self.tokenized_corpus = []
    
    def build_bm25_index(self):
        """Build BM25 index from chunks"""
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            logger.error("rank-bm25 not installed. Install with: pip install rank-bm25")
            raise
        
        corpus = [chunk.content for chunk in self.vector_store.chunks]
        self.tokenized_corpus = [doc.lower().split() for doc in corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        logger.info(f"Built BM25 index for {len(corpus)} documents")
    
    def hybrid_search(
        self,
        query: str,
        query_embedding: np.ndarray,
        top_k: int = 10,
        alpha: float = 0.7  # Weight for vector search (1-alpha for BM25)
    ) -> List[Tuple[Chunk, float]]:
        """Perform hybrid search combining vector and keyword scores"""
        
        if self.bm25 is None:
            self.build_bm25_index()
        
        # Vector search
        vector_results = self.vector_store.search(query_embedding, top_k=top_k*2)
        
        # BM25 search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Combine scores
        combined_scores = {}
        
        # Add vector scores
        for chunk, score in vector_results:
            combined_scores[chunk.chunk_id] = {
                'chunk': chunk,
                'vector_score': score,
                'bm25_score': 0.0
            }
        
        # Add BM25 scores
        max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 and max(bm25_scores) > 0 else 1.0
        
        for idx, score in enumerate(bm25_scores):
            if idx < len(self.vector_store.chunks):
                chunk = self.vector_store.chunks[idx]
                if chunk.chunk_id in combined_scores:
                    combined_scores[chunk.chunk_id]['bm25_score'] = score / max_bm25 if max_bm25 > 0 else 0
                else:
                    combined_scores[chunk.chunk_id] = {
                        'chunk': chunk,
                        'vector_score': 0.0,
                        'bm25_score': score / max_bm25 if max_bm25 > 0 else 0
                    }
        
        # Normalize and combine
        results = []
        for chunk_id, scores in combined_scores.items():
            # Weighted combination
            combined_score = alpha * scores['vector_score'] + (1 - alpha) * scores['bm25_score']
            results.append((scores['chunk'], combined_score))
        
        # Sort by combined score
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]

