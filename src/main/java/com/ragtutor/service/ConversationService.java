package com.ragtutor.service;

import com.ragtutor.memory.ConversationManager;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Conversation service
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ConversationService {
    
    private final ConversationManager conversationManager;
    
    public Map<String, Object> getHistory(String sessionId) {
        List<ConversationManager.Message> history = conversationManager.getFullHistory(sessionId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("session_id", sessionId);
        response.put("history", history);
        response.put("count", history.size());
        
        return response;
    }
    
    public void clearHistory(String sessionId) {
        conversationManager.clearHistory(sessionId);
        log.info("Cleared conversation history for session: {}", sessionId);
    }
}
