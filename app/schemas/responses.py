"""Response schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChunkResponse(BaseModel):
    """Chunk response schema"""
    content: str
    chunk_id: str
    doc_id: str
    metadata: Dict[str, Any]
    score: Optional[float] = None


class QueryResponse(BaseModel):
    """Query response schema"""
    query: str
    results: List[ChunkResponse]
    total_results: int
    retrieval_time: Optional[float] = None


class ChatResponse(BaseModel):
    """Chat response schema"""
    response: str
    sources: List[ChunkResponse]
    conversation_id: str
    tokens_used: Optional[int] = None


class QueryResponse(BaseModel):
    """Query response schema (updated)"""
    answer: str
    citations: Dict[str, Any]
    session_id: str
    chunks_used: int
    tools_used: Optional[List[Dict]] = Field(default=[], description="Tools used in agent execution")


class MetricsResponse(BaseModel):
    """Metrics response schema"""
    total_queries: int
    average_latency: float
    error_rate: float
    cache_hit_rate: float


class DocumentResponse(BaseModel):
    """Document response schema"""
    doc_id: str
    source: str
    content_preview: str
    metadata: Dict[str, Any]
    chunks_count: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    documents_indexed: int = Field(..., description="Number of documents indexed")
    vector_store_size: Optional[int] = Field(None, description="Vector store size (backward compat)")
    uptime: Optional[float] = None
    
    @property
    def vector_store_size(self) -> int:
        """Backward compatibility property"""
        return self.documents_indexed

