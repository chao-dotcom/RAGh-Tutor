"""Prevent infinite tool loops"""
import time
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ActionBudgetGuard:
    """Prevent infinite tool loops"""
    
    def __init__(
        self,
        max_actions_per_session: int = 10,
        max_actions_per_minute: int = 20,
        reset_after_seconds: int = 3600
    ):
        self.max_actions_per_session = max_actions_per_session
        self.max_actions_per_minute = max_actions_per_minute
        self.reset_after_seconds = reset_after_seconds
        
        self.session_counts: Dict[str, int] = {}
        self.session_timestamps: Dict[str, float] = {}
        self.minute_windows: Dict[str, list] = {}
    
    def check_budget(self, session_id: str) -> bool:
        """Check if session has budget remaining"""
        now = time.time()
        
        # Reset if expired
        if session_id in self.session_timestamps:
            if now - self.session_timestamps[session_id] > self.reset_after_seconds:
                self.reset(session_id)
        
        # Check session limit
        session_count = self.session_counts.get(session_id, 0)
        if session_count >= self.max_actions_per_session:
            return False
        
        # Check per-minute limit
        if not self._check_minute_limit(session_id, now):
            return False
        
        return True
    
    def _check_minute_limit(self, session_id: str, now: float) -> bool:
        """Check per-minute action limit"""
        if session_id not in self.minute_windows:
            self.minute_windows[session_id] = []
        
        window = self.minute_windows[session_id]
        
        # Remove timestamps older than 1 minute
        window[:] = [ts for ts in window if now - ts < 60]
        
        # Check if under limit
        return len(window) < self.max_actions_per_minute
    
    def increment(self, session_id: str):
        """Increment action count"""
        now = time.time()
        
        self.session_counts[session_id] = self.session_counts.get(session_id, 0) + 1
        self.session_timestamps[session_id] = now
        
        if session_id not in self.minute_windows:
            self.minute_windows[session_id] = []
        self.minute_windows[session_id].append(now)
    
    def reset(self, session_id: str):
        """Reset counters for session"""
        self.session_counts.pop(session_id, None)
        self.session_timestamps.pop(session_id, None)
        self.minute_windows.pop(session_id, None)
    
    def get_remaining(self, session_id: str) -> int:
        """Get remaining actions for session"""
        used = self.session_counts.get(session_id, 0)
        return max(0, self.max_actions_per_session - used)


# Backward compatibility alias
ActionBudget = ActionBudgetGuard

