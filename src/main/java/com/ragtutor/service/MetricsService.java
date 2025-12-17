package com.ragtutor.service;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Timer;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

/**
 * Metrics collection service
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class MetricsService {
    
    private final MeterRegistry meterRegistry;
    
    public Map<String, Object> getAllMetrics() {
        Map<String, Object> metrics = new HashMap<>();
        
        // Collect all meters
        meterRegistry.getMeters().forEach(meter -> {
            String name = meter.getId().getName();
            
            if (meter instanceof Counter) {
                Counter counter = (Counter) meter;
                metrics.put(name, counter.count());
            } else if (meter instanceof Timer) {
                Timer timer = (Timer) meter;
                metrics.put(name + ".count", timer.count());
                metrics.put(name + ".mean", timer.mean());
                metrics.put(name + ".max", timer.max());
            }
        });
        
        return metrics;
    }
    
    public String exportPrometheusMetrics() {
        // Prometheus format is handled automatically by micrometer
        // This is a placeholder - actual export is done by Spring Boot Actuator
        return "# Metrics exported via /actuator/prometheus endpoint";
    }
    
    public void recordQuery(long durationMs) {
        Timer.builder("rag.query.duration")
            .description("Query processing duration")
            .register(meterRegistry)
            .record(java.time.Duration.ofMillis(durationMs));
        
        Counter.builder("rag.query.total")
            .description("Total queries processed")
            .register(meterRegistry)
            .increment();
    }
    
    public void recordError(String errorType) {
        Counter.builder("rag.errors")
            .tag("type", errorType)
            .description("Total errors")
            .register(meterRegistry)
            .increment();
    }
}
