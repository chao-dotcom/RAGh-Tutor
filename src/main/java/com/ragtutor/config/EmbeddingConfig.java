package com.ragtutor.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Embedding model configuration
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "embedding")
public class EmbeddingConfig {
    
    private String model = "sentence-transformers/all-mpnet-base-v2";
    private String device = "cpu";
    private int batchSize = 32;
    private int dimension = 768;
}
