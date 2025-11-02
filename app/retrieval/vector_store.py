"""FAISS-based in-memory vector store"""
import logging
import pickle
from typing import List, Tuple, Optional
import numpy as np

from app.schemas.documents import Chunk

logger = logging.getLogger(__name__)


class InMemoryVectorStore:
    """FAISS-based in-memory vector store"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index = None
        self.chunks: List[Chunk] = []
        self.id_to_idx = {}  # chunk_id -> index mapping
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index"""
        try:
            import faiss
            # Inner product for cosine similarity (after normalization)
            self.index = faiss.IndexFlatIP(self.dimension)
        except ImportError:
            logger.error("FAISS not installed. Install with: pip install faiss-cpu or faiss-gpu")
            raise
    
    def add(
        self,
        embeddings: np.ndarray,
        chunks: List[Chunk]
    ):
        """Add embeddings and chunks to store"""
        if self.index is None:
            raise RuntimeError("FAISS index not initialized")
        
        if len(embeddings) != len(chunks):
            raise ValueError("Number of embeddings must match number of chunks")
        
        # Normalize embeddings for cosine similarity
        import faiss
        embeddings = embeddings.astype('float32')
        faiss.normalize_L2(embeddings)
        
        # Add to FAISS index
        start_idx = len(self.chunks)
        self.index.add(embeddings)
        
        # Store chunks
        for i, chunk in enumerate(chunks):
            # Store embedding reference (not the full array to save memory)
            self.chunks.append(chunk)
            self.id_to_idx[chunk.chunk_id] = start_idx + i
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10
    ) -> List[Tuple[Chunk, float]]:
        """Search for most similar chunks"""
        if self.index is None:
            raise RuntimeError("FAISS index not initialized")
        
        if len(self.chunks) == 0:
            return []
        
        import faiss
        
        # Normalize query
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        k = min(top_k, len(self.chunks))
        scores, indices = self.index.search(query_embedding, k)
        
        # Return chunks with scores
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if 0 <= idx < len(self.chunks):  # Valid index
                results.append((self.chunks[idx], float(score)))
        
        return results
    
    def get_by_id(self, chunk_id: str) -> Optional[Chunk]:
        """Retrieve chunk by ID"""
        idx = self.id_to_idx.get(chunk_id)
        if idx is not None and 0 <= idx < len(self.chunks):
            return self.chunks[idx]
        return None
    
    def save(self, path: str):
        """Save index and chunks to disk"""
        import faiss
        
        faiss.write_index(self.index, f"{path}.index")
        with open(f"{path}.chunks", 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'id_to_idx': self.id_to_idx,
                'dimension': self.dimension
            }, f)
        logger.info(f"Saved vector store to {path}")
    
    def load(self, path: str):
        """Load index and chunks from disk"""
        import faiss
        
        self.index = faiss.read_index(f"{path}.index")
        with open(f"{path}.chunks", 'rb') as f:
            data = pickle.load(f)
            self.chunks = data['chunks']
            self.id_to_idx = data['id_to_idx']
            self.dimension = data.get('dimension', 768)
        logger.info(f"Loaded vector store from {path}")
    
    def clear(self):
        """Clear all data"""
        if self.index:
            self.index.reset()
        self.chunks.clear()
        self.id_to_idx.clear()
    
    @property
    def size(self) -> int:
        """Number of chunks in store"""
        return len(self.chunks)

