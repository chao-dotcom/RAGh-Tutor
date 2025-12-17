package com.ragtutor.config;

import com.ragtutor.service.InitializationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

/**
 * Application startup listener
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class ApplicationStartupListener {
    
    private final InitializationService initializationService;
    
    @EventListener(ApplicationReadyEvent.class)
    public void onApplicationReady() {
        log.info("Application is ready!");
        initializationService.initialize();
        
        log.info("=".repeat(60));
        log.info("RAG Tutor Application Started Successfully!");
        log.info("API Documentation: http://localhost:8000/swagger-ui.html");
        log.info("Health Check: http://localhost:8000/api/v1/health");
        log.info("Metrics: http://localhost:8000/actuator/metrics");
        log.info("=".repeat(60));
    }
}
