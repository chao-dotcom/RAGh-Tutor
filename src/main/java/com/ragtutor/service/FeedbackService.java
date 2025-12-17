package com.ragtutor.service;

import com.ragtutor.schemas.FeedbackRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.time.LocalDateTime;
import java.util.*;

/**
 * Feedback collection service
 */
@Slf4j
@Service
public class FeedbackService {
    
    private final String storagePath;
    private final ObjectMapper objectMapper;
    private final List<Map<String, Object>> feedbackCache;
    
    public FeedbackService(@Value("${app.feedback-storage:./data/feedback}") String storagePath) {
        this.storagePath = storagePath;
        this.objectMapper = new ObjectMapper();
        this.feedbackCache = Collections.synchronizedList(new ArrayList<>());
        
        // Create storage directory
        try {
            Files.createDirectories(Paths.get(storagePath));
        } catch (IOException e) {
            log.error("Failed to create feedback storage directory", e);
        }
        
        log.info("Initialized FeedbackService with storage: {}", storagePath);
    }
    
    public void recordFeedback(FeedbackRequest request) {
        Map<String, Object> feedbackData = new HashMap<>();
        feedbackData.put("query", request.getQuery());
        feedbackData.put("response", request.getResponse());
        feedbackData.put("rating", request.getRating());
        feedbackData.put("feedback", request.getFeedback());
        feedbackData.put("session_id", request.getSessionId());
        feedbackData.put("timestamp", LocalDateTime.now().toString());
        
        // Add to cache
        feedbackCache.add(feedbackData);
        
        // Write to file
        try {
            String filename = String.format("feedback_%s.json", 
                LocalDateTime.now().toString().replace(":", "-"));
            Path filepath = Paths.get(storagePath, filename);
            
            String json = objectMapper.writerWithDefaultPrettyPrinter()
                .writeValueAsString(feedbackData);
            Files.writeString(filepath, json, StandardOpenOption.CREATE);
            
            log.info("Recorded feedback for session: {}", request.getSessionId());
        } catch (IOException e) {
            log.error("Failed to write feedback to file", e);
        }
    }
    
    public Map<String, Object> getStatistics() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("total_feedback", feedbackCache.size());
        
        if (!feedbackCache.isEmpty()) {
            double averageRating = feedbackCache.stream()
                .map(f -> f.get("rating"))
                .filter(Objects::nonNull)
                .mapToInt(r -> (Integer) r)
                .average()
                .orElse(0.0);
            
            stats.put("average_rating", averageRating);
        } else {
            stats.put("average_rating", 0.0);
        }
        
        return stats;
    }
}
