"""Collect and analyze user feedback"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class FeedbackCollector:
    """Collect and analyze user feedback"""
    
    def __init__(self, storage_path: str = "./data/feedback"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.storage_path / "feedback.jsonl"
    
    async def record_feedback(
        self,
        query: str,
        response: str,
        rating: int,
        feedback_text: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Record user feedback"""
        feedback_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': session_id,
            'query': query,
            'response': response,
            'rating': rating,
            'feedback_text': feedback_text,
            'metadata': metadata or {}
        }
        
        # Append to file
        with open(self.feedback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_entry) + '\n')
    
    def get_statistics(self) -> Dict:
        """Get feedback statistics"""
        if not self.feedback_file.exists():
            return {
                'total_feedback': 0,
                'average_rating': 0,
                'rating_distribution': {}
            }
        
        ratings = []
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    rating = entry['rating']
                    ratings.append(rating)
                    if rating in rating_counts:
                        rating_counts[rating] += 1
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return {
            'total_feedback': len(ratings),
            'average_rating': sum(ratings) / len(ratings) if ratings else 0,
            'rating_distribution': rating_counts
        }
    
    def get_low_rated_queries(self, threshold: int = 2) -> List[Dict]:
        """Get queries with low ratings for analysis"""
        low_rated = []
        
        if not self.feedback_file.exists():
            return low_rated
        
        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry['rating'] <= threshold:
                        low_rated.append(entry)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return low_rated
    
    async def analyze_feedback_trends(self) -> Dict:
        """Analyze feedback trends over time"""
        if not self.feedback_file.exists():
            return {}
        
        daily_ratings = {}
        
        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    date = entry['timestamp'][:10]  # Get date part
                    
                    if date not in daily_ratings:
                        daily_ratings[date] = []
                    
                    daily_ratings[date].append(entry['rating'])
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # Calculate daily averages
        trends = {}
        for date, ratings in daily_ratings.items():
            trends[date] = {
                'average_rating': sum(ratings) / len(ratings) if ratings else 0,
                'total_feedback': len(ratings)
            }
        
        return trends
