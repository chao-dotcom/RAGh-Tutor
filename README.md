# RAG System

A production-ready Retrieval-Augmented Generation (RAG) system built with FastAPI.

## Features

- **Document Processing**: Support for PDF, DOCX, Excel, CSV, HTML, JSON, and more
- **Advanced Chunking**: Multiple chunking strategies (semantic, specialized, overlap)
- **Embedding**: Sentence transformers with batch processing
- **Vector Store**: FAISS-based vector store with hybrid search (vector + BM25)
- **LLM Integration**: Support for OpenAI and Anthropic
- **Agent Orchestration**: RAG agent with tool support
- **Conversation Memory**: Context management and summarization
- **Security**: Content moderation, PII detection, rate limiting
- **Streaming**: Server-Sent Events and WebSocket support
- **API**: RESTful API with FastAPI

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables (create `.env` file):

```env
OPENAI_API_KEY=your_key_here
# or
ANTHROPIC_API_KEY=your_key_here

EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
```

## Usage

1. Start the server:

```bash
python -m app.main
```

Or with uvicorn:

```bash
uvicorn app.main:app --reload
```

2. Index documents:

Place documents in the `documents/` directory and call:

```bash
curl -X POST http://localhost:8000/index
```

3. Query the system:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?"}'
```

## API Endpoints

- `GET /health` - Health check
- `POST /query` - Query the knowledge base
- `POST /chat` - Chat with conversation context
- `POST /index` - Index documents

## Project Structure

```
app/
├── main.py              # FastAPI application
├── config.py            # Configuration
├── chunking/            # Document chunking
├── embedding/           # Embedding generation
├── retrieval/           # Vector store and retrieval
├── generation/          # LLM integration
├── agents/              # Agent orchestration
├── memory/              # Conversation management
├── processing/          # Document processing
├── security/            # Security components
├── streaming/           # Streaming support
└── utils/               # Utilities
```

## License

MIT

