"""Document schemas"""
from pydantic import BaseModel
from typing import Dict, Any, Optional


class Document(BaseModel):
    """Document schema"""
    content: str
    metadata: Dict[str, Any]
    doc_id: str
    source: str


class Chunk(BaseModel):
    """Chunk schema"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    doc_id: str
    embedding: Optional[Any] = None

