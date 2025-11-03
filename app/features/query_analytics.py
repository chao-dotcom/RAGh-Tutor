"""Analyze query patterns and performance"""
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
from pathlib import Path


class QueryAnalytics:
    """Analyze query patterns and performance"""
    
    def __init__(self, storage_path: str = "./data/analytics"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.queries_file = self.storage_path / "queries.jsonl"
    
    async def log_query(
        self,
        query: str,
        session_id: str,
        latency: float,
        chunks_retrieved: int,
        success: bool,
        metadata: Dict = None
    ):
        """Log query for analytics"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'query': query,
            'session_id': session_id,
            'latency': latency,
            'chunks_retrieved': chunks_retrieved,
            'success': success,
            'metadata': metadata or {}
        }
        
        with open(self.queries_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_popular_queries(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently asked queries"""
        if not self.queries_file.exists():
            return []
        
        query_counts = Counter()
        
        with open(self.queries_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    # Normalize query for counting
                    normalized = entry['query'].lower().strip()
                    query_counts[normalized] += 1
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return query_counts.most_common(limit)
    
    def get_slow_queries(self, threshold: float = 5.0) -> List[Dict]:
        """Get queries that took longer than threshold"""
        if not self.queries_file.exists():
            return []
        
        slow_queries = []
        
        with open(self.queries_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry['latency'] > threshold:
                        slow_queries.append(entry)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return slow_queries
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics"""
        if not self.queries_file.exists():
            return {}
        
        latencies = []
        success_count = 0
        total_count = 0
        
        with open(self.queries_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    latencies.append(entry['latency'])
                    if entry['success']:
                        success_count += 1
                    total_count += 1
                except (json.JSONDecodeError, KeyError):
                    continue
        
        if not latencies:
            return {}
        
        sorted_latencies = sorted(latencies)
        
        return {
            'total_queries': total_count,
            'success_rate': success_count / total_count if total_count > 0 else 0,
            'average_latency': sum(latencies) / len(latencies),
            'median_latency': sorted_latencies[len(sorted_latencies) // 2],
            'p95_latency': sorted_latencies[int(len(sorted_latencies) * 0.95)] if sorted_latencies else 0,
            'p99_latency': sorted_latencies[int(len(sorted_latencies) * 0.99)] if sorted_latencies else 0
        }
    
    def get_usage_over_time(self, days: int = 7) -> Dict[str, int]:
        """Get query volume over time"""
        if not self.queries_file.exists():
            return {}
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        daily_counts = defaultdict(int)
        
        with open(self.queries_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    timestamp = datetime.fromisoformat(entry['timestamp'])
                    
                    if timestamp > cutoff:
                        date = timestamp.date().isoformat()
                        daily_counts[date] += 1
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        
        return dict(sorted(daily_counts.items()))
    
    def detect_query_patterns(self) -> Dict[str, Any]:
        """Detect patterns in queries"""
        if not self.queries_file.exists():
            return {}
        
        # Analyze query characteristics
        query_lengths = []
        question_words = Counter()
        topics = Counter()
        
        with open(self.queries_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    query = entry['query'].lower()
                    
                    # Length
                    query_lengths.append(len(query.split()))
                    
                    # Question words
                    for word in ['what', 'how', 'why', 'when', 'where', 'who']:
                        if word in query:
                            question_words[word] += 1
                    
                    # Simple topic extraction (first noun-like word)
                    words = query.split()
                    if len(words) > 1:
                        topics[words[1]] += 1
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return {
            'avg_query_length': sum(query_lengths) / len(query_lengths) if query_lengths else 0,
            'common_question_words': dict(question_words.most_common(5)),
            'common_topics': dict(topics.most_common(10))
        }

