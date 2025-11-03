# RAGh-Tutor

A production-ready Retrieval-Augmented Generation (RAG) system built with FastAPI.

## 🎥 Demo

[![RAGh-Tutor Demo](assets/ragh_tutor.png)](assets/Ragh_tutor_READMEver.mp4)

Click the thumbnail above to watch the demo video!

## Features

- **Document Processing**: Support for PDF, DOCX, Excel, CSV, HTML, JSON, Audio, Images, and more
- **Advanced Chunking**: Multiple chunking strategies (semantic, specialized, overlap)
- **Embedding**: Sentence transformers with batch processing and multimodal support
- **Vector Store**: FAISS-based vector store with hybrid search (vector + BM25)
- **LLM Integration**: Support for OpenAI and Anthropic
- **Agent Orchestration**: RAG agent with tool support and contextual execution
- **Conversation Memory**: Context management and summarization
- **Security**: Content moderation, PII detection, rate limiting, audit logging
- **Streaming**: Server-Sent Events (SSE) and WebSocket support
- **Monitoring & Observability**: Metrics collection, health checks, performance profiling, tracing
- **Performance Optimization**: Query optimization, response caching, batch processing
- **Query Analytics**: Query pattern analysis, performance tracking, usage statistics
- **Multi-Document QA**: Query across multiple specific documents
- **Feedback System**: Collect and analyze user feedback
- **API**: RESTful API with FastAPI

## Installation

### 🐳 Docker (Recommended - Solves Windows Issues)

**If you're encountering Windows installation errors (pytesseract, playwright), use Docker!**

**Windows Commands (No Make Required):**
```powershell
# 1. Build Docker image (includes all dependencies pre-installed)
docker-compose build

# 2. Start services
docker-compose up -d

# 3. Index documents (after adding files to documents/ folder)
docker-compose exec rag-api python scripts/index_documents.py

# Access at http://localhost:8000
```

**Or with Make (if installed):**
```powershell
make docker-build
make docker-run
make docker-index
```

See `guide/windows-setup.md` for detailed Windows setup guide.

### 💻 Native Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

⚠️ **Windows Warning**: You may encounter errors with `pytesseract` and `playwright`. Use Docker instead!

2. Set up environment variables (create `.env` file):
```env
OPENAI_API_KEY=your_key_here
# or
ANTHROPIC_API_KEY=your_key_here

EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
```

## Usage

### With Docker (Recommended)

**Windows Commands:**
```powershell
# Start services (includes API, Redis, Prometheus)
docker-compose up -d

# Index documents
docker-compose exec rag-api python scripts/index_documents.py

# Access services:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Prometheus: http://localhost:9090
# - Redis: localhost:6379

# Query (PowerShell)
$body = @{query="What is RAG?"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/query -Method POST -Body $body -ContentType "application/json"
```

**Or with Make:**
```powershell
make docker-run
make docker-index
```

**Development Mode:**
```powershell
# Uses docker-compose.yml with hot-reload enabled
docker-compose up -d

# Logs
docker-compose logs -f rag-api
```

### Native Installation

```bash
# Start server
uvicorn app.main:app --reload

# Index documents (place files in documents/ folder)
make index

# Query
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query": "What is RAG?"}'
```

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /health/detailed` - Detailed health check with component status
- `GET /ready` - Kubernetes readiness check
- `POST /query` - Query the knowledge base
- `POST /query/multi-document` - Query across multiple specific documents
- `POST /stream` - Streaming query (Server-Sent Events)
- `GET /docs` - Interactive API documentation (Swagger UI)

### Document Management
- `POST /documents/upload` - Upload and index a new document
- `POST /index` - Index all documents from documents folder

### Processing Endpoints
- `POST /process/audio` - Transcribe audio files
- `POST /process/image` - Extract text from images using OCR

### Conversation Management
- `GET /conversation/{session_id}/history` - Get conversation history
- `DELETE /conversation/{session_id}` - Clear conversation history

### Feedback & Analytics
- `POST /feedback` - Submit user feedback
- `GET /feedback/stats` - Get feedback statistics

### Monitoring & Metrics
- `GET /metrics` - Get system metrics (JSON)
- `GET /metrics/prometheus` - Prometheus metrics endpoint
- `WebSocket /ws/{client_id}` - WebSocket for real-time streaming

See `guide/quick-start.md` for full API reference.

## Monitoring & Observability

The system includes comprehensive monitoring capabilities:

- **Prometheus Metrics**: Export metrics at `/metrics/prometheus`
- **Health Checks**: Basic (`/health`) and detailed (`/health/detailed`) health endpoints
- **Performance Profiling**: Built-in performance profiler for optimization
- **Tracing**: Distributed tracing support
- **Query Analytics**: Track query patterns, performance, and usage statistics

### Monitoring Setup

With Docker Compose, Prometheus is automatically configured:
```powershell
# Access Prometheus UI
# http://localhost:9090
```

For production deployments, see `k8s/` directory for Kubernetes manifests with monitoring configured.

## Deployment

### Docker Production

Production-ready Docker Compose configuration is available:
```powershell
# Use production configuration
docker-compose -f docker/docker-compose.prod.yml up -d
```

### Kubernetes

Kubernetes deployment manifests are available in the `k8s/` directory:
- Deployment with horizontal pod autoscaling
- Service and Ingress configuration
- ConfigMap and Secrets management
- Persistent volume claims for data storage

## Documentation

- **Windows Setup**: `guide/windows-setup.md` ⭐ (No Make required - Windows-friendly commands)
- **Quick Start**: `guide/quick-start.md`
- **Docker Setup**: `guide/docker-setup-instructions.md`
- **Docker Quick Fix**: `guide/docker-quick-fix.md` (solves installation errors)
- **Troubleshooting**: `guide/troubleshooting.md`

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── dependencies.py      # Dependency injection
│
├── chunking/            # Document chunking strategies
│   ├── document_chunker.py
│   ├── semantic_chunker.py
│   └── specialized_chunker.py
│
├── embedding/           # Embedding generation
│   ├── embedding_model.py
│   ├── batch_embedder.py
│   └── multimodal_embedder.py
│
├── retrieval/           # Vector store and retrieval
│   ├── vector_store.py
│   ├── retrieval_pipeline.py
│   ├── hybrid_search.py
│   ├── reranker.py
│   └── query_expansion.py
│
├── generation/          # LLM integration
│   ├── llm_client.py
│   ├── prompt_builder.py
│   ├── response_parser.py
│   └── citation_tracker.py
│
├── agents/              # Agent orchestration
│   ├── rag_agent.py
│   ├── contextual_agent_executor.py
│   ├── tool_registry.py
│   ├── action_planner.py
│   └── tools/           # Agent tools
│       └── browser_tool.py
│
├── memory/              # Conversation management
│   ├── conversation_manager.py
│   ├── context_window_manager.py
│   ├── memory_store.py
│   └── summarizer.py
│
├── processing/          # Document processing
│   ├── document_loader.py
│   ├── pdf_processor.py
│   ├── audio_processor.py
│   ├── image_processor.py
│   ├── web_scraper.py
│   └── table_extractor.py
│
├── security/            # Security components
│   ├── content_moderation.py
│   ├── pii_detector.py
│   ├── rate_limiter.py
│   ├── auth.py
│   ├── audit_logger.py
│   └── action_budget.py
│
├── streaming/          # Streaming support
│   ├── sse_stream.py
│   ├── websocket_handler.py
│   └── stream_aggregator.py
│
├── monitoring/          # Observability & monitoring
│   ├── metrics.py
│   ├── health_checks.py
│   ├── performance_profiler.py
│   └── tracing.py
│
├── performance/         # Performance optimization
│   ├── query_optimizer.py
│   ├── response_cache.py
│   └── batch_processor.py
│
├── features/            # Advanced features
│   ├── feedback_collector.py
│   ├── multi_document_qa.py
│   └── query_analytics.py
│
├── middleware/          # Middleware components
│   └── rate_limiter.py
│
├── schemas/             # Pydantic schemas
│   ├── requests.py
│   ├── responses.py
│   ├── documents.py
│   └── events.py
│
└── utils/               # Utility functions
    ├── caching.py
    ├── file_handling.py
    ├── text_processing.py
    └── validators.py
```

## License

MIT

