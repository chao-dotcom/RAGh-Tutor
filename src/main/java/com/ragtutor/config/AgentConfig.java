package com.ragtutor.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Agent configuration
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "agent")
public class AgentConfig {
    
    private int maxIterations = 5;
    private int maxActionsPerSession = 10;
    private int maxActionsPerMinute = 20;
}
