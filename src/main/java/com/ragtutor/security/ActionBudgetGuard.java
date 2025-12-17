package com.ragtutor.security;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Action budget guard to prevent abuse
 */
@Slf4j
@Component
public class ActionBudgetGuard {
    
    private final int maxActionsPerSession;
    private final int maxActionsPerMinute;
    private final Map<String, SessionBudget> sessionBudgets;
    
    public ActionBudgetGuard() {
        this.maxActionsPerSession = 10;
        this.maxActionsPerMinute = 20;
        this.sessionBudgets = new ConcurrentHashMap<>();
    }
    
    /**
     * Check if action is allowed for session
     */
    public boolean isAllowed(String sessionId) {
        SessionBudget budget = sessionBudgets.computeIfAbsent(
            sessionId, 
            k -> new SessionBudget()
        );
        
        // Check total actions
        if (budget.totalActions.get() >= maxActionsPerSession) {
            log.warn("Session {} exceeded total action limit", sessionId);
            return false;
        }
        
        // Check actions per minute
        LocalDateTime now = LocalDateTime.now();
        if (budget.lastMinuteStart.plusMinutes(1).isBefore(now)) {
            // Reset minute counter
            budget.lastMinuteStart = now;
            budget.actionsThisMinute.set(0);
        }
        
        if (budget.actionsThisMinute.get() >= maxActionsPerMinute) {
            log.warn("Session {} exceeded rate limit", sessionId);
            return false;
        }
        
        // Increment counters
        budget.totalActions.incrementAndGet();
        budget.actionsThisMinute.incrementAndGet();
        
        return true;
    }
    
    /**
     * Reset budget for session
     */
    public void reset(String sessionId) {
        sessionBudgets.remove(sessionId);
        log.info("Reset action budget for session: {}", sessionId);
    }
    
    /**
     * Session budget tracker
     */
    private static class SessionBudget {
        private final AtomicInteger totalActions = new AtomicInteger(0);
        private final AtomicInteger actionsThisMinute = new AtomicInteger(0);
        private LocalDateTime lastMinuteStart = LocalDateTime.now();
    }
}
