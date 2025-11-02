"""Parse and extract information from LLM responses"""
import re
from typing import List, Dict, Optional


class ResponseParser:
    """Parse LLM responses to extract citations and structure"""
    
    def extract_citations(self, response: str) -> List[int]:
        """Extract citation numbers from response"""
        # Find patterns like [1], [2], (1), (2), etc.
        patterns = [
            r'\[(\d+)\]',  # [1], [2]
            r'\((\d+)\)',  # (1), (2)
            r'Context (\d+)',  # Context 1
        ]
        
        citations = set()
        for pattern in patterns:
            matches = re.findall(pattern, response)
            citations.update([int(m) for m in matches])
        
        return sorted(list(citations))
    
    def parse_structured_response(self, response: str) -> Dict:
        """Parse structured response (if formatted)"""
        # Extract answer section if present
        answer_match = re.search(r'## Answer:\s*(.+?)(?:##|$)', response, re.DOTALL)
        answer = answer_match.group(1).strip() if answer_match else response
        
        return {
            'answer': answer,
            'citations': self.extract_citations(response),
            'raw_response': response
        }
    
    def format_with_citations(self, response: str, chunks: List) -> str:
        """Format response with proper citation links"""
        citations = self.extract_citations(response)
        
        # Replace citation numbers with formatted citations
        formatted = response
        for citation_num in citations:
            if 1 <= citation_num <= len(chunks):
                chunk = chunks[citation_num - 1]
                source = chunk.metadata.get('filename') or chunk.metadata.get('source', 'Unknown')
                formatted = re.sub(
                    f'\\[{citation_num}\\]',
                    f'[{citation_num}](source: {source})',
                    formatted
                )
        
        return formatted

