"""Rate limiting middleware"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.security.rate_limiter import RateLimiter
import logging

logger = logging.getLogger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for FastAPI"""
    
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.rate_limiter = RateLimiter(requests=requests_per_minute, window=60)
    
    @classmethod
    def create(cls, requests_per_minute: int = 120):
        """Factory method to create middleware with parameters"""
        def middleware_factory(app):
            return cls(app, requests_per_minute)
        return middleware_factory
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier
        client_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not self.rate_limiter.is_allowed(client_id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Process request
        response = await call_next(request)
        return response

