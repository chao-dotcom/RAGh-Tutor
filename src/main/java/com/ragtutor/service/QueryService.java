package com.ragtutor.service;

import com.ragtutor.config.RetrievalConfig;
import com.ragtutor.embedding.EmbeddingModelService;
import com.ragtutor.generation.LLMClient;
import com.ragtutor.memory.ConversationManager;
import com.ragtutor.retrieval.InMemoryVectorStore;
import com.ragtutor.schemas.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

/**
 * Query processing service
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class QueryService {
    
    private final InMemoryVectorStore vectorStore;
    private final EmbeddingModelService embeddingModel;
    private final LLMClient llmClient;
    private final ConversationManager conversationManager;
    private final RetrievalConfig retrievalConfig;
    private final MetricsService metricsService;
    
    public QueryResponse processQuery(QueryRequest request, String sessionId) {
        long startTime = System.currentTimeMillis();
        
        try {
            // Content moderation would go here
            
            // Get conversation history
            List<ConversationManager.Message> history = conversationManager.getContext(sessionId, 2000);
            
            // Retrieve chunks
            long retrievalStart = System.currentTimeMillis();
            List<InMemoryVectorStore.ChunkWithScore> chunksWithScores = retrieveChunks(
                request.getQuery(),
                request.getTopK() != null ? request.getTopK() : retrievalConfig.getTopK()
            );
            long retrievalTime = System.currentTimeMillis() - retrievalStart;
            
            // Build prompt
            String prompt = buildRAGPrompt(request.getQuery(), chunksWithScores, history);
            String systemPrompt = getSystemPrompt();
            
            // Generate response
            long genStart = System.currentTimeMillis();
            String response = llmClient.generate(prompt, systemPrompt);
            long generationTime = System.currentTimeMillis() - genStart;
            
            // Extract citations (simplified)
            List<String> citations = extractCitations(chunksWithScores);
            
            // Update conversation
            conversationManager.addMessage(sessionId, "user", request.getQuery());
            conversationManager.addMessage(sessionId, "assistant", response);
            
            // Record metrics
            metricsService.recordQuery(System.currentTimeMillis() - startTime);
            
            List<Chunk> sources = chunksWithScores.stream()
                .map(InMemoryVectorStore.ChunkWithScore::getChunk)
                .collect(Collectors.toList());
            
            return QueryResponse.builder()
                .answer(response)
                .sources(sources)
                .citations(citations)
                .retrievalTime(retrievalTime / 1000.0)
                .generationTime(generationTime / 1000.0)
                .sessionId(sessionId)
                .build();
        } catch (Exception e) {
            log.error("Query processing failed", e);
            metricsService.recordError("query_processing");
            throw new RuntimeException("Query processing failed: " + e.getMessage(), e);
        }
    }
    
    public QueryResponse processChat(ChatRequest request) {
        String conversationId = request.getConversationId() != null ? 
            request.getConversationId() : conversationManager.createConversation();
        
        QueryRequest queryRequest = QueryRequest.builder()
            .query(request.getMessage())
            .sessionId(conversationId)
            .build();
        
        return processQuery(queryRequest, conversationId);
    }
    
    public void processQueryStreaming(QueryRequest request, String sessionId, SseEmitter emitter) {
        CompletableFuture.runAsync(() -> {
            try {
                // Retrieve chunks
                List<InMemoryVectorStore.ChunkWithScore> chunksWithScores = retrieveChunks(
                    request.getQuery(),
                    request.getTopK() != null ? request.getTopK() : retrievalConfig.getTopK()
                );
                
                // Build prompt
                List<ConversationManager.Message> history = conversationManager.getContext(sessionId, 2000);
                String prompt = buildRAGPrompt(request.getQuery(), chunksWithScores, history);
                String systemPrompt = getSystemPrompt();
                
                // Stream response
                StringBuilder fullResponse = new StringBuilder();
                llmClient.generateStream(prompt, systemPrompt)
                    .doOnNext(chunk -> {
                        try {
                            fullResponse.append(chunk);
                            Map<String, Object> event = new HashMap<>();
                            event.put("type", "chunk");
                            event.put("content", chunk);
                            emitter.send(event);
                        } catch (IOException e) {
                            log.error("Error sending SSE event", e);
                        }
                    })
                    .doOnComplete(() -> {
                        try {
                            // Update conversation
                            conversationManager.addMessage(sessionId, "user", request.getQuery());
                            conversationManager.addMessage(sessionId, "assistant", fullResponse.toString());
                            
                            Map<String, Object> completeEvent = new HashMap<>();
                            completeEvent.put("type", "complete");
                            emitter.send(completeEvent);
                            emitter.complete();
                        } catch (IOException e) {
                            log.error("Error completing SSE stream", e);
                        }
                    })
                    .doOnError(error -> {
                        log.error("Error in streaming", error);
                        emitter.completeWithError(error);
                    })
                    .subscribe();
                
            } catch (Exception e) {
                log.error("Streaming query failed", e);
                emitter.completeWithError(e);
            }
        });
    }
    
    public QueryResponse processMultiDocumentQuery(MultiDocumentQueryRequest request) {
        // Simplified implementation - filter chunks by document IDs
        String sessionId = UUID.randomUUID().toString();
        
        List<InMemoryVectorStore.ChunkWithScore> chunksWithScores = retrieveChunks(
            request.getQuery(),
            request.getTopK() != null ? request.getTopK() * request.getDocumentIds().size() : 50
        );
        
        // Filter by document IDs if provided
        if (request.getDocumentIds() != null && !request.getDocumentIds().isEmpty()) {
            chunksWithScores = chunksWithScores.stream()
                .filter(cws -> request.getDocumentIds().contains(cws.getChunk().getDocumentId()))
                .collect(Collectors.toList());
        }
        
        String prompt = buildRAGPrompt(request.getQuery(), chunksWithScores, new ArrayList<>());
        String systemPrompt = getSystemPrompt();
        
        String response = llmClient.generate(prompt, systemPrompt);
        List<String> citations = extractCitations(chunksWithScores);
        
        List<Chunk> sources = chunksWithScores.stream()
            .map(InMemoryVectorStore.ChunkWithScore::getChunk)
            .collect(Collectors.toList());
        
        return QueryResponse.builder()
            .answer(response)
            .sources(sources)
            .citations(citations)
            .sessionId(sessionId)
            .build();
    }
    
    private List<InMemoryVectorStore.ChunkWithScore> retrieveChunks(String query, int topK) {
        float[] queryEmbedding = embeddingModel.encodeSingle(query);
        return vectorStore.search(queryEmbedding, topK);
    }
    
    private String buildRAGPrompt(
        String query,
        List<InMemoryVectorStore.ChunkWithScore> chunks,
        List<ConversationManager.Message> history
    ) {
        StringBuilder prompt = new StringBuilder();
        
        prompt.append("Context:\n\n");
        for (int i = 0; i < chunks.size(); i++) {
            InMemoryVectorStore.ChunkWithScore cws = chunks.get(i);
            prompt.append(String.format("[%d] %s\n\n", i + 1, cws.getChunk().getContent()));
        }
        
        if (!history.isEmpty()) {
            prompt.append("\nConversation History:\n");
            for (ConversationManager.Message msg : history) {
                prompt.append(String.format("%s: %s\n", msg.getRole(), msg.getContent()));
            }
        }
        
        prompt.append("\nQuestion: ").append(query).append("\n\n");
        prompt.append("Please provide a detailed answer based on the context above. ");
        prompt.append("Include citations using [n] format where n is the source number.");
        
        return prompt.toString();
    }
    
    private String getSystemPrompt() {
        return "You are a helpful AI assistant that answers questions based on the provided context. " +
               "Always cite your sources using [n] format. Be concise but thorough.";
    }
    
    private List<String> extractCitations(List<InMemoryVectorStore.ChunkWithScore> chunks) {
        return chunks.stream()
            .limit(5)
            .map(cws -> {
                Chunk chunk = cws.getChunk();
                return String.format("[%s] %s",
                    chunk.getChunkId(),
                    chunk.getMetadata().getOrDefault("source", "Unknown"));
            })
            .collect(Collectors.toList());
    }
}
