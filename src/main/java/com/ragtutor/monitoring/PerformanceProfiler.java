package com.ragtutor.monitoring;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Callable;

/**
 * Performance profiler for tracking operation timings
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class PerformanceProfiler {
    
    private final MeterRegistry meterRegistry;
    
    /**
     * Time an operation
     */
    public <T> T time(String operationName, Callable<T> operation) throws Exception {
        Timer.Sample sample = Timer.start(meterRegistry);
        try {
            T result = operation.call();
            sample.stop(Timer.builder("rag.operation.duration")
                .tag("operation", operationName)
                .register(meterRegistry));
            return result;
        } catch (Exception e) {
            sample.stop(Timer.builder("rag.operation.duration")
                .tag("operation", operationName)
                .tag("error", "true")
                .register(meterRegistry));
            throw e;
        }
    }
    
    /**
     * Time an operation (void)
     */
    public void timeVoid(String operationName, Runnable operation) {
        Timer.Sample sample = Timer.start(meterRegistry);
        try {
            operation.run();
            sample.stop(Timer.builder("rag.operation.duration")
                .tag("operation", operationName)
                .register(meterRegistry));
        } catch (Exception e) {
            sample.stop(Timer.builder("rag.operation.duration")
                .tag("operation", operationName)
                .tag("error", "true")
                .register(meterRegistry));
            throw e;
        }
    }
    
    /**
     * Get timing statistics
     */
    public Map<String, Object> getStats() {
        Map<String, Object> stats = new HashMap<>();
        
        meterRegistry.getMeters().stream()
            .filter(meter -> meter.getId().getName().startsWith("rag.operation"))
            .forEach(meter -> {
                String name = meter.getId().getName();
                if (meter instanceof Timer) {
                    Timer timer = (Timer) meter;
                    Map<String, Object> timerStats = new HashMap<>();
                    timerStats.put("count", timer.count());
                    timerStats.put("mean_ms", timer.mean(java.util.concurrent.TimeUnit.MILLISECONDS));
                    timerStats.put("max_ms", timer.max(java.util.concurrent.TimeUnit.MILLISECONDS));
                    stats.put(name, timerStats);
                }
            });
        
        return stats;
    }
}
