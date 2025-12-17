package com.ragtutor.controller;

import com.ragtutor.config.AppConfig;
import com.ragtutor.schemas.*;
import com.ragtutor.service.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import reactor.core.publisher.Flux;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Main REST controller for RAG Tutor API
 */
@Slf4j
@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
@Tag(name = "RAG Tutor API", description = "Production-ready RAG System API")
public class RagController {
    
    private final QueryService queryService;
    private final DocumentService documentService;
    private final ConversationService conversationService;
    private final FeedbackService feedbackService;
    private final HealthService healthService;
    private final MetricsService metricsService;
    private final AppConfig appConfig;
    
    @GetMapping("/health")
    @Operation(summary = "Health check endpoint")
    public ResponseEntity<HealthResponse> healthCheck() {
        try {
            HealthResponse health = healthService.checkHealth();
            return ResponseEntity.ok(health);
        } catch (Exception e) {
            log.error("Health check failed", e);
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(HealthResponse.builder()
                    .status("unhealthy")
                    .version(appConfig.getVersion())
                    .build());
        }
    }
    
    @GetMapping("/ready")
    @Operation(summary = "Readiness check for Kubernetes")
    public ResponseEntity<Map<String, String>> readinessCheck() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "ready");
        return ResponseEntity.ok(response);
    }
    
    @PostMapping("/query")
    @Operation(summary = "Non-streaming query endpoint")
    public ResponseEntity<QueryResponse> query(@Valid @RequestBody QueryRequest request) {
        try {
            String sessionId = request.getSessionId() != null ? 
                request.getSessionId() : UUID.randomUUID().toString();
            
            QueryResponse response = queryService.processQuery(request, sessionId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Query processing failed", e);
            throw new RuntimeException("Query processing failed: " + e.getMessage(), e);
        }
    }
    
    @PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    @Operation(summary = "Streaming query endpoint with SSE")
    public SseEmitter streamQuery(@Valid @RequestBody QueryRequest request) {
        String sessionId = request.getSessionId() != null ? 
            request.getSessionId() : UUID.randomUUID().toString();
        
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);
        
        queryService.processQueryStreaming(request, sessionId, emitter);
        
        return emitter;
    }
    
    @PostMapping("/query/multi-document")
    @Operation(summary = "Query multiple specific documents")
    public ResponseEntity<QueryResponse> multiDocumentQuery(
        @Valid @RequestBody MultiDocumentQueryRequest request) {
        try {
            QueryResponse response = queryService.processMultiDocumentQuery(request);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Multi-document query failed", e);
            throw new RuntimeException("Multi-document query failed: " + e.getMessage(), e);
        }
    }
    
    @PostMapping("/feedback")
    @Operation(summary = "Submit user feedback")
    public ResponseEntity<Map<String, String>> submitFeedback(
        @Valid @RequestBody FeedbackRequest request) {
        try {
            feedbackService.recordFeedback(request);
            Map<String, String> response = new HashMap<>();
            response.put("status", "feedback_recorded");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Feedback submission failed", e);
            throw new RuntimeException("Feedback submission failed: " + e.getMessage(), e);
        }
    }
    
    @GetMapping("/feedback/stats")
    @Operation(summary = "Get feedback statistics")
    public ResponseEntity<Map<String, Object>> getFeedbackStats() {
        Map<String, Object> stats = feedbackService.getStatistics();
        return ResponseEntity.ok(stats);
    }
    
    @PostMapping("/documents/upload")
    @Operation(summary = "Upload and index a new document")
    public ResponseEntity<Map<String, Object>> uploadDocument(
        @RequestParam("file") MultipartFile file) {
        try {
            Map<String, Object> result = documentService.uploadAndIndexDocument(file);
            return ResponseEntity.ok(result);
        } catch (IOException e) {
            log.error("Document upload failed", e);
            throw new RuntimeException("Document upload failed: " + e.getMessage(), e);
        }
    }
    
    @PostMapping("/index")
    @Operation(summary = "Index all documents from documents folder")
    public ResponseEntity<Map<String, Object>> indexDocuments() {
        try {
            Map<String, Object> result = documentService.indexAllDocuments();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("Document indexing failed", e);
            throw new RuntimeException("Document indexing failed: " + e.getMessage(), e);
        }
    }
    
    @GetMapping("/conversation/{sessionId}/history")
    @Operation(summary = "Get conversation history")
    public ResponseEntity<Map<String, Object>> getConversationHistory(
        @PathVariable String sessionId) {
        Map<String, Object> history = conversationService.getHistory(sessionId);
        return ResponseEntity.ok(history);
    }
    
    @DeleteMapping("/conversation/{sessionId}")
    @Operation(summary = "Clear conversation history")
    public ResponseEntity<Map<String, String>> clearConversation(
        @PathVariable String sessionId) {
        conversationService.clearHistory(sessionId);
        Map<String, String> response = new HashMap<>();
        response.put("status", "cleared");
        response.put("session_id", sessionId);
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/metrics")
    @Operation(summary = "Get system metrics")
    public ResponseEntity<Map<String, Object>> getMetrics() {
        Map<String, Object> metrics = metricsService.getAllMetrics();
        return ResponseEntity.ok(metrics);
    }
    
    @GetMapping(value = "/metrics/prometheus", produces = "text/plain")
    @Operation(summary = "Prometheus metrics endpoint")
    public ResponseEntity<String> prometheusMetrics() {
        String metrics = metricsService.exportPrometheusMetrics();
        return ResponseEntity.ok(metrics);
    }
    
    @GetMapping("/health/detailed")
    @Operation(summary = "Detailed health check with all component status")
    public ResponseEntity<Map<String, Object>> detailedHealthCheck() {
        Map<String, Object> health = healthService.checkDetailedHealth();
        return ResponseEntity.ok(health);
    }
    
    @PostMapping("/chat")
    @Operation(summary = "Chat endpoint with conversation memory")
    public ResponseEntity<QueryResponse> chat(@Valid @RequestBody ChatRequest request) {
        try {
            QueryResponse response = queryService.processChat(request);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Chat processing failed", e);
            throw new RuntimeException("Chat processing failed: " + e.getMessage(), e);
        }
    }
}
