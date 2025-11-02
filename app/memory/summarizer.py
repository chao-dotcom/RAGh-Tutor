"""Summarize conversation history"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class Summarizer:
    """Summarize long conversations"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    async def summarize_conversation(self, messages: List[Dict]) -> str:
        """Summarize a conversation"""
        if not self.llm_client:
            # Simple concatenation fallback
            return " ".join([msg.get('content', '') for msg in messages])
        
        # Build summarization prompt
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])
        
        prompt = f"""Summarize the following conversation:\n\n{conversation_text}\n\nSummary:"""
        
        summary = await self.llm_client.generate(prompt, max_tokens=500)
        return summary
    
    def summarize_chunks(self, chunks: List) -> str:
        """Summarize a list of chunks"""
        # Simple concatenation
        return "\n".join([chunk.content[:200] for chunk in chunks[:5]])

