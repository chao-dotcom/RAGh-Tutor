package com.ragtutor.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Application configuration properties
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "app")
public class AppConfig {
    
    // Application Info
    private String version = "1.0.0";
    private String description = "Production-ready RAG System";
    
    // Paths
    private String documentFolder = "./documents";
    private String logFolder = "./logs";
    private String dataFolder = "./data";
    private String auditLogFile = "./logs/audit.log";
    private String feedbackStorage = "./data/feedback";
}
