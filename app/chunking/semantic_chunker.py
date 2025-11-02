"""Semantic chunking based on meaning"""
import logging
from typing import List

from app.schemas.documents import Document, Chunk

logger = logging.getLogger(__name__)


class SemanticChunker:
    """Chunk documents based on semantic similarity"""
    
    def __init__(
        self,
        embedding_model=None,
        similarity_threshold: float = 0.5,
        max_chunk_size: int = 1000
    ):
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        self.max_chunk_size = max_chunk_size
    
    async def chunk_document(self, document: Document) -> List[Chunk]:
        """Chunk document by semantic breaks"""
        if not self.embedding_model:
            raise ValueError("Embedding model required for semantic chunking")
        
        # Split into sentences
        sentences = self._split_into_sentences(document.content)
        
        if len(sentences) <= 1:
            return [self._create_chunk(document.content, document, 0)]
        
        # Get embeddings for all sentences
        embeddings = await self.embedding_model.encode_async(sentences)
        
        # Find semantic breaks
        breaks = [0]
        for i in range(len(embeddings) - 1):
            similarity = self._cosine_similarity(
                embeddings[i],
                embeddings[i + 1]
            )
            
            if similarity < self.similarity_threshold:
                breaks.append(i + 1)
        
        breaks.append(len(sentences))
        
        # Create chunks from breaks
        chunks = []
        for i in range(len(breaks) - 1):
            start = breaks[i]
            end = breaks[i + 1]
            
            chunk_sentences = sentences[start:end]
            chunk_text = ' '.join(chunk_sentences)
            
            # Split if too large
            if len(chunk_text) > self.max_chunk_size:
                sub_chunks = self._split_large_chunk(chunk_text, document, len(chunks))
                chunks.extend(sub_chunks)
            else:
                chunk = self._create_chunk(chunk_text, document, len(chunks))
                chunks.append(chunk)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_large_chunk(
        self,
        text: str,
        document: Document,
        start_index: int
    ) -> List[Chunk]:
        """Split large chunk into smaller pieces"""
        chunks = []
        words = text.split()
        
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1
            
            if current_length >= self.max_chunk_size:
                chunk_text = ' '.join(current_chunk)
                chunk = self._create_chunk(
                    chunk_text,
                    document,
                    start_index + len(chunks)
                )
                chunks.append(chunk)
                current_chunk = []
                current_length = 0
        
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk = self._create_chunk(
                chunk_text,
                document,
                start_index + len(chunks)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(
        self,
        text: str,
        document: Document,
        chunk_index: int
    ) -> Chunk:
        """Create a chunk object"""
        chunk_id = f"{document.doc_id}_chunk_{chunk_index}"
        
        return Chunk(
            content=text,
            metadata={
                **document.metadata,
                'chunk_index': chunk_index,
                'doc_id': document.doc_id,
                'source': document.source,
                'chunking_method': 'semantic'
            },
            chunk_id=chunk_id,
            doc_id=document.doc_id
        )
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            similarity = cosine_similarity(
                vec1.reshape(1, -1),
                vec2.reshape(1, -1)
            )[0][0]
            return float(similarity)
        except ImportError:
            # Fallback to manual calculation
            import numpy as np
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            return dot_product / (norm1 * norm2) if norm1 * norm2 > 0 else 0.0

