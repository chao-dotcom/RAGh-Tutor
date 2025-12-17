package com.ragtutor.schemas;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * Query response schema
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class QueryResponse {
    
    private String answer;
    private List<Chunk> sources;
    private List<String> citations;
    private Map<String, Object> metadata;
    private double retrievalTime;
    private double generationTime;
    private String sessionId;
}
