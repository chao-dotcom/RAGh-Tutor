"""Rate limiting"""
import time
import logging
from typing import Dict
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests: int = 100, window: int = 60):
        self.requests = requests
        self.window = window
        self.clients: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Clean old requests
        self.clients[client_id] = [
            req_time for req_time in self.clients[client_id]
            if now - req_time < self.window
        ]
        
        # Check limit
        if len(self.clients[client_id]) >= self.requests:
            return False
        
        # Record request
        self.clients[client_id].append(now)
        return True
    
    def reset(self, client_id: str = None):
        """Reset rate limit for client"""
        if client_id:
            self.clients[client_id].clear()
        else:
            self.clients.clear()

