"""Dependency injection for FastAPI"""
from functools import lru_cache
from typing import Optional
from app.config import settings
from app.embedding.embedding_model import EmbeddingModel
from app.retrieval.vector_store import InMemoryVectorStore
from app.chunking.document_chunker import DocumentChunker
from app.processing.document_loader import DocumentLoader


@lru_cache()
def get_embedding_model() -> EmbeddingModel:
    """Get singleton embedding model instance"""
    return EmbeddingModel(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.EMBEDDING_DEVICE
    )


@lru_cache()
def get_vector_store() -> InMemoryVectorStore:
    """Get singleton vector store instance"""
    return InMemoryVectorStore(dimension=settings.EMBEDDING_DIMENSION)


@lru_cache()
def get_document_chunker() -> DocumentChunker:
    """Get singleton document chunker instance"""
    return DocumentChunker(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separator=settings.CHUNK_SEPARATOR
    )


@lru_cache()
def get_document_loader() -> DocumentLoader:
    """Get singleton document loader instance"""
    return DocumentLoader(base_path=settings.DOCUMENTS_PATH)

