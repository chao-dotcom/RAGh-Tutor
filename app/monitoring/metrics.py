"""Collect and expose Prometheus metrics"""
from typing import Dict, Any
import time
from collections import defaultdict

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Fallback classes
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def inc(self): pass
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def observe(self, value): pass
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, value): pass
    def generate_latest(): return b''
    Counter._value = type('obj', (object,), {'get': lambda: 0.0})()
    Histogram._value = Counter._value
    Gauge._value = Counter._value


class MetricsCollector:
    """Collect and expose Prometheus metrics"""
    
    def __init__(self):
        # Fallback metrics if Prometheus not available
        self._counters = defaultdict(int)
        self._timers = defaultdict(list)
        self._gauges = {}
        
        if PROMETHEUS_AVAILABLE:
            # Counters
            self.queries_total = Counter(
                'rag_queries_total',
                'Total number of queries processed',
                ['status']
            )
            
            self.tool_calls_total = Counter(
                'rag_tool_calls_total',
                'Total number of tool calls',
                ['tool_name', 'status']
            )
            
            self.errors_total = Counter(
                'rag_errors_total',
                'Total number of errors',
                ['error_type']
            )
            
            # Histograms
            self.query_latency = Histogram(
                'rag_query_latency_seconds',
                'Query processing latency',
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            )
            
            self.retrieval_latency = Histogram(
                'rag_retrieval_latency_seconds',
                'Retrieval latency',
                buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
            )
            
            self.generation_latency = Histogram(
                'rag_generation_latency_seconds',
                'Generation latency',
                buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
            )
            
            # Gauges
            self.active_sessions = Gauge(
                'rag_active_sessions',
                'Number of active sessions'
            )
            
            self.vector_store_size = Gauge(
                'rag_vector_store_size',
                'Number of chunks in vector store'
            )
            
            self.cache_size = Gauge(
                'rag_cache_size',
                'Number of entries in cache'
            )
        else:
            # Fallback to simple metrics
            self.queries_total = type('obj', (object,), {
                'labels': lambda self, **kwargs: self,
                'inc': lambda self: None,
                '_value': type('obj', (object,), {'get': lambda: 0.0})()
            })()
            self.errors_total = self.queries_total
            self.active_sessions = type('obj', (object,), {
                'set': lambda self, value: None,
                '_value': type('obj', (object,), {'get': lambda: 0.0})()
            })()
            self.vector_store_size = self.active_sessions
            self.query_latency = type('obj', (object,), {'observe': lambda self, value: None})()
            self.retrieval_latency = self.query_latency
            self.generation_latency = self.query_latency
            self.tool_calls_total = self.queries_total
    
    def record_query(self, status: str, latency: float):
        """Record query metrics"""
        self.queries_total.labels(status=status).inc()
        self.query_latency.observe(latency)
        self._counters['queries'] += 1
        if 'query_latency' not in self._timers:
            self._timers['query_latency'] = []
        self._timers['query_latency'].append(latency)
    
    def record_tool_call(self, tool_name: str, status: str):
        """Record tool call metrics"""
        self.tool_calls_total.labels(tool_name=tool_name, status=status).inc()
    
    def record_error(self, error_type: str):
        """Record error metrics"""
        self.errors_total.labels(error_type=error_type).inc()
        self._counters['errors'] += 1
    
    def record_retrieval(self, latency: float):
        """Record retrieval metrics"""
        self.retrieval_latency.observe(latency)
    
    def record_generation(self, latency: float):
        """Record generation metrics"""
        self.generation_latency.observe(latency)
    
    def update_vector_store_size(self, size: int):
        """Update vector store size"""
        self.vector_store_size.set(size)
    
    def export_metrics(self) -> bytes:
        """Export metrics in Prometheus format"""
        if PROMETHEUS_AVAILABLE:
            return generate_latest()
        return b'# Prometheus not available\n'
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as dictionary"""
        total_queries = self._counters.get('queries', 0)
        total_errors = self._counters.get('errors', 0)
        
        avg_latency = 0.0
        if 'query_latency' in self._timers and self._timers['query_latency']:
            avg_latency = sum(self._timers['query_latency']) / len(self._timers['query_latency'])
        
        error_rate = (total_errors / total_queries) if total_queries > 0 else 0.0
        cache_hits = self._counters.get('cache_hits', 0)
        cache_hit_rate = (cache_hits / total_queries) if total_queries > 0 else 0.0
        
        try:
            queries_total = self._get_counter_value(self.queries_total)
            errors_total = self._get_counter_value(self.errors_total)
            active_sessions = self.active_sessions._value.get() if hasattr(self.active_sessions, '_value') else 0
            vector_store_size = self.vector_store_size._value.get() if hasattr(self.vector_store_size, '_value') else 0
        except:
            queries_total = total_queries
            errors_total = total_errors
            active_sessions = 0
            vector_store_size = 0
        
        return {
            'total_queries': queries_total or total_queries,
            'average_latency': avg_latency,
            'error_rate': error_rate,
            'cache_hit_rate': cache_hit_rate,
            'errors_total': errors_total or total_errors,
            'active_sessions': active_sessions,
            'vector_store_size': vector_store_size
        }
    
    def _get_counter_value(self, counter) -> float:
        """Get counter value"""
        try:
            return counter._value.get()
        except:
            return 0.0
    
    # Backward compatibility methods
    def increment(self, metric: str, value: int = 1):
        """Increment counter"""
        self._counters[metric] += value
    
    def record_time(self, metric: str, duration: float):
        """Record timing metric"""
        self._timers[metric].append(duration)
    
    def set_gauge(self, metric: str, value: float):
        """Set gauge value"""
        self._gauges[metric] = value
    
    def get_metrics(self) -> Dict:
        """Get all metrics (backward compatibility)"""
        return {
            'counters': dict(self._counters),
            'timers': {k: {'avg': sum(v)/len(v), 'count': len(v)} for k, v in self._timers.items() if v},
            'gauges': self._gauges
        }

