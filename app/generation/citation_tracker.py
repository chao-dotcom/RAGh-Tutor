"""Track and format citations in responses"""
import re
from typing import List, Dict, Set, Any

from app.schemas.documents import Chunk


class CitationTracker:
    """Track and format citations in responses"""
    
    def __init__(self):
        self.citation_pattern = re.compile(r'\[([^\]]+)\]')
        self.citation_map: Dict[str, Chunk] = {}
    
    def extract_citations(self, text: str) -> Set[str]:
        """Extract all citation IDs from text"""
        citations = self.citation_pattern.findall(text)
        return set(citations)
    
    def format_citations(
        self,
        text: str,
        chunks: List[Chunk]
    ) -> Dict[str, Any]:
        """Format text with citation metadata"""
        
        # Extract citations
        cited_ids = self.extract_citations(text)
        
        # Build citation map
        citation_map = {}
        for chunk in chunks:
            if chunk.chunk_id in cited_ids:
                citation_map[chunk.chunk_id] = {
                    'source': chunk.metadata.get('source', 'Unknown'),
                    'filename': chunk.metadata.get('filename', 'Unknown'),
                    'chunk_index': chunk.metadata.get('chunk_index', 0),
                    'doc_id': chunk.doc_id
                }
        
        return {
            'text': text,
            'citations': citation_map,
            'citation_count': len(cited_ids)
        }
    
    def add_footnotes(
        self,
        text: str,
        chunks: List[Chunk]
    ) -> str:
        """Add footnote-style citations"""
        
        cited_ids = self.extract_citations(text)
        
        if not cited_ids:
            return text
        
        # Build footnotes
        footnotes = ["\n\n## Sources\n"]
        for i, chunk_id in enumerate(sorted(cited_ids), 1):
            # Find chunk
            chunk = next((c for c in chunks if c.chunk_id == chunk_id), None)
            if chunk:
                source = chunk.metadata.get('filename', 'Unknown')
                footnotes.append(f"[{i}] {source} - {chunk_id}")
        
        return text + "\n".join(footnotes)
    
    def add_citations(self, chunks: List[Chunk]):
        """Add chunks to citation map (backward compatibility)"""
        for i, chunk in enumerate(chunks, 1):
            self.citation_map[str(i)] = chunk
    
    def get_citation_info(self, citation_num: int) -> Dict:
        """Get information about a citation (backward compatibility)"""
        chunk = self.citation_map.get(str(citation_num))
        if not chunk:
            return None
        
        return {
            'chunk_id': chunk.chunk_id,
            'doc_id': chunk.doc_id,
            'source': chunk.metadata.get('source') or chunk.metadata.get('filename'),
            'preview': chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
            'metadata': chunk.metadata
        }
    
    def clear(self):
        """Clear citation map"""
        self.citation_map.clear()

