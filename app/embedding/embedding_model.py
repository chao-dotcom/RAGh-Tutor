"""Wrapper for embedding model with batching support"""
import logging
import asyncio
import numpy as np
from typing import List, Union

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Wrapper for embedding model with batching support"""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-mpnet-base-v2",
        device: str = None
    ):
        self.model_name = model_name
        self.device = device or self._get_device()
        self.model = None
        self.dimension = None
        self._initialize_model()
    
    def _get_device(self) -> str:
        """Get available device"""
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self.dimension = self.model.get_sentence_embedding_dimension()
        except ImportError:
            logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False,
        normalize: bool = True
    ) -> np.ndarray:
        """Generate embeddings for text(s)"""
        if not self.model:
            raise RuntimeError("Model not initialized")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        return embeddings
    
    async def encode_async(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> np.ndarray:
        """Async wrapper for encoding"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.encode,
            texts,
            batch_size,
            False,  # show_progress
            True    # normalize
        )

