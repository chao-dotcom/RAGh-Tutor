"""RAG agent orchestrator"""
import logging
from typing import List, Optional, Dict, Any
import json

from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.generation.llm_client import LLMClient
from app.generation.prompt_builder import PromptBuilder
from app.generation.response_parser import ResponseParser
from app.generation.citation_tracker import CitationTracker
from app.agents.tool_registry import ToolRegistry
from app.schemas.documents import Chunk

logger = logging.getLogger(__name__)


class RAGAgent:
    """Main RAG agent that orchestrates retrieval and generation"""
    
    def __init__(
        self,
        retrieval_pipeline: RetrievalPipeline,
        llm_client: LLMClient,
        use_citations: bool = True
    ):
        self.retrieval_pipeline = retrieval_pipeline
        self.llm_client = llm_client
        self.prompt_builder = PromptBuilder()
        self.response_parser = ResponseParser()
        self.citation_tracker = CitationTracker()
        self.use_citations = use_citations
    
    async def query(
        self,
        query: str,
        top_k: int = 10,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """Process a query through RAG pipeline"""
        
        # Retrieve relevant chunks
        chunks_with_scores, retrieval_time = await self.retrieval_pipeline.retrieve(
            query,
            top_k=top_k
        )
        
        chunks = [chunk for chunk, _ in chunks_with_scores]
        
        # Track citations
        if self.use_citations:
            self.citation_tracker.add_citations(chunks)
        
        # Build prompt
        prompt = self.prompt_builder.build_rag_prompt(
            query,
            chunks_with_scores,
            conversation_history=conversation_history
        )
        
        # Generate response
        system_prompt = self.prompt_builder.system_prompt
        response = await self.llm_client.generate(prompt, system=system_prompt)
        
        # Parse response
        parsed = self.response_parser.parse_structured_response(response)
        
        return {
            'response': parsed['answer'],
            'sources': chunks,
            'citations': parsed['citations'] if self.use_citations else [],
            'retrieval_time': retrieval_time,
            'raw_response': response
        }
    
    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None,
        top_k: int = 10
    ) -> Dict:
        """Chat with conversation context"""
        
        # Retrieve
        chunks_with_scores, retrieval_time = await self.retrieval_pipeline.retrieve(
            message,
            top_k=top_k
        )
        
        chunks = [chunk for chunk, _ in chunks_with_scores]
        
        # Build chat prompt
        prompt = self.prompt_builder.build_chat_prompt(
            message,
            chunks,
            conversation_history
        )
        
        # Generate
        response = await self.llm_client.generate(prompt)
        
        return {
            'response': response,
            'sources': chunks,
            'retrieval_time': retrieval_time
        }


class RAGTutorAgent:
    """Agent that combines RAG with tool use"""
    
    def __init__(
        self,
        llm_client: LLMClient,
        retrieval_pipeline: RetrievalPipeline,
        tool_registry: ToolRegistry
    ):
        self.llm = llm_client
        self.retrieval = retrieval_pipeline
        self.tools = tool_registry
        self.max_iterations = 5
    
    async def execute(
        self,
        query: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Execute agent with query"""
        
        # First, check if we need tools
        needs_tools = await self._analyze_intent(query)
        
        if not needs_tools:
            # Simple RAG query
            return await self._simple_rag_query(query)
        
        # Agent loop with tools
        return await self._agentic_execution(query, session_id)
    
    async def _analyze_intent(self, query: str) -> bool:
        """Determine if query needs tools"""
        prompt = f"""Analyze this query and determine if it requires:
- Real-time web browsing
- External data fetching
- Interactive actions

Query: {query}

Answer with just YES or NO."""
        
        response = await self.llm.generate(prompt, max_tokens=10)
        return 'yes' in response.lower()
    
    async def _simple_rag_query(self, query: str) -> Dict[str, Any]:
        """Handle simple RAG query without tools"""
        from app.generation.prompt_builder import PromptBuilder
        from app.generation.citation_tracker import CitationTracker
        
        # Retrieve chunks
        chunks, _ = await self.retrieval.retrieve(query, top_k=5, rerank=True)
        
        # Build prompt
        prompt_builder = PromptBuilder()
        prompt = prompt_builder.build_rag_prompt(query, chunks)
        
        # Generate response
        response = await self.llm.generate(prompt)
        
        # Track citations
        citation_tracker = CitationTracker()
        formatted = citation_tracker.format_citations(
            response,
            [chunk for chunk, _ in chunks]
        )
        
        return {
            'answer': formatted['text'],
            'citations': formatted['citations'],
            'chunks_used': len(chunks),
            'tools_used': []
        }
    
    async def _agentic_execution(
        self,
        query: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Execute agent loop with tools"""
        import json
        
        tools_used = []
        final_answer = None
        
        # Initial retrieval
        chunks, _ = await self.retrieval.retrieve(query, top_k=5, rerank=True)
        context = "\n\n".join([chunk.content for chunk, _ in chunks[:3]])
        
        for iteration in range(self.max_iterations):
            # Build agent prompt
            prompt_builder = PromptBuilder()
            prompt = prompt_builder.build_agent_prompt(
                query,
                self.tools.get_tool_schemas(),
                conversation_context=context
            )
            
            # Get LLM response with tools
            response = await self.llm.generate_with_tools(
                prompt,
                tools=self.tools.get_tool_schemas(),
                system="You are a helpful agent. Use tools when needed to answer queries accurately."
            )
            
            # Check if LLM wants to use tools (Anthropic format)
            if hasattr(response, 'stop_reason') and response.stop_reason == 'tool_use':
                # Extract tool calls
                for content_block in response.content:
                    if hasattr(content_block, 'type') and content_block.type == 'tool_use':
                        tool_name = content_block.name
                        tool_input = content_block.input
                        
                        # Execute tool
                        try:
                            tool_result = await self.tools.execute_tool(
                                tool_name,
                                tool_input
                            )
                            
                            tools_used.append({
                                'name': tool_name,
                                'input': tool_input,
                                'result': tool_result,
                                'success': True
                            })
                            
                            # Add to context
                            context += f"\n\nTool: {tool_name}\nResult: {json.dumps(tool_result)}"
                            
                        except Exception as e:
                            tools_used.append({
                                'name': tool_name,
                                'input': tool_input,
                                'error': str(e),
                                'success': False
                            })
            
            # Check OpenAI format (function calling)
            elif hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                    for tool_call in choice.message.tool_calls:
                        tool_name = tool_call.function.name
                        import json as json_lib
                        tool_input = json_lib.loads(tool_call.function.arguments)
                        
                        try:
                            tool_result = await self.tools.execute_tool(tool_name, tool_input)
                            
                            tools_used.append({
                                'name': tool_name,
                                'input': tool_input,
                                'result': tool_result,
                                'success': True
                            })
                            
                            context += f"\n\nTool: {tool_name}\nResult: {json.dumps(tool_result)}"
                            
                        except Exception as e:
                            tools_used.append({
                                'name': tool_name,
                                'input': tool_input,
                                'error': str(e),
                                'success': False
                            })
            
            else:
                # LLM provided final answer
                if hasattr(response, 'content') and response.content:
                    if isinstance(response.content, list):
                        final_answer = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
                    else:
                        final_answer = str(response.content)
                elif hasattr(response, 'choices') and response.choices:
                    final_answer = response.choices[0].message.content
                else:
                    final_answer = str(response)
                break
        
        if not final_answer:
            final_answer = "I couldn't complete the task within the allowed iterations."
        
        return {
            'answer': final_answer,
            'tools_used': tools_used,
            'iterations': iteration + 1,
            'chunks_used': len(chunks)
        }

