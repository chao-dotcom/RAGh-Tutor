"""Script to index documents"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.processing.document_loader import DocumentLoader
from app.chunking.document_chunker import DocumentChunker
from app.embedding.embedding_model import EmbeddingModel
from app.embedding.batch_embedder import BatchEmbedder
from app.retrieval.vector_store import InMemoryVectorStore
from app.config import settings


async def main():
    """Index documents"""
    print("Loading documents...")
    loader = DocumentLoader(base_path=settings.DOCUMENTS_PATH)
    documents = await loader.load_all_documents()
    print(f"Loaded {len(documents)} documents")
    
    print("Chunking documents...")
    chunker = DocumentChunker(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    all_chunks = []
    for doc in documents:
        chunks = await chunker.chunk_document(doc)
        all_chunks.extend(chunks)
    print(f"Created {len(all_chunks)} chunks")
    
    print("Generating embeddings...")
    embedding_model = EmbeddingModel(model_name=settings.EMBEDDING_MODEL)
    batch_embedder = BatchEmbedder(embedding_model)
    embeddings = await batch_embedder.embed_chunks(all_chunks)
    print(f"Generated embeddings for {len(all_chunks)} chunks")
    
    print("Indexing in vector store...")
    vector_store = InMemoryVectorStore(dimension=settings.EMBEDDING_DIMENSION)
    vector_store.add(embeddings, all_chunks)
    vector_store.save(settings.VECTOR_STORE_PATH)
    print(f"Indexed {vector_store.size} chunks in vector store")


if __name__ == "__main__":
    asyncio.run(main())

