"""Unit tests for retrieval"""
import pytest
import numpy as np
from app.retrieval.vector_store import InMemoryVectorStore
from app.schemas.documents import Chunk


@pytest.fixture
def vector_store():
    return InMemoryVectorStore(dimension=768)


@pytest.fixture
def sample_chunks():
    return [
        Chunk(
            content=f"Test content {i}",
            metadata={'index': i},
            chunk_id=f'chunk_{i}',
            doc_id='test_doc'
        )
        for i in range(10)
    ]


def test_add_and_search(vector_store, sample_chunks):
    # Generate random embeddings
    embeddings = np.random.rand(10, 768).astype('float32')
    
    # Add to store
    vector_store.add(embeddings, sample_chunks)
    
    assert vector_store.size == 10
    
    # Search
    query_embedding = np.random.rand(768).astype('float32')
    results = vector_store.search(query_embedding, top_k=5)
    
    assert len(results) == 5
    assert all(isinstance(chunk, Chunk) for chunk, _ in results)
    assert all(isinstance(score, float) for _, score in results)


def test_get_by_id(vector_store, sample_chunks):
    embeddings = np.random.rand(10, 768).astype('float32')
    vector_store.add(embeddings, sample_chunks)
    
    chunk = vector_store.get_by_id('chunk_5')
    assert chunk is not None
    assert chunk.chunk_id == 'chunk_5'

