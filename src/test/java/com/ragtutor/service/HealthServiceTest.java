package com.ragtutor.service;

import com.ragtutor.config.AppConfig;
import com.ragtutor.retrieval.InMemoryVectorStore;
import com.ragtutor.schemas.HealthResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class HealthServiceTest {
    
    @Mock
    private InMemoryVectorStore vectorStore;
    
    @Mock
    private AppConfig appConfig;
    
    private HealthService healthService;
    
    @BeforeEach
    void setUp() {
        healthService = new HealthService(vectorStore, appConfig);
    }
    
    @Test
    void checkHealth_returnsHealthyStatus() {
        // Arrange
        when(vectorStore.size()).thenReturn(100);
        when(appConfig.getVersion()).thenReturn("1.0.0");
        
        // Act
        HealthResponse response = healthService.checkHealth();
        
        // Assert
        assertNotNull(response);
        assertEquals("healthy", response.getStatus());
        assertEquals("1.0.0", response.getVersion());
        assertEquals(100, response.getDocumentsIndexed());
        assertTrue(response.isEmbeddingModelLoaded());
        assertTrue(response.isLlmClientReady());
    }
}
