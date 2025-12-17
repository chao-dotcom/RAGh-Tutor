package com.ragtutor.chunking;

import com.ragtutor.config.ChunkingConfig;
import com.ragtutor.schemas.Chunk;
import com.ragtutor.schemas.Document;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Chunk documents with overlap for better retrieval
 */
@Slf4j
@Component
public class DocumentChunker {
    
    private final int chunkSize;
    private final int chunkOverlap;
    private final String separator;
    
    public DocumentChunker(ChunkingConfig config) {
        this.chunkSize = config.getSize();
        this.chunkOverlap = config.getOverlap();
        this.separator = config.getSeparator();
        log.info("Initialized DocumentChunker with size={}, overlap={}", chunkSize, chunkOverlap);
    }
    
    /**
     * Chunk a document into smaller pieces
     */
    public List<Chunk> chunkDocument(Document document) {
        String text = document.getContent();
        
        // Split by separator first
        List<String> splits = splitText(text, separator);
        
        List<Chunk> chunks = new ArrayList<>();
        List<String> currentChunk = new ArrayList<>();
        int currentLength = 0;
        
        for (String split : splits) {
            int splitLength = split.length();
            
            if (currentLength + splitLength > chunkSize && !currentChunk.isEmpty()) {
                // Create chunk
                String chunkText = String.join(separator, currentChunk);
                Chunk chunk = createChunk(chunkText, document, chunks.size());
                chunks.add(chunk);
                
                // Start new chunk with overlap
                int overlapLength = 0;
                List<String> overlapParts = new ArrayList<>();
                
                for (int i = currentChunk.size() - 1; i >= 0; i--) {
                    String part = currentChunk.get(i);
                    if (overlapLength + part.length() < chunkOverlap) {
                        overlapParts.add(0, part);
                        overlapLength += part.length();
                    } else {
                        break;
                    }
                }
                
                currentChunk = overlapParts;
                currentLength = overlapLength;
            }
            
            currentChunk.add(split);
            currentLength += splitLength;
        }
        
        // Add final chunk
        if (!currentChunk.isEmpty()) {
            String chunkText = String.join(separator, currentChunk);
            Chunk chunk = createChunk(chunkText, document, chunks.size());
            chunks.add(chunk);
        }
        
        log.debug("Chunked document {} into {} chunks", document.getDocId(), chunks.size());
        return chunks;
    }
    
    /**
     * Split text by separator
     */
    private List<String> splitText(String text, String separator) {
        List<String> splits = new ArrayList<>();
        
        if (separator != null && !separator.isEmpty()) {
            String[] parts = text.split(separator);
            for (String part : parts) {
                if (!part.trim().isEmpty()) {
                    splits.add(part);
                }
            }
        } else {
            for (char c : text.toCharArray()) {
                splits.add(String.valueOf(c));
            }
        }
        
        return splits;
    }
    
    /**
     * Create a chunk object
     */
    private Chunk createChunk(String text, Document document, int chunkIndex) {
        String chunkId = document.getDocId() + "_chunk_" + chunkIndex;
        
        Map<String, Object> metadata = new HashMap<>();
        if (document.getMetadata() != null) {
            metadata.putAll(document.getMetadata());
        }
        metadata.put("chunk_index", chunkIndex);
        metadata.put("chunk_length", text.length());
        
        return Chunk.builder()
            .content(text)
            .chunkId(chunkId)
            .documentId(document.getDocId())
            .metadata(metadata)
            .chunkIndex(chunkIndex)
            .build();
    }
}
