package com.ragtutor.schemas;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Query request schema
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class QueryRequest {
    
    @NotBlank
    @Size(min = 1, max = 2000)
    private String query;
    
    private String sessionId;
    
    private String userId;
    
    @Min(1)
    @Max(20)
    @Builder.Default
    private Integer topK = 5;
    
    @Builder.Default
    private String retrievalMode = "hybrid";
    
    @Builder.Default
    private Boolean includeMetadata = true;
    
    private Map<String, Object> filters;
    
    @Builder.Default
    private Boolean useAgent = false;
}
