"""Chunk documents with overlap for better retrieval"""
import logging
from typing import List

from app.schemas.documents import Document, Chunk

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunk documents with overlap for better retrieval"""
    
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 200,
        separator: str = "\n\n"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
    
    async def chunk_document(self, document: Document) -> List[Chunk]:
        """Chunk a document into smaller pieces"""
        text = document.content
        
        # Split by separator first
        splits = self._split_text(text, self.separator)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for i, split in enumerate(splits):
            split_length = len(split)
            
            if current_length + split_length > self.chunk_size and current_chunk:
                # Create chunk
                chunk_text = self.separator.join(current_chunk)
                chunk = self._create_chunk(
                    chunk_text,
                    document,
                    chunk_index=len(chunks)
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_length = 0
                overlap_parts = []
                for part in reversed(current_chunk):
                    if overlap_length + len(part) < self.chunk_overlap:
                        overlap_parts.insert(0, part)
                        overlap_length += len(part)
                    else:
                        break
                
                current_chunk = overlap_parts
                current_length = overlap_length
            
            current_chunk.append(split)
            current_length += split_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = self.separator.join(current_chunk)
            chunk = self._create_chunk(
                chunk_text,
                document,
                chunk_index=len(chunks)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_text(self, text: str, separator: str) -> List[str]:
        """Split text by separator"""
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)
        
        return [s for s in splits if s.strip()]
    
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
                'chunk_length': len(text)
            },
            chunk_id=chunk_id,
            doc_id=document.doc_id
        )

