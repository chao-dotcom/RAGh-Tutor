package com.ragtutor.schemas;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * Multi-document query request
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MultiDocumentQueryRequest {
    
    private String query;
    private List<String> documentIds;
    private Integer topK;
    private Map<String, Object> filters;
}
