"""Configuration management for RAG system"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_TITLE: str = "RAG System API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Production-ready RAG System"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Embedding Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    EMBEDDING_DEVICE: Optional[str] = None
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DIMENSION: int = 768
    
    # Chunking Settings
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 200
    CHUNK_SEPARATOR: str = "\n\n"
    
    # Vector Store Settings
    VECTOR_STORE_PATH: str = "./data/vector_store"
    FAISS_INDEX_PATH: str = "./data/embeddings/faiss.index"
    
    # LLM Settings
    LLM_PROVIDER: str = "openai"  # openai, anthropic, local
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    
    # Retrieval Settings
    RETRIEVAL_TOP_K: int = 10
    RETRIEVAL_MODE: str = "hybrid"  # vector, keyword, hybrid
    HYBRID_SEARCH_ALPHA: float = 0.7
    
    # Document Processing
    DOCUMENTS_PATH: str = "./documents"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Security Settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    CONTENT_MODERATION_ENABLED: bool = True
    PII_DETECTION_ENABLED: bool = True
    
    # Monitoring
    LOG_LEVEL: str = "INFO"
    ENABLE_TRACING: bool = True
    ENABLE_METRICS: bool = True
    
    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # seconds
    
    # Memory/Conversation Settings
    MAX_CONTEXT_LENGTH: int = 4000
    ENABLE_MEMORY: bool = True
    MAX_HISTORY_LENGTH: int = 10
    SUMMARIZATION_THRESHOLD: int = 20
    
    # Agent Settings
    MAX_AGENT_ITERATIONS: int = 5
    MAX_ACTIONS_PER_SESSION: int = 10
    MAX_ACTIONS_PER_MINUTE: int = 20
    
    # Paths
    DOCUMENT_FOLDER: str = "./documents"
    LOG_FOLDER: str = "./logs"
    DATA_FOLDER: str = "./data"
    AUDIT_LOG_FILE: str = "./logs/audit.log"
    FEEDBACK_STORAGE: str = "./data/feedback"
    
    # Retrieval Settings
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    USE_HYBRID_SEARCH: bool = False
    
    # Performance Settings
    BATCH_SIZE: int = 32
    ENABLE_CACHING: bool = True
    CACHE_TTL_SECONDS: int = 3600
    
    # Application Info
    APP_NAME: str = "RAG System"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings() -> Settings:
    """Get application settings"""
    return settings


settings = Settings()

