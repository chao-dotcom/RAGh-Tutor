"""Specialized chunkers for different document types"""
import logging
from typing import List

from app.schemas.documents import Document, Chunk

logger = logging.getLogger(__name__)


class SpecializedChunker:
    """Specialized chunkers for code, markdown, etc."""
    
    async def chunk_code(self, document: Document, language: str = None) -> List[Chunk]:
        """Chunk code by functions/classes"""
        content = document.content
        chunks = []
        
        # Simple implementation - split by function/class definitions
        lines = content.split('\n')
        current_chunk = []
        chunk_index = 0
        
        for line in lines:
            current_chunk.append(line)
            
            # Check if line starts a new function/class
            if line.strip().startswith(('def ', 'class ', 'async def ')):
                if current_chunk:
                    chunk_text = '\n'.join(current_chunk)
                    chunk = Chunk(
                        content=chunk_text,
                        metadata={**document.metadata, 'chunk_index': chunk_index, 'type': 'code'},
                        chunk_id=f"{document.doc_id}_chunk_{chunk_index}",
                        doc_id=document.doc_id
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_chunk = []
        
        # Add remaining
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunk = Chunk(
                content=chunk_text,
                metadata={**document.metadata, 'chunk_index': chunk_index, 'type': 'code'},
                chunk_id=f"{document.doc_id}_chunk_{chunk_index}",
                doc_id=document.doc_id
            )
            chunks.append(chunk)
        
        return chunks
    
    async def chunk_markdown(self, document: Document) -> List[Chunk]:
        """Chunk markdown by headings"""
        content = document.content
        chunks = []
        lines = content.split('\n')
        
        current_section = []
        current_heading = None
        chunk_index = 0
        
        for line in lines:
            if line.strip().startswith('#'):
                # New heading found
                if current_section and current_heading:
                    chunk_text = '\n'.join(current_section)
                    chunk = Chunk(
                        content=chunk_text,
                        metadata={**document.metadata, 'chunk_index': chunk_index, 'heading': current_heading, 'type': 'markdown'},
                        chunk_id=f"{document.doc_id}_chunk_{chunk_index}",
                        doc_id=document.doc_id
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                current_heading = line.strip()
                current_section = [line]
            else:
                current_section.append(line)
        
        # Add final section
        if current_section:
            chunk_text = '\n'.join(current_section)
            chunk = Chunk(
                content=chunk_text,
                metadata={**document.metadata, 'chunk_index': chunk_index, 'heading': current_heading, 'type': 'markdown'},
                chunk_id=f"{document.doc_id}_chunk_{chunk_index}",
                doc_id=document.doc_id
            )
            chunks.append(chunk)
        
        return chunks

