package com.ragtutor.performance;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.concurrent.TimeUnit;

/**
 * Response cache for query results
 */
@Slf4j
@Component
public class ResponseCache {
    
    private final Cache<String, CachedResponse> cache;
    
    public ResponseCache() {
        this.cache = Caffeine.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(1, TimeUnit.HOURS)
            .recordStats()
            .build();
        
        log.info("Initialized ResponseCache with 1000 entries, 1 hour TTL");
    }
    
    /**
     * Get cached response
     */
    public CachedResponse get(String query) {
        CachedResponse response = cache.getIfPresent(generateKey(query));
        if (response != null) {
            log.debug("Cache hit for query: {}", query);
        }
        return response;
    }
    
    /**
     * Put response in cache
     */
    public void put(String query, String response, Object metadata) {
        CachedResponse cachedResponse = new CachedResponse(response, metadata);
        cache.put(generateKey(query), cachedResponse);
        log.debug("Cached response for query: {}", query);
    }
    
    /**
     * Clear cache
     */
    public void clear() {
        cache.invalidateAll();
        log.info("Cleared response cache");
    }
    
    /**
     * Get cache stats
     */
    public java.util.Map<String, Object> getStats() {
        var stats = cache.stats();
        java.util.Map<String, Object> result = new java.util.HashMap<>();
        result.put("hit_count", stats.hitCount());
        result.put("miss_count", stats.missCount());
        result.put("hit_rate", stats.hitRate());
        result.put("eviction_count", stats.evictionCount());
        result.put("size", cache.estimatedSize());
        return result;
    }
    
    private String generateKey(String query) {
        return query.toLowerCase().trim();
    }
    
    /**
     * Cached response wrapper
     */
    public static class CachedResponse {
        private final String response;
        private final Object metadata;
        private final long timestamp;
        
        public CachedResponse(String response, Object metadata) {
            this.response = response;
            this.metadata = metadata;
            this.timestamp = System.currentTimeMillis();
        }
        
        public String getResponse() {
            return response;
        }
        
        public Object getMetadata() {
            return metadata;
        }
        
        public long getTimestamp() {
            return timestamp;
        }
    }
}
