"""Event schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class Event(BaseModel):
    """Base event schema"""
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class QueryEvent(Event):
    """Query event"""
    query: str
    results_count: int
    response_time: float


class DocumentIndexedEvent(Event):
    """Document indexed event"""
    doc_id: str
    chunks_count: int

