"""Request schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class QueryRequest(BaseModel):
    """Query request schema"""
    query: str = Field(..., min_length=1, max_length=2000, description="User query")
    session_id: Optional[str] = Field(None, description="Session ID for conversation")
    user_id: Optional[str] = Field(None, description="User ID")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of results to return")
    retrieval_mode: Optional[str] = Field("hybrid", description="Retrieval mode: vector, keyword, hybrid")
    include_metadata: Optional[bool] = Field(True, description="Include metadata in response")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    use_agent: Optional[bool] = Field(False, description="Use agent with tools")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is retrieval augmented generation?",
                "session_id": "abc123",
                "top_k": 5
            }
        }


class DocumentUploadRequest(BaseModel):
    """Document upload request"""
    file_path: Optional[str] = Field(None, description="Local file path")
    url: Optional[str] = Field(None, description="URL to fetch document from")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    stream: Optional[bool] = Field(False, description="Enable streaming response")
    use_memory: Optional[bool] = Field(True, description="Use conversation memory")


class IndexRequest(BaseModel):
    """Index documents request"""
    paths: Optional[List[str]] = Field(None, description="Specific paths to index")
    recursive: Optional[bool] = Field(True, description="Recursively index directory")


class FeedbackRequest(BaseModel):
    """Feedback submission request"""
    query: str
    response: str
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    feedback_text: Optional[str] = Field(None, description="Free-form feedback")
    session_id: Optional[str] = Field(None, description="Session ID")


class MultiDocumentQueryRequest(BaseModel):
    """Multi-document query request"""
    query: str
    doc_ids: List[str]
    top_k_per_doc: int = Field(3, ge=1, le=10, description="Top k chunks per document")

