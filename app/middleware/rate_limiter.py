"""Rate limiting middleware"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict, deque
from typing import Dict, Deque
import asyncio
import logging

logger = logging.getLogger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # seconds
        self.requests: Dict[str, Deque] = defaultdict(deque)
        self.cleanup_task = None
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP or user ID)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self._check_rate_limit(client_id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Process request
        response = await call_next(request)
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier"""
        # Try to get from headers first (for authenticated users)
        user_id = request.headers.get('X-User-ID')
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"
        
        return f"ip:{request.client.host if request.client else 'unknown'}"
    
    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limit"""
        now = time.time()
        window_start = now - self.window_size
        
        # Get request timestamps for this client
        timestamps = self.requests[client_id]
        
        # Remove old timestamps
        while timestamps and timestamps[0] < window_start:
            timestamps.popleft()
        
        # Check if under limit
        if len(timestamps) >= self.requests_per_minute:
            return False
        
        # Add current request
        timestamps.append(now)
        return True
    
    async def cleanup_old_entries(self):
        """Periodically cleanup old entries"""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            now = time.time()
            
            # Remove clients with no recent requests
            clients_to_remove = []
            for client_id, timestamps in self.requests.items():
                if not timestamps or timestamps[-1] < now - 3600:  # 1 hour
                    clients_to_remove.append(client_id)
            
            for client_id in clients_to_remove:
                del self.requests[client_id]

