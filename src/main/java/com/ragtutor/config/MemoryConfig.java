package com.ragtutor.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Memory/conversation configuration
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "memory")
public class MemoryConfig {
    
    private int maxContextLength = 4000;
    private boolean enabled = true;
    private int maxHistoryLength = 10;
    private int summarizationThreshold = 20;
}
