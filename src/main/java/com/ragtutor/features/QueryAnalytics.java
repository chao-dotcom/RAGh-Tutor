package com.ragtutor.features;

import com.ragtutor.schemas.QueryRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Query analytics and tracking
 */
@Slf4j
@Component
public class QueryAnalytics {
    
    private final Map<String, List<QueryRecord>> queryHistory;
    private final Map<String, Integer> queryFrequency;
    
    public QueryAnalytics() {
        this.queryHistory = new ConcurrentHashMap<>();
        this.queryFrequency = new ConcurrentHashMap<>();
    }
    
    /**
     * Record a query
     */
    public void recordQuery(String userId, QueryRequest request, long latencyMs) {
        QueryRecord record = new QueryRecord(
            request.getQuery(),
            LocalDateTime.now(),
            latencyMs
        );
        
        // Add to history
        queryHistory.computeIfAbsent(userId, k -> new ArrayList<>()).add(record);
        
        // Update frequency
        String queryKey = request.getQuery().toLowerCase().trim();
        queryFrequency.merge(queryKey, 1, Integer::sum);
        
        log.debug("Recorded query for user: {}", userId);
    }
    
    /**
     * Get popular queries
     */
    public List<Map.Entry<String, Integer>> getPopularQueries(int limit) {
        return queryFrequency.entrySet().stream()
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(limit)
            .toList();
    }
    
    /**
     * Get user query history
     */
    public List<QueryRecord> getUserHistory(String userId) {
        return queryHistory.getOrDefault(userId, new ArrayList<>());
    }
    
    /**
     * Get analytics summary
     */
    public Map<String, Object> getSummary() {
        Map<String, Object> summary = new HashMap<>();
        
        int totalQueries = queryHistory.values().stream()
            .mapToInt(List::size)
            .sum();
        
        double avgLatency = queryHistory.values().stream()
            .flatMap(List::stream)
            .mapToLong(QueryRecord::getLatencyMs)
            .average()
            .orElse(0.0);
        
        summary.put("total_queries", totalQueries);
        summary.put("unique_users", queryHistory.size());
        summary.put("unique_queries", queryFrequency.size());
        summary.put("avg_latency_ms", avgLatency);
        summary.put("popular_queries", getPopularQueries(10));
        
        return summary;
    }
    
    /**
     * Query record
     */
    public record QueryRecord(
        String query,
        LocalDateTime timestamp,
        long latencyMs
    ) {}
}
