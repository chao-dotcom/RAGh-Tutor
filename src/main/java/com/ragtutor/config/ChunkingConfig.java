package com.ragtutor.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Chunking configuration
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "chunking")
public class ChunkingConfig {
    
    private int size = 800;
    private int overlap = 200;
    private String separator = "\n\n";
}
