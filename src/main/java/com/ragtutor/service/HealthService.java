package com.ragtutor.service;

import com.ragtutor.config.AppConfig;
import com.ragtutor.retrieval.InMemoryVectorStore;
import com.ragtutor.schemas.HealthResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Health check service
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class HealthService {
    
    private final InMemoryVectorStore vectorStore;
    private final AppConfig appConfig;
    
    public HealthResponse checkHealth() {
        return HealthResponse.builder()
            .status("healthy")
            .version(appConfig.getVersion())
            .documentsIndexed(vectorStore.size())
            .vectorStoreSize(vectorStore.size())
            .embeddingModelLoaded(true)
            .llmClientReady(true)
            .build();
    }
    
    public java.util.Map<String, Object> checkDetailedHealth() {
        java.util.Map<String, Object> health = new java.util.HashMap<>();
        health.put("status", "healthy");
        health.put("version", appConfig.getVersion());
        health.put("vector_store_size", vectorStore.size());
        health.put("embedding_model_loaded", true);
        health.put("llm_client_ready", true);
        health.put("timestamp", java.time.LocalDateTime.now().toString());
        return health;
    }
}
