"""Audit logging for compliance and debugging"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit logging for compliance and debugging"""
    
    def __init__(self, log_file: str = "logs/audit.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an audit event"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            **data
        }
        self.logger.info(json.dumps(event))
    
    def log_query(
        self,
        session_id: str,
        user_id: Optional[str],
        query: str,
        retrieved_chunks: List[str],
        response: str,
        latency: float
    ):
        """Log a query execution"""
        self._log_event('query', {
            'session_id': session_id,
            'user_id': user_id,
            'query': query[:200],  # Truncate for privacy
            'chunks_retrieved': len(retrieved_chunks),
            'response_length': len(response),
            'latency_ms': latency * 1000
        })
    
    def log_tool_call(
        self,
        session_id: str,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Any,
        success: bool,
        latency: float = 0
    ):
        """Log a tool execution"""
        self._log_event('tool_call', {
            'session_id': session_id,
            'tool_name': tool_name,
            'tool_input': str(tool_input)[:200],
            'success': success,
            'latency_ms': latency * 1000
        })
    
    def log_error(
        self,
        session_id: str,
        error_type: str,
        error_message: str,
        query: Optional[str] = None,
        stack_trace: Optional[str] = None
    ):
        """Log an error"""
        self._log_event('error', {
            'session_id': session_id,
            'error_type': error_type,
            'error_message': error_message,
            'query': query[:200] if query else None,
            'stack_trace': stack_trace[:500] if stack_trace else None
        })
    
    def log_security_event(
        self,
        event_type: str,
        session_id: str,
        details: Dict[str, Any]
    ):
        """Log security-related events"""
        self._log_event('security', {
            'security_event_type': event_type,
            'session_id': session_id,
            **details
        })
    
    def log_document_upload(
        self,
        user_id: Optional[str],
        filename: str,
        file_size: int,
        chunks_created: int
    ):
        """Log document upload"""
        self._log_event('document_upload', {
            'user_id': user_id,
            'filename': filename,
            'file_size': file_size,
            'chunks_created': chunks_created
        })
    
    # Backward compatibility
    def log_event(self, event_type: str, details: Dict, user_id: Optional[str] = None):
        """Log an audit event (backward compatibility)"""
        self._log_event(event_type, {**details, 'user_id': user_id})

