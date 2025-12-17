package com.ragtutor.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Security configuration properties
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "security")
public class SecurityConfig {
    
    private RateLimitConfig rateLimit = new RateLimitConfig();
    private ContentModerationConfig contentModeration = new ContentModerationConfig();
    private boolean piiDetectionEnabled = true;
    
    @Data
    public static class RateLimitConfig {
        private boolean enabled = true;
        private int requests = 100;
        private int window = 60;
    }
    
    @Data
    public static class ContentModerationConfig {
        private boolean enabled = true;
    }
}
