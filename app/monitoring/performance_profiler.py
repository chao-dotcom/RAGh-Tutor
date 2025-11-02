"""Profile performance of functions"""
import time
import functools
import asyncio
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


class PerformanceProfiler:
    """Profile performance of functions"""
    
    def __init__(self, metrics_collector=None):
        self.metrics_collector = metrics_collector
        self.timings = {}
    
    def profile(self, name: str = None):
        """Decorator to profile function execution"""
        def decorator(func: Callable) -> Callable:
            prof_name = name or func.__name__
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start
                    self._record_timing(prof_name, duration, success=True)
                    return result
                except Exception as e:
                    duration = time.time() - start
                    self._record_timing(prof_name, duration, success=False)
                    raise
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start
                    self._record_timing(prof_name, duration, success=True)
                    return result
                except Exception as e:
                    duration = time.time() - start
                    self._record_timing(prof_name, duration, success=False)
                    raise
            
            # Return appropriate wrapper
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def _record_timing(self, name: str, duration: float, success: bool):
        """Record timing data"""
        if name not in self.timings:
            self.timings[name] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'failures': 0
            }
        
        stats = self.timings[name]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['min_time'] = min(stats['min_time'], duration)
        stats['max_time'] = max(stats['max_time'], duration)
        
        if not success:
            stats['failures'] += 1
        
        # Log slow operations
        if duration > 5.0:
            logger.warning(f"Slow operation: {name} took {duration:.2f}s")
    
    def get_stats(self) -> dict:
        """Get performance statistics"""
        stats = {}
        for name, timing in self.timings.items():
            count = timing['count']
            if count > 0:
                stats[name] = {
                    'calls': count,
                    'total_time': timing['total_time'],
                    'avg_time': timing['total_time'] / count,
                    'min_time': timing['min_time'] if timing['min_time'] != float('inf') else 0,
                    'max_time': timing['max_time'],
                    'failure_rate': timing['failures'] / count if count > 0 else 0
                }
        return stats

