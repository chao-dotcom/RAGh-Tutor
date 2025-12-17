package com.ragtutor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * Main application entry point for RAG Tutor System
 */
@SpringBootApplication
@EnableConfigurationProperties
@EnableCaching
@EnableAsync
public class RagTutorApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(RagTutorApplication.class, args);
    }
}
