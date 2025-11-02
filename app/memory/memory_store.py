"""Persistent memory store"""
import logging
import json
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class MemoryStore:
    """Persistent storage for conversations"""
    
    def __init__(self, storage_path: str = "./data/memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_conversation(self, conversation_id: str, data: Dict):
        """Save conversation to disk"""
        file_path = self.storage_path / f"{conversation_id}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Load conversation from disk"""
        file_path = self.storage_path / f"{conversation_id}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def delete_conversation(self, conversation_id: str):
        """Delete conversation from disk"""
        file_path = self.storage_path / f"{conversation_id}.json"
        if file_path.exists():
            file_path.unlink()

