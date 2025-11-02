"""Execute agent with streaming support"""
import logging
import json
import asyncio
from typing import AsyncGenerator, Dict, Any

from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.generation.llm_client import LLMClient
from app.agents.rag_agent import RAGTutorAgent
from app.generation.prompt_builder import PromptBuilder
from app.generation.citation_tracker import CitationTracker

logger = logging.getLogger(__name__)


class ContextualAgentExecutor:
    """Execute agent with streaming support"""
    
    def __init__(
        self,
        retrieval_pipeline: RetrievalPipeline,
        llm_client: LLMClient,
        agent: RAGTutorAgent
    ):
        self.retrieval = retrieval_pipeline
        self.llm = llm_client
        self.agent = agent
    
    async def execute_with_streaming(
        self,
        query: str,
        session_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute agent with streaming events"""
        
        # Emit start event
        yield {
            'type': 'agent_start',
            'query': query,
            'session_id': session_id
        }
        
        # Check if tools needed
        needs_tools = await self.agent._analyze_intent(query)
        
        yield {
            'type': 'intent_analysis',
            'needs_tools': needs_tools
        }
        
        if not needs_tools:
            # Simple RAG with streaming
            async for event in self._stream_simple_rag(query):
                yield event
        else:
            # Agent execution with streaming
            async for event in self._stream_agent_execution(query, session_id):
                yield event
        
        yield {'type': 'done'}
    
    async def _stream_simple_rag(
        self,
        query: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream simple RAG query"""
        
        # Retrieve
        yield {'type': 'retrieval_start'}
        
        chunks, _ = await self.retrieval.retrieve(query, top_k=5, rerank=True)
        
        yield {
            'type': 'retrieval_complete',
            'chunks_retrieved': len(chunks)
        }
        
        # Build prompt
        prompt_builder = PromptBuilder()
        prompt = prompt_builder.build_rag_prompt(query, chunks)
        system_prompt = prompt_builder.system_prompt
        
        # Stream generation
        yield {'type': 'generation_start'}
        
        full_response = ""
        async for token in self.llm.generate_stream(prompt, system=system_prompt):
            full_response += token
            yield {
                'type': 'content_delta',
                'delta': token
            }
        
        # Track citations
        citation_tracker = CitationTracker()
        formatted = citation_tracker.format_citations(
            full_response,
            [chunk for chunk, _ in chunks]
        )
        
        yield {
            'type': 'citations',
            'citations': formatted['citations']
        }
    
    async def _stream_agent_execution(
        self,
        query: str,
        session_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream agent execution with tool calls"""
        
        # Retrieve initial context
        yield {'type': 'retrieval_start'}
        
        chunks, _ = await self.retrieval.retrieve(query, top_k=5, rerank=True)
        context = "\n\n".join([chunk.content for chunk, _ in chunks[:3]])
        
        yield {
            'type': 'retrieval_complete',
            'chunks_retrieved': len(chunks)
        }
        
        # Agent loop
        for iteration in range(self.agent.max_iterations):
            yield {
                'type': 'iteration_start',
                'iteration': iteration + 1
            }
            
            # Build prompt
            prompt_builder = PromptBuilder()
            prompt = prompt_builder.build_agent_prompt(
                query,
                self.agent.tools.get_tool_schemas(),
                conversation_context=context
            )
            
            # Get LLM response
            try:
                response = await self.llm.generate_with_tools(
                    prompt,
                    tools=self.agent.tools.get_tool_schemas(),
                    system="You are a helpful agent. Use tools when needed to answer queries accurately."
                )
                
                # Check for tool use (Anthropic)
                if hasattr(response, 'stop_reason') and response.stop_reason == 'tool_use':
                    for content_block in response.content:
                        if hasattr(content_block, 'type') and content_block.type == 'tool_use':
                            tool_name = content_block.name
                            tool_input = content_block.input
                            
                            # Emit tool call event
                            yield {
                                'type': 'tool_call',
                                'tool_name': tool_name,
                                'tool_input': tool_input
                            }
                            
                            # Execute tool
                            try:
                                tool_result = await self.agent.tools.execute_tool(
                                    tool_name,
                                    tool_input
                                )
                                
                                yield {
                                    'type': 'tool_result',
                                    'tool_name': tool_name,
                                    'result': tool_result,
                                    'success': True
                                }
                                
                                context += f"\n\nTool: {tool_name}\nResult: {json.dumps(tool_result)}"
                                
                            except Exception as e:
                                yield {
                                    'type': 'tool_error',
                                    'tool_name': tool_name,
                                    'error': str(e)
                                }
                
                # Check OpenAI format
                elif hasattr(response, 'choices') and response.choices:
                    choice = response.choices[0]
                    if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                        for tool_call in choice.message.tool_calls:
                            tool_name = tool_call.function.name
                            import json as json_lib
                            tool_input = json_lib.loads(tool_call.function.arguments)
                            
                            yield {
                                'type': 'tool_call',
                                'tool_name': tool_name,
                                'tool_input': tool_input
                            }
                            
                            try:
                                tool_result = await self.agent.tools.execute_tool(tool_name, tool_input)
                                
                                yield {
                                    'type': 'tool_result',
                                    'tool_name': tool_name,
                                    'result': tool_result,
                                    'success': True
                                }
                                
                                context += f"\n\nTool: {tool_name}\nResult: {json.dumps(tool_result)}"
                                
                            except Exception as e:
                                yield {
                                    'type': 'tool_error',
                                    'tool_name': tool_name,
                                    'error': str(e)
                                }
                    else:
                        # Final answer from OpenAI
                        yield {'type': 'generation_start'}
                        answer = choice.message.content
                        
                        # Stream the answer
                        for i in range(0, len(answer), 10):
                            yield {
                                'type': 'content_delta',
                                'delta': answer[i:i+10]
                            }
                            await asyncio.sleep(0.01)  # Simulate streaming
                        break
                
                else:
                    # Final answer
                    yield {'type': 'generation_start'}
                    
                    if hasattr(response, 'content') and response.content:
                        if isinstance(response.content, list):
                            answer = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
                        else:
                            answer = str(response.content)
                    else:
                        answer = str(response)
                    
                    # Stream the answer
                    for i in range(0, len(answer), 10):
                        yield {
                            'type': 'content_delta',
                            'delta': answer[i:i+10]
                        }
                        await asyncio.sleep(0.01)  # Simulate streaming
                    
                    break
                    
            except Exception as e:
                logger.error(f"Agent execution error: {e}")
                yield {
                    'type': 'error',
                    'error': str(e)
                }
                break
