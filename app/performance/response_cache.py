"""Cache RAG responses with smart invalidation"""
from typing import Optional, Dict, Any
import hashlib
import json
from datetime import datetime, timedelta


class ResponseCache:
    """Cache RAG responses with smart invalidation"""
    
    def __init__(
        self,
        default_ttl_minutes: int = 60,
        max_cache_size: int = 1000
    ):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
        self.max_size = max_cache_size
        self.access_times: Dict[str, datetime] = {}
    
    def _generate_cache_key(self, query: str, **params) -> str:
        """Generate cache key from query and parameters"""
        cache_data = {
            'query': query.lower().strip(),
            **params
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get(
        self,
        query: str,
        **params
    ) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        cache_key = self._generate_cache_key(query, **params)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            # Check if expired
            if datetime.utcnow() < entry['expires_at']:
                # Update access time
                self.access_times[cache_key] = datetime.utcnow()
                return entry['response']
            else:
                # Remove expired entry
                del self.cache[cache_key]
                del self.access_times[cache_key]
        
        return None
    
    def set(
        self,
        query: str,
        response: Dict[str, Any],
        ttl: Optional[timedelta] = None,
        **params
    ):
        """Cache response"""
        # Check cache size
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        cache_key = self._generate_cache_key(query, **params)
        ttl = ttl or self.default_ttl
        
        self.cache[cache_key] = {
            'response': response,
            'cached_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + ttl,
            'query': query  # Store for pattern matching
        }
        self.access_times[cache_key] = datetime.utcnow()
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.access_times:
            return
        
        # Find least recently accessed
        lru_key = min(self.access_times, key=self.access_times.get)
        
        # Remove from cache
        del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        keys_to_remove = []
        
        for cache_key, entry in self.cache.items():
            # Check if query contains pattern
            if pattern.lower() in entry.get('query', '').lower():
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del self.cache[key]
            del self.access_times[key]
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.utcnow()
        expired_count = sum(
            1 for entry in self.cache.values()
            if now >= entry.get('expires_at', datetime.max)
        )
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'expired_entries': expired_count,
            'utilization': len(self.cache) / self.max_size if self.max_size > 0 else 0
        }

