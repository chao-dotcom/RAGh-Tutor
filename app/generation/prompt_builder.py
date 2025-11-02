"""Prompt builder for RAG"""
from typing import List, Tuple, Optional, Dict

from app.schemas.documents import Chunk


class PromptBuilder:
    """Build prompts for RAG queries"""
    
    def __init__(self):
        self.system_prompt = self._default_system_prompt()
    
    def _default_system_prompt(self) -> str:
        return """You are a helpful AI assistant with access to a knowledge base. 
Your task is to answer questions based on the provided context.

Guidelines:
- Always cite your sources using the chunk IDs provided
- If the context doesn't contain enough information, say so
- Be concise but thorough
- If you're uncertain, acknowledge it
- Format citations as [chunk_id]"""
    
    def build_rag_prompt(
        self,
        query: str,
        chunks: List[Tuple[Chunk, float]],
        conversation_history: Optional[List[dict]] = None,
        include_scores: bool = False
    ) -> str:
        """Build complete RAG prompt"""
        
        prompt_parts = []
        
        # Add conversation history if available
        if conversation_history:
            prompt_parts.append("## Conversation History")
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg['role'].capitalize()
                content = msg['content']
                prompt_parts.append(f"{role}: {content}")
            prompt_parts.append("")
        
        # Add context
        prompt_parts.append("## Context")
        for i, (chunk, score) in enumerate(chunks, 1):
            chunk_text = f"[{chunk.chunk_id}]\n{chunk.content}"
            if include_scores:
                chunk_text += f"\n(Relevance: {score:.3f})"
            prompt_parts.append(chunk_text)
            prompt_parts.append("")
        
        # Add query
        prompt_parts.append("## Question")
        prompt_parts.append(query)
        prompt_parts.append("")
        prompt_parts.append("## Answer")
        prompt_parts.append("Based on the context above, here is my answer:")
        
        return "\n".join(prompt_parts)
    
    def build_multi_document_prompt(
        self,
        query: str,
        document_groups: Dict[str, List[Tuple[Chunk, float]]]
    ) -> str:
        """Build prompt for multi-document reasoning"""
        
        prompt_parts = [
            "You need to synthesize information from multiple documents to answer this question.",
            "",
            "## Documents"
        ]
        
        for doc_id, chunks in document_groups.items():
            prompt_parts.append(f"\n### Document: {doc_id}")
            for chunk, score in chunks:
                prompt_parts.append(f"[{chunk.chunk_id}]\n{chunk.content}\n")
        
        prompt_parts.extend([
            "",
            "## Question",
            query,
            "",
            "## Instructions",
            "Synthesize information from all documents above to provide a comprehensive answer.",
            "Note any contradictions or differences between documents.",
            "Cite specific documents when making claims.",
            "",
            "## Answer"
        ])
        
        return "\n".join(prompt_parts)
    
    def build_agent_prompt(
        self,
        query: str,
        available_tools: List[dict],
        conversation_context: Optional[str] = None
    ) -> str:
        """Build prompt for agent with tool use"""
        
        tool_descriptions = []
        for tool in available_tools:
            tool_desc = f"- {tool['name']}: {tool['description']}"
            tool_descriptions.append(tool_desc)
        
        prompt_parts = [
            "You are an AI agent with access to tools. Analyze the query and determine if you need to use any tools.",
            "",
            "## Available Tools"
        ]
        prompt_parts.extend(tool_descriptions)
        
        if conversation_context:
            prompt_parts.extend([
                "",
                "## Context",
                conversation_context
            ])
        
        prompt_parts.extend([
            "",
            "## Query",
            query,
            "",
            "## Instructions",
            "1. Analyze if the query can be answered with available knowledge",
            "2. If tools are needed, decide which tool(s) to use",
            "3. Plan your approach step by step",
            "4. Execute the plan and provide a comprehensive answer"
        ])
        
        return "\n".join(prompt_parts)
    
    def build_chat_prompt(
        self,
        message: str,
        chunks: List[Chunk],
        conversation_history: Optional[List[dict]] = None
    ) -> str:
        """Build chat prompt with context and history (backward compatibility)"""
        
        chunks_with_scores = [(chunk, 1.0) for chunk in chunks]
        return self.build_rag_prompt(message, chunks_with_scores, conversation_history)
