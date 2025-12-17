package com.ragtutor.monitoring;

import io.micrometer.tracing.Tracer;
import io.micrometer.tracing.Span;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.function.Supplier;

/**
 * Distributed tracing support
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class TracingService {
    
    private final Tracer tracer;
    
    /**
     * Create a new span
     */
    public Span startSpan(String name) {
        return tracer.nextSpan().name(name).start();
    }
    
    /**
     * Execute with tracing
     */
    public <T> T trace(String spanName, Supplier<T> operation) {
        Span span = startSpan(spanName);
        try {
            return operation.get();
        } catch (Exception e) {
            span.error(e);
            throw e;
        } finally {
            span.end();
        }
    }
    
    /**
     * Execute with tracing (void)
     */
    public void traceVoid(String spanName, Runnable operation) {
        Span span = startSpan(spanName);
        try {
            operation.run();
        } catch (Exception e) {
            span.error(e);
            throw e;
        } finally {
            span.end();
        }
    }
    
    /**
     * Add tag to current span
     */
    public void addTag(String key, String value) {
        Span currentSpan = tracer.currentSpan();
        if (currentSpan != null) {
            currentSpan.tag(key, value);
        }
    }
}
