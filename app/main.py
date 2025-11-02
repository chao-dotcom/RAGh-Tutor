"""FastAPI application entry point"""
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, WebSocket
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
import time
from typing import Optional
import uuid
import json

from app.config import settings
from app.schemas.requests import QueryRequest, FeedbackRequest, MultiDocumentQueryRequest
from app.schemas.responses import QueryResponse, HealthResponse
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.security.content_moderation import ContentModerator
from app.monitoring.metrics import MetricsCollector

# Import all components
from app.processing.document_loader import DocumentLoader
from app.chunking.document_chunker import DocumentChunker
from app.embedding.embedding_model import EmbeddingModel
from app.retrieval.vector_store import InMemoryVectorStore
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.retrieval.reranker import Reranker
from app.generation.llm_client import LLMClient
from app.agents.rag_agent import RAGTutorAgent
from app.agents.contextual_agent_executor import ContextualAgentExecutor
from app.agents.tool_registry import ToolRegistry
from app.memory.conversation_manager import ConversationManager
from app.security.audit_logger import AuditLogger
from app.features.feedback_collector import FeedbackCollector
from app.streaming.sse_stream import SSEStream

# Configure logging first
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting application initialization...")
    
    # Initialize embedding model
    logger.info("Loading embedding model...")
    embedding_model = EmbeddingModel(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.EMBEDDING_DEVICE
    )
    
    # Initialize vector store
    logger.info("Initializing vector store...")
    vector_store = InMemoryVectorStore(dimension=settings.EMBEDDING_DIMENSION)
    
    # Try to load existing vector store
    try:
        vector_store.load(settings.VECTOR_STORE_PATH)
        logger.info(f"Loaded existing vector store with {vector_store.size} chunks")
    except Exception as e:
        logger.info(f"No existing vector store found, will create new one: {e}")
    
    # Initialize reranker
    reranker = Reranker()
    
    # Initialize retrieval pipeline
    from app.retrieval.query_expansion import QueryExpander
    query_expander = QueryExpander()
    retrieval_pipeline = RetrievalPipeline(
        vector_store=vector_store,
        embedding_model=embedding_model,
        reranker=reranker,
        query_expander=query_expander,
        use_hybrid=True
    )
    
    # Initialize LLM client
    llm_client = LLMClient(
        provider=settings.LLM_PROVIDER,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS
    )
    
    # Initialize tool registry
    tool_registry = ToolRegistry()
    
    # Register tools
    from app.agents.tools.browser_tool import BrowserTool
    browser_tool = BrowserTool()
    
    tool_registry.register(
        name="web_navigate",
        description="Navigate to a URL and extract page content",
        parameters={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to navigate to"
                }
            },
            "required": ["url"]
        },
        function=browser_tool.navigate
    )
    
    # Initialize agent
    rag_agent = RAGTutorAgent(
        llm_client=llm_client,
        retrieval_pipeline=retrieval_pipeline,
        tool_registry=tool_registry
    )
    
    # Initialize contextual agent executor
    contextual_agent = ContextualAgentExecutor(
        retrieval_pipeline=retrieval_pipeline,
        llm_client=llm_client,
        agent=rag_agent
    )
    
    # Initialize conversation manager
    conversation_manager = ConversationManager(
        max_history=settings.MAX_CONTEXT_LENGTH // 200
    )
    
    # Initialize audit logger
    audit_logger = AuditLogger(log_path="./logs/audit.log")
    
    # Initialize feedback collector
    feedback_collector = FeedbackCollector(storage_path="./data/feedback")
    
    # Initialize content moderator
    content_moderator = ContentModerator()
    
    # Initialize metrics collector
    metrics_collector = MetricsCollector()
    
    # Initialize action budget guard
    from app.security.action_budget import ActionBudgetGuard
    action_budget = ActionBudgetGuard(
        max_actions_per_session=10,
        max_actions_per_minute=20
    )
    
    # Store in app state
    app_state.update({
        'settings': settings,
        'embedding_model': embedding_model,
        'vector_store': vector_store,
        'retrieval_pipeline': retrieval_pipeline,
        'llm_client': llm_client,
        'rag_agent': rag_agent,
        'contextual_agent': contextual_agent,
        'conversation_manager': conversation_manager,
        'audit_logger': audit_logger,
        'feedback_collector': feedback_collector,
        'content_moderator': content_moderator,
        'metrics_collector': metrics_collector,
        'tool_registry': tool_registry,
        'browser_tool': browser_tool,
        'action_budget': action_budget
    })
    
    logger.info("Application initialization complete!")
    
    yield
    
    # Cleanup
    logger.info("Shutting down application...")
    if 'browser_tool' in app_state:
        await app_state['browser_tool'].cleanup()
    logger.info("Cleanup complete")

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description="Production-ready RAG system with agent capabilities",
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.security.rate_limiter import RateLimiter

class RateLimiterWrapper(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = RateLimiter(requests=120, window=60)
    
    async def dispatch(self, request, call_next):
        client_id = request.client.host if request.client else "unknown"
        if not self.rate_limiter.is_allowed(client_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        return await call_next(request)

app.add_middleware(RateLimiterWrapper)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if not app_state:
        raise HTTPException(status_code=503, detail="Not initialized")
    vector_store = app_state['vector_store']
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        documents_indexed=vector_store.size
    )


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    if not app_state:
        raise HTTPException(status_code=503, detail="Not ready")
    return {"status": "ready"}


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """Non-streaming query endpoint"""
    
    # Get components
    retrieval_pipeline = app_state['retrieval_pipeline']
    llm_client = app_state['llm_client']
    conversation_manager = app_state['conversation_manager']
    audit_logger = app_state['audit_logger']
    content_moderator = app_state['content_moderator']
    
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Content moderation (using sync version)
        is_safe, reason = content_moderator.check_content(request.query)
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"Content violation: {reason}")
        
        # Get conversation history
        history = conversation_manager.get_context(session_id, max_tokens=2000)
        
        # Retrieve chunks
        chunks, retrieval_time = await retrieval_pipeline.retrieve(
            request.query,
            top_k=request.top_k or 5,
            rerank=True
        )
        
        # Build prompt
        from app.generation.prompt_builder import PromptBuilder
        prompt_builder = PromptBuilder()
        prompt = prompt_builder.build_rag_prompt(
            request.query,
            chunks,
            conversation_history=history
        )
        system_prompt = prompt_builder.system_prompt
        
        # Generate response
        response = await llm_client.generate(prompt, system=system_prompt)
        
        # Track citations
        from app.generation.citation_tracker import CitationTracker
        citation_tracker = CitationTracker()
        formatted = citation_tracker.format_citations(
            response,
            [chunk for chunk, _ in chunks]
        )
        
        # Update conversation
        conversation_manager.add_message(session_id, "user", request.query)
        conversation_manager.add_message(session_id, "assistant", response)
        
        # Audit log
        audit_logger.log_query(
            session_id=session_id,
            user_id=request.user_id,
            query=request.query,
            retrieved_chunks=[c.chunk_id for c, _ in chunks],
            response=response,
            latency=retrieval_time
        )
        
        return QueryResponse(
            answer=formatted['text'],
            citations=formatted['citations'],
            session_id=session_id,
            chunks_used=len(chunks)
        )
    
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        audit_logger.log_error(
            session_id=session_id,
            error_type=type(e).__name__,
            error_message=str(e),
            query=request.query
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream")
async def stream_query_endpoint(request: QueryRequest):
    """Streaming query endpoint with SSE"""
    
    # Get components
    contextual_agent = app_state['contextual_agent']
    conversation_manager = app_state['conversation_manager']
    content_moderator = app_state['content_moderator']
    
    session_id = request.session_id or str(uuid.uuid4())
    
    # Content moderation (using sync version)
    is_safe, reason = content_moderator.check_content(request.query)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"Content violation: {reason}")
    
    async def event_generator():
        try:
            # Stream agent execution
            async for event in contextual_agent.execute_with_streaming(
                request.query,
                session_id
            ):
                # Format as SSE
                event_str = f"data: {json.dumps(event)}\n\n"
                yield event_str
        
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            error_event = {
                'type': 'error',
                'error': str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback"""
    
    feedback_collector = app_state['feedback_collector']
    
    await feedback_collector.record_feedback(
        query=request.query,
        response=request.response,
        rating=request.rating,
        feedback_text=request.feedback_text,
        session_id=request.session_id
    )
    
    return {"status": "feedback_recorded"}


@app.get("/feedback/stats")
async def get_feedback_stats():
    """Get feedback statistics"""
    
    feedback_collector = app_state['feedback_collector']
    return feedback_collector.get_statistics()


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and index a new document"""
    
    settings = app_state['settings']
    vector_store = app_state['vector_store']
    embedding_model = app_state['embedding_model']
    
    # Save file
    import os
    os.makedirs(settings.DOCUMENTS_PATH, exist_ok=True)
    file_path = f"{settings.DOCUMENTS_PATH}/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Load document
        document_loader = DocumentLoader(base_path=settings.DOCUMENTS_PATH)
        document = await document_loader.load_single_document(file_path)
        
        # Chunk document
        chunker = DocumentChunker()
        chunks = await chunker.chunk_document(document)
        
        # Generate embeddings
        from app.embedding.batch_embedder import BatchEmbedder
        batch_embedder = BatchEmbedder(embedding_model)
        embeddings = await batch_embedder.embed_chunks(chunks)
        
        # Add to vector store
        vector_store.add(embeddings, chunks)
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_created": len(chunks),
            "total_chunks": vector_store.size
        }
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
async def index_documents():
    """Index all documents from documents folder"""
    settings = app_state['settings']
    vector_store = app_state['vector_store']
    embedding_model = app_state['embedding_model']
    
    # Clear existing
    vector_store.clear()
    
    # Reload
    document_loader = DocumentLoader(base_path=settings.DOCUMENTS_PATH)
    documents = await document_loader.load_all_documents()
    
    # Chunk
    chunker = DocumentChunker()
    all_chunks = []
    for doc in documents:
        chunks = await chunker.chunk_document(doc)
        all_chunks.extend(chunks)
    
    # Embed and index
    from app.embedding.batch_embedder import BatchEmbedder
    batch_embedder = BatchEmbedder(embedding_model)
    embeddings = await batch_embedder.embed_chunks(all_chunks)
    vector_store.add(embeddings, all_chunks)
    
    # Save
    vector_store.save(settings.VECTOR_STORE_PATH)
    
    return {
        "status": "success",
        "documents": len(documents),
        "chunks": len(all_chunks),
        "vector_store_size": vector_store.size
    }


@app.get("/conversation/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Get conversation history"""
    
    conversation_manager = app_state['conversation_manager']
    history = conversation_manager.get_full_history(session_id)
    
    return {"session_id": session_id, "history": history}


@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history"""
    
    conversation_manager = app_state['conversation_manager']
    conversation_manager.clear_history(session_id)
    
    return {"status": "cleared", "session_id": session_id}


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    
    metrics_collector = app_state['metrics_collector']
    return metrics_collector.get_all_metrics()


@app.get("/metrics/prometheus")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import Response
    
    metrics_collector = app_state['metrics_collector']
    return Response(
        content=metrics_collector.export_metrics(),
        media_type="text/plain"
    )


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all component status"""
    from app.monitoring.health_checks import HealthChecker
    
    health_checker = HealthChecker(app_state)
    return await health_checker.check_all()


@app.post("/query/multi-document")
async def multi_document_query_endpoint(request: MultiDocumentQueryRequest) -> QueryResponse:
    """Query multiple specific documents"""
    
    retrieval_pipeline = app_state['retrieval_pipeline']
    llm_client = app_state['llm_client']
    conversation_manager = app_state['conversation_manager']
    content_moderator = app_state['content_moderator']
    
    session_id = str(uuid.uuid4())
    
    try:
        # Content moderation
        is_safe, reason = content_moderator.check_content(request.query)
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"Content violation: {reason}")
        
        # Retrieve chunks from specific documents
        chunks, _ = await retrieval_pipeline.retrieve_by_document(
            request.query,
            request.doc_ids,
            top_k=request.top_k_per_doc * len(request.doc_ids)
        )
        
        # Build prompt
        from app.generation.prompt_builder import PromptBuilder
        prompt_builder = PromptBuilder()
        
        # Group chunks by document
        from collections import defaultdict
        doc_groups = defaultdict(list)
        for chunk, score in chunks:
            doc_groups[chunk.doc_id].append((chunk, score))
        
        prompt = prompt_builder.build_multi_document_prompt(
            request.query,
            doc_groups
        )
        
        # Generate response
        response = await llm_client.generate(prompt, system=prompt_builder.system_prompt)
        
        # Track citations
        from app.generation.citation_tracker import CitationTracker
        citation_tracker = CitationTracker()
        formatted = citation_tracker.format_citations(
            response,
            [chunk for chunk, _ in chunks]
        )
        
        return QueryResponse(
            answer=formatted['text'],
            citations=formatted['citations'],
            session_id=session_id,
            chunks_used=len(chunks)
        )
    
    except Exception as e:
        logger.error(f"Multi-document query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    """Transcribe audio file"""
    
    from app.processing.audio_processor import AudioProcessor
    
    # Save temporarily
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        temp_path = tmp_file.name
    
    try:
        audio_processor = AudioProcessor()
        result = await audio_processor.transcribe(temp_path)
        
        return {
            "filename": file.filename,
            "transcription": result["text"],
            "language": result.get("language"),
            "duration": result.get("duration")
        }
    
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/process/image")
async def process_image_endpoint(
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = None
):
    """Extract text from image using OCR"""
    
    from app.processing.image_processor import ImageProcessor
    
    if not file and not image_url:
        raise HTTPException(status_code=400, detail="Provide either file or image_url")
    
    image_processor = ImageProcessor()
    
    if file:
        # Save temporarily
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_path = tmp_file.name
        
        try:
            result = await image_processor.process_image(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        result = await image_processor.process_image(image_url)
    
    return result


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time streaming"""
    from app.streaming.websocket_handler import ConnectionManager
    from fastapi import WebSocketDisconnect
    
    connection_manager = ConnectionManager()
    await connection_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            query = data.get('query')
            session_id = data.get('session_id', client_id)
            
            if not query:
                await websocket.send_json({
                    'type': 'error',
                    'error': 'No query provided'
                })
                continue
            
            # Process query with streaming
            contextual_agent = app_state['contextual_agent']
            
            async for event in contextual_agent.execute_with_streaming(query, session_id):
                await connection_manager.send_message(client_id, event)
    
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await connection_manager.send_message(client_id, {
            'type': 'error',
            'error': str(e)
        })
        connection_manager.disconnect(client_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

