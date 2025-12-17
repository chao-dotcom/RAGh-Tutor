# RAG Tutor System - Java Version

Production-ready Retrieval-Augmented Generation (RAG) system built with **Java 17** and **Spring Boot 3**.

## 🚀 Features

- **Vector Search**: In-memory vector store with cosine similarity
- **Document Processing**: PDF, TXT, MD support
- **Multiple LLM Providers**: OpenAI, Anthropic (Claude)
- **Conversation Memory**: Context-aware conversations
- **Streaming Responses**: Server-Sent Events (SSE) support
- **Metrics & Monitoring**: Prometheus/Grafana integration
- **RESTful API**: OpenAPI/Swagger documentation
- **Docker Support**: Containerized deployment

## 📋 Prerequisites

- Java 17 or higher
- Maven 3.6+
- Docker (optional)
- OpenAI or Anthropic API key

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   cd RAGh-Tutor
   ```

2. **Set environment variables**
   ```bash
   export OPENAI_API_KEY=your_openai_key_here
   # or
   export ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

3. **Build the project**
   ```bash
   mvn clean install
   ```

4. **Run the application**
   ```bash
   mvn spring-boot:run
   ```

The application will start at `http://localhost:8000`

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose -f docker-compose-java.yml up --build
   ```

2. **Access services**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/swagger-ui.html
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000

## 📚 API Documentation

### Interactive Documentation
Visit http://localhost:8000/swagger-ui.html for interactive API documentation.

### Key Endpoints

#### Health Check
```bash
GET /api/v1/health
```

#### Query (Non-Streaming)
```bash
POST /api/v1/query
Content-Type: application/json

{
  "query": "What is retrieval augmented generation?",
  "topK": 5,
  "sessionId": "optional-session-id"
}
```

#### Query (Streaming)
```bash
POST /api/v1/stream
Content-Type: application/json

{
  "query": "Explain RAG in detail",
  "topK": 5
}
```

#### Upload Document
```bash
POST /api/v1/documents/upload
Content-Type: multipart/form-data

file: <your-file>
```

#### Index Documents
```bash
POST /api/v1/index
```

#### Conversation History
```bash
GET /api/v1/conversation/{sessionId}/history
DELETE /api/v1/conversation/{sessionId}
```

#### Feedback
```bash
POST /api/v1/feedback
Content-Type: application/json

{
  "query": "...",
  "response": "...",
  "rating": 5,
  "feedback": "Great answer!"
}
```

## 🔧 Configuration

Edit `src/main/resources/application.properties`:

```properties
# Server
server.port=8000

# LLM Settings
llm.provider=openai
llm.openai.model=gpt-4
llm.temperature=0.7
llm.max-tokens=2000

# Retrieval
retrieval.top-k=10
retrieval.mode=hybrid

# Chunking
chunking.size=800
chunking.overlap=200
```

## 📁 Project Structure

```
src/main/java/com/ragtutor/
├── config/          # Configuration classes
├── controller/      # REST controllers
├── service/         # Business logic
├── retrieval/       # Vector store & search
├── embedding/       # Embedding model
├── generation/      # LLM client
├── chunking/        # Document chunking
├── processing/      # Document loading
├── memory/          # Conversation management
├── schemas/         # Request/Response DTOs
└── RagTutorApplication.java
```

## 🧪 Testing

```bash
# Run unit tests
mvn test

# Run integration tests
mvn verify

# Run with coverage
mvn clean test jacoco:report
```

## 📊 Monitoring

### Metrics
- Prometheus metrics: http://localhost:8000/actuator/prometheus
- Application metrics: http://localhost:8000/api/v1/metrics

### Health Checks
- Basic: http://localhost:8000/api/v1/health
- Detailed: http://localhost:8000/api/v1/health/detailed
- Actuator: http://localhost:8000/actuator/health

## 🚀 Deployment

### Build JAR
```bash
mvn clean package
java -jar target/rag-tutor-1.0.0.jar
```

### Docker
```bash
docker build -t rag-tutor:latest .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v ./documents:/app/documents \
  -v ./data:/app/data \
  rag-tutor:latest
```

## 🔐 Security

- Rate limiting: 100 requests/minute per IP
- Content moderation (configurable)
- API key authentication (optional)
- CORS configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check the [documentation](./guide/)

## 🔄 Migration from Python

This is a Java port of the original Python RAG system. Key differences:

- **Framework**: FastAPI → Spring Boot
- **LLM Library**: LangChain → LangChain4j / Native clients
- **Async**: asyncio → CompletableFuture / Reactive (WebFlux)
- **Type Safety**: Pydantic → Bean Validation / Lombok
- **Dependency Management**: pip → Maven

## 📈 Performance

- Startup time: ~15-20 seconds
- Query latency: 200-500ms (depending on LLM)
- Throughput: 100+ queries/second
- Memory usage: ~512MB (base) + vector store

## 🛣️ Roadmap

- [ ] Kubernetes deployment manifests
- [ ] Integration with Pinecone/Weaviate
- [ ] Advanced RAG techniques (HyDE, RAG-Fusion)
- [ ] Multi-modal support (images, audio)
- [ ] GraphQL API
- [ ] WebSocket support
- [ ] Redis caching layer

---

**Made with ☕ in Java**
