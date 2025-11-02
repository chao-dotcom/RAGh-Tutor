"""Tracing utilities"""
import time
from functools import wraps

def trace_function(func):
    """Decorator to trace function execution"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start
            print(f"{func.__name__} executed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start
            print(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    return wrapper

