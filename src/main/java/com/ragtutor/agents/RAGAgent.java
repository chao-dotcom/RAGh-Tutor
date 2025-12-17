package com.ragtutor.agents;

import com.ragtutor.generation.LLMClient;
import com.ragtutor.retrieval.InMemoryVectorStore;
import com.ragtutor.schemas.Chunk;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Main RAG agent orchestrator
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RAGAgent {
    
    private final LLMClient llmClient;
    private final com.ragtutor.embedding.EmbeddingModelService embeddingModel;
    private final InMemoryVectorStore vectorStore;
    
    /**
     * Process a query through RAG pipeline
     */
    public Map<String, Object> query(String query, int topK) {
        long startTime = System.currentTimeMillis();
        
        // Retrieve relevant chunks
        float[] queryEmbedding = embeddingModel.encodeSingle(query);
        List<InMemoryVectorStore.ChunkWithScore> chunksWithScores = 
            vectorStore.search(queryEmbedding, topK);
        
        long retrievalTime = System.currentTimeMillis() - startTime;
        
        // Build prompt
        String prompt = buildPrompt(query, chunksWithScores);
        String systemPrompt = "You are a helpful AI assistant. Answer based on the provided context.";
        
        // Generate response
        long genStart = System.currentTimeMillis();
        String response = llmClient.generate(prompt, systemPrompt);
        long generationTime = System.currentTimeMillis() - genStart;
        
        // Build result
        Map<String, Object> result = new HashMap<>();
        result.put("response", response);
        result.put("sources", chunksWithScores.stream()
            .map(InMemoryVectorStore.ChunkWithScore::getChunk)
            .collect(Collectors.toList()));
        result.put("retrieval_time", retrievalTime / 1000.0);
        result.put("generation_time", generationTime / 1000.0);
        
        return result;
    }
    
    private String buildPrompt(String query, List<InMemoryVectorStore.ChunkWithScore> chunks) {
        StringBuilder prompt = new StringBuilder();
        prompt.append("Context:\n\n");
        
        for (int i = 0; i < chunks.size(); i++) {
            Chunk chunk = chunks.get(i).getChunk();
            prompt.append(String.format("[%d] %s\n\n", i + 1, chunk.getContent()));
        }
        
        prompt.append("\nQuestion: ").append(query);
        prompt.append("\n\nPlease provide a detailed answer based on the context above.");
        
        return prompt.toString();
    }
}
