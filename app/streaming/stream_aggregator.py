"""Aggregate streaming chunks"""
from typing import List


class StreamAggregator:
    """Aggregate streaming response chunks"""
    
    def __init__(self):
        self.chunks: List[str] = []
    
    def add_chunk(self, chunk: str):
        """Add a chunk"""
        self.chunks.append(chunk)
    
    def get_full_text(self) -> str:
        """Get full aggregated text"""
        return "".join(self.chunks)
    
    def reset(self):
        """Reset aggregator"""
        self.chunks.clear()

