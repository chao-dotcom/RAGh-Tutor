package com.ragtutor.schemas;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Health response schema
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class HealthResponse {
    
    private String status;
    private String version;
    private long documentsIndexed;
    private long vectorStoreSize;
    private boolean embeddingModelLoaded;
    private boolean llmClientReady;
}
