package com.ragtutor.schemas;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Chunk model representing a document chunk
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Chunk {
    
    private String chunkId;
    private String documentId;
    private String content;
    private Map<String, Object> metadata;
    private int chunkIndex;
    private int startChar;
    private int endChar;
    
    public Chunk(String content) {
        this.content = content;
    }
}
