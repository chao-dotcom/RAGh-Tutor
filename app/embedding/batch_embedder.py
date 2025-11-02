"""Batch embedding processing"""
import asyncio
import logging
from typing import List
import numpy as np

from app.embedding.embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)


class BatchEmbedder:
    """Batch embedding processor for large-scale indexing"""
    
    def __init__(self, embedding_model: EmbeddingModel, batch_size: int = 32):
        self.embedding_model = embedding_model
        self.batch_size = batch_size
    
    async def embed_chunks(self, chunks: List) -> np.ndarray:
        """Embed a list of chunks in batches"""
        texts = [chunk.content for chunk in chunks]
        
        # Process in batches
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            embeddings = await self.embedding_model.encode_async(batch, batch_size=self.batch_size)
            all_embeddings.append(embeddings)
            
            logger.info(f"Embedded batch {i//self.batch_size + 1}/{(len(texts)-1)//self.batch_size + 1}")
        
        # Concatenate all embeddings
        if all_embeddings:
            return np.vstack(all_embeddings)
        return np.array([])
    
    async def embed_single(self, text: str) -> np.ndarray:
        """Embed a single text"""
        embeddings = await self.embedding_model.encode_async([text])
        return embeddings[0]

