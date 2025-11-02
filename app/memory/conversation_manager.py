"""Conversation manager for maintaining context"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict
import uuid
import json

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manage conversation history and context"""
    
    def __init__(
        self,
        max_history: int = 10,
        max_history_length: int = 10,
        summarization_threshold: int = 20
    ):
        self.max_history = max_history
        self.max_history_length = max_history_length or max_history
        self.summarization_threshold = summarization_threshold
        self.conversations: Dict[str, List[Dict]] = defaultdict(list)
        self.summaries: Dict[str, str] = {}
    
    def create_conversation(self) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = []
        return conversation_id
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Add a message to conversation"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        
        self.conversations[conversation_id].append(message)
        
        # Check if summarization needed
        if len(self.conversations[conversation_id]) > self.summarization_threshold:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self._summarize_conversation(conversation_id))
                else:
                    asyncio.run(self._summarize_conversation(conversation_id))
            except RuntimeError:
                # If no event loop, just trim
                if len(self.conversations[conversation_id]) > self.max_history_length * 2:
                    self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_history_length:]
    
    def get_history(self, conversation_id: str) -> List[Dict]:
        """Get conversation history"""
        return self.conversations.get(conversation_id, [])
    
    def get_formatted_history(self, conversation_id: str) -> List[Dict]:
        """Get formatted history for prompts"""
        history = self.get_history(conversation_id)
        formatted = []
        
        for msg in history[-self.max_history:]:
            formatted.append({
                'user' if msg['role'] == 'user' else 'assistant': msg['content']
            })
        
        return formatted
    
    def get_context(
        self,
        session_id: str,
        max_tokens: int = 2000
    ) -> List[Dict]:
        """Get conversation context within token limit"""
        if session_id not in self.conversations:
            return []
        
        messages = self.conversations[session_id]
        
        # Start with most recent messages
        context = []
        total_tokens = 0
        
        for message in reversed(messages):
            # Estimate tokens (rough approximation)
            message_tokens = len(message['content'].split()) * 1.3
            
            if total_tokens + message_tokens > max_tokens:
                break
            
            context.insert(0, message)
            total_tokens += message_tokens
        
        # Add summary if available and space permits
        if session_id in self.summaries:
            summary_tokens = len(self.summaries[session_id].split()) * 1.3
            if total_tokens + summary_tokens < max_tokens:
                context.insert(0, {
                    'role': 'system',
                    'content': f"Previous conversation summary: {self.summaries[session_id]}",
                    'timestamp': None
                })
        
        return context
    
    def get_full_history(self, session_id: str) -> List[Dict]:
        """Get full conversation history"""
        return self.get_history(session_id)
    
    def clear_history(self, session_id: str):
        """Clear conversation history (alias for clear_conversation)"""
        self.clear_conversation(session_id)
    
    def clear_conversation(self, conversation_id: str):
        """Clear a conversation"""
        self.conversations.pop(conversation_id, None)
        self.summaries.pop(conversation_id, None)
    
    async def _summarize_conversation(self, session_id: str):
        """Summarize old conversation history"""
        # Get messages to summarize (keep recent messages)
        messages = self.conversations[session_id]
        to_summarize = messages[:-self.max_history_length]
        
        if not to_summarize:
            return
        
        # Build summary prompt
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in to_summarize
        ])
        
        # TODO: Use LLM to generate summary
        # For now, create simple summary
        summary = f"Conversation covered {len(to_summarize)} messages."
        
        # Store summary and trim history
        self.summaries[session_id] = summary
        self.conversations[session_id] = messages[-self.max_history_length:]
    
    def export_conversation(self, session_id: str, filepath: str):
        """Export conversation to file"""
        data = {
            'session_id': session_id,
            'messages': self.conversations.get(session_id, []),
            'summary': self.summaries.get(session_id),
            'exported_at': datetime.utcnow().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

