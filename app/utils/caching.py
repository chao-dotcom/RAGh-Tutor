"""Caching utilities"""
import hashlib
import json
import time
from typing import Optional, Any


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


class SimpleCache:
    """Simple in-memory cache"""
    
    def __init__(self, ttl: int = 3600):
        self.cache: dict = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get from cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set cache value"""
        self.cache[key] = (value, time.time())
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()

