package com.ragtutor.service;

import com.ragtutor.middleware.RateLimiterFilter;
import com.ragtutor.security.ActionBudgetGuard;
import com.ragtutor.security.AuditLogger;
import com.ragtutor.security.ContentModerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Application initialization service
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class InitializationService {
    
    private final com.ragtutor.retrieval.InMemoryVectorStore vectorStore;
    private final com.ragtutor.config.AppConfig appConfig;
    
    /**
     * Initialize application on startup
     */
    public void initialize() {
        log.info("Initializing RAG Tutor application...");
        
        // Create necessary directories
        createDirectories();
        
        // Try to load existing vector store
        tryLoadVectorStore();
        
        log.info("Application initialization complete!");
        log.info("Vector store size: {}", vectorStore.size());
    }
    
    private void createDirectories() {
        com.ragtutor.utils.FileUtils.ensureDirectoryExists(appConfig.getDocumentFolder());
        com.ragtutor.utils.FileUtils.ensureDirectoryExists(appConfig.getDataFolder());
        com.ragtutor.utils.FileUtils.ensureDirectoryExists(appConfig.getLogFolder());
        com.ragtutor.utils.FileUtils.ensureDirectoryExists(appConfig.getFeedbackStorage());
    }
    
    private void tryLoadVectorStore() {
        try {
            String vectorStorePath = appConfig.getDataFolder() + "/vector_store";
            vectorStore.load(vectorStorePath);
            log.info("Loaded existing vector store with {} chunks", vectorStore.size());
        } catch (Exception e) {
            log.info("No existing vector store found, will create new one");
        }
    }
}
