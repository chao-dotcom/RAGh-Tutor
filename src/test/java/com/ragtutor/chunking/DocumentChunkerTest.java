package com.ragtutor.chunking;

import com.ragtutor.config.ChunkingConfig;
import com.ragtutor.schemas.Chunk;
import com.ragtutor.schemas.Document;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class DocumentChunkerTest {
    
    private DocumentChunker chunker;
    private ChunkingConfig config;
    
    @BeforeEach
    void setUp() {
        config = new ChunkingConfig();
        config.setSize(100);
        config.setOverlap(20);
        config.setSeparator("\n\n");
        
        chunker = new DocumentChunker(config);
    }
    
    @Test
    void chunkDocument_createsMultipleChunks() {
        // Arrange
        String content = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph.\n\nFourth paragraph.";
        Document document = Document.builder()
            .docId("test-doc")
            .content(content)
            .metadata(new HashMap<>())
            .build();
        
        // Act
        List<Chunk> chunks = chunker.chunkDocument(document);
        
        // Assert
        assertNotNull(chunks);
        assertTrue(chunks.size() > 0);
        
        // Verify each chunk has required fields
        for (Chunk chunk : chunks) {
            assertNotNull(chunk.getChunkId());
            assertNotNull(chunk.getContent());
            assertNotNull(chunk.getDocumentId());
            assertEquals("test-doc", chunk.getDocumentId());
        }
    }
    
    @Test
    void chunkDocument_preservesMetadata() {
        // Arrange
        HashMap<String, Object> metadata = new HashMap<>();
        metadata.put("source", "test.txt");
        metadata.put("author", "Test Author");
        
        Document document = Document.builder()
            .docId("test-doc")
            .content("Some content here")
            .metadata(metadata)
            .build();
        
        // Act
        List<Chunk> chunks = chunker.chunkDocument(document);
        
        // Assert
        for (Chunk chunk : chunks) {
            assertTrue(chunk.getMetadata().containsKey("source"));
            assertTrue(chunk.getMetadata().containsKey("author"));
            assertTrue(chunk.getMetadata().containsKey("chunk_index"));
        }
    }
}
