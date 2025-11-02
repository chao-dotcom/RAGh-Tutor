"""Unit tests for chunker"""
import pytest
from app.chunking.document_chunker import DocumentChunker
from app.schemas.documents import Document


@pytest.fixture
def chunker():
    return DocumentChunker(chunk_size=100, chunk_overlap=20)


@pytest.fixture
def sample_document():
    return Document(
        content="This is a test document. " * 50,
        metadata={'filename': 'test.txt'},
        doc_id='test_doc_1',
        source='/path/to/test.txt'
    )


@pytest.mark.asyncio
async def test_chunk_document(chunker, sample_document):
    chunks = await chunker.chunk_document(sample_document)
    
    assert len(chunks) > 0
    assert all(chunk.doc_id == sample_document.doc_id for chunk in chunks)
    assert all(len(chunk.content) <= chunker.chunk_size * 2 for chunk in chunks)


@pytest.mark.asyncio
async def test_chunk_overlap(chunker, sample_document):
    chunks = await chunker.chunk_document(sample_document)
    
    # Check overlap between consecutive chunks
    if len(chunks) > 1:
        for i in range(len(chunks) - 1):
            chunk1_end = chunks[i].content[-50:]
            chunk2_start = chunks[i + 1].content[:50]
            
            # Should have some overlap
            assert any(word in chunk2_start for word in chunk1_end.split() if len(word) > 3)

