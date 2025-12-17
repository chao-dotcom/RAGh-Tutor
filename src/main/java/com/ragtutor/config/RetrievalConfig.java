package com.ragtutor.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Retrieval configuration
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "retrieval")
public class RetrievalConfig {
    
    private int topK = 10;
    private String mode = "hybrid";
    private double hybridSearchAlpha = 0.7;
    private String rerankerModel = "cross-encoder/ms-marco-MiniLM-L-6-v2";
    private boolean useHybridSearch = false;
}
