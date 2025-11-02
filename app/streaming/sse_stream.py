"""Server-Sent Events streaming"""
from typing import AsyncGenerator, Dict, Any
import json
import asyncio


class SSEStream:
    """Server-Sent Events stream handler"""
    
    def __init__(self):
        self.event_id = 0
    
    def _format_event(
        self,
        data: Dict[str, Any],
        event_type: str = "message"
    ) -> str:
        """Format data as SSE event"""
        self.event_id += 1
        
        lines = []
        lines.append(f"id: {self.event_id}")
        lines.append(f"event: {event_type}")
        lines.append(f"data: {json.dumps(data)}")
        lines.append("")  # Empty line marks end of event
        
        return "\n".join(lines) + "\n"
    
    async def generate_events(
        self,
        query: str,
        agent_executor,
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """Generate SSE events for agent execution"""
        
        try:
            async for event in agent_executor.execute_with_streaming(
                query,
                session_id
            ):
                yield self._format_event(event, event_type=event.get('type', 'message'))
        
        except Exception as e:
            error_event = {
                'type': 'error',
                'error': str(e),
                'error_type': type(e).__name__
            }
            yield self._format_event(error_event, event_type='error')


async def sse_stream_response(stream: AsyncGenerator[str, None]):
    """Create SSE stream response (backward compatibility)"""
    async def generate():
        async for chunk in stream:
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

