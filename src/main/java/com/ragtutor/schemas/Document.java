package com.ragtutor.schemas;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Document model
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Document {
    
    private String docId;
    private String content;
    private Map<String, Object> metadata;
    private String source;
    private String title;
}
