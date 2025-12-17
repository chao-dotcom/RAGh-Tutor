package com.ragtutor.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Audit logging service
 */
@Slf4j
@Component
public class AuditLogger {
    
    private final String logPath;
    private final ObjectMapper objectMapper;
    
    public AuditLogger() {
        this.logPath = "./logs/audit.log";
        this.objectMapper = new ObjectMapper();
        
        try {
            Path path = Paths.get(logPath);
            Files.createDirectories(path.getParent());
        } catch (IOException e) {
            log.error("Failed to create audit log directory", e);
        }
    }
    
    public void logQuery(String sessionId, String userId, String query, 
                        java.util.List<String> retrievedChunks, String response, double latency) {
        Map<String, Object> logEntry = new HashMap<>();
        logEntry.put("event", "query");
        logEntry.put("timestamp", LocalDateTime.now().toString());
        logEntry.put("session_id", sessionId);
        logEntry.put("user_id", userId);
        logEntry.put("query", query);
        logEntry.put("chunks_retrieved", retrievedChunks != null ? retrievedChunks.size() : 0);
        logEntry.put("response_length", response != null ? response.length() : 0);
        logEntry.put("latency_ms", latency);
        
        writeLog(logEntry);
    }
    
    public void logError(String sessionId, String errorType, String errorMessage, String query) {
        Map<String, Object> logEntry = new HashMap<>();
        logEntry.put("event", "error");
        logEntry.put("timestamp", LocalDateTime.now().toString());
        logEntry.put("session_id", sessionId);
        logEntry.put("error_type", errorType);
        logEntry.put("error_message", errorMessage);
        logEntry.put("query", query);
        
        writeLog(logEntry);
    }
    
    public void logDocumentUpload(String filename, long fileSize, int chunksCreated) {
        Map<String, Object> logEntry = new HashMap<>();
        logEntry.put("event", "document_upload");
        logEntry.put("timestamp", LocalDateTime.now().toString());
        logEntry.put("filename", filename);
        logEntry.put("file_size", fileSize);
        logEntry.put("chunks_created", chunksCreated);
        
        writeLog(logEntry);
    }
    
    private void writeLog(Map<String, Object> logEntry) {
        try {
            String json = objectMapper.writeValueAsString(logEntry);
            Path path = Paths.get(logPath);
            Files.writeString(path, json + "\n", 
                StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        } catch (IOException e) {
            log.error("Failed to write audit log", e);
        }
    }
}
