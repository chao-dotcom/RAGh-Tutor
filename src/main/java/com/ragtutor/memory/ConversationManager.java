package com.ragtutor.memory;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Manage conversation history and context
 */
@Slf4j
@Component
public class ConversationManager {
    
    private final int maxHistory;
    private final int maxHistoryLength;
    private final int summarizationThreshold;
    private final Map<String, List<Message>> conversations;
    private final Map<String, String> summaries;
    private final ObjectMapper objectMapper;
    
    public ConversationManager() {
        this.maxHistory = 10;
        this.maxHistoryLength = 10;
        this.summarizationThreshold = 20;
        this.conversations = new ConcurrentHashMap<>();
        this.summaries = new ConcurrentHashMap<>();
        this.objectMapper = new ObjectMapper();
        log.info("Initialized ConversationManager");
    }
    
    /**
     * Create a new conversation
     */
    public String createConversation() {
        String conversationId = UUID.randomUUID().toString();
        conversations.put(conversationId, Collections.synchronizedList(new ArrayList<>()));
        log.debug("Created new conversation: {}", conversationId);
        return conversationId;
    }
    
    /**
     * Add a message to conversation
     */
    public void addMessage(
        String conversationId,
        String role,
        String content,
        Map<String, Object> metadata
    ) {
        if (!conversations.containsKey(conversationId)) {
            conversations.put(conversationId, Collections.synchronizedList(new ArrayList<>()));
        }
        
        Message message = new Message();
        message.setRole(role);
        message.setContent(content);
        message.setTimestamp(LocalDateTime.now());
        message.setMetadata(metadata != null ? metadata : new HashMap<>());
        
        List<Message> history = conversations.get(conversationId);
        history.add(message);
        
        // Check if summarization needed (for production, implement async summarization)
        if (history.size() > summarizationThreshold) {
            trimHistory(conversationId);
        }
        
        log.debug("Added {} message to conversation {}", role, conversationId);
    }
    
    /**
     * Add a message without metadata
     */
    public void addMessage(String conversationId, String role, String content) {
        addMessage(conversationId, role, content, null);
    }
    
    /**
     * Get conversation history
     */
    public List<Message> getHistory(String conversationId) {
        return conversations.getOrDefault(conversationId, new ArrayList<>());
    }
    
    /**
     * Get full conversation history
     */
    public List<Message> getFullHistory(String conversationId) {
        return new ArrayList<>(getHistory(conversationId));
    }
    
    /**
     * Get formatted history for prompts
     */
    public List<Map<String, String>> getFormattedHistory(String conversationId) {
        List<Message> history = getHistory(conversationId);
        List<Map<String, String>> formatted = new ArrayList<>();
        
        int startIndex = Math.max(0, history.size() - maxHistory);
        for (int i = startIndex; i < history.size(); i++) {
            Message msg = history.get(i);
            Map<String, String> formattedMsg = new HashMap<>();
            formattedMsg.put(msg.getRole(), msg.getContent());
            formatted.add(formattedMsg);
        }
        
        return formatted;
    }
    
    /**
     * Get conversation context within token limit
     */
    public List<Message> getContext(String conversationId, int maxTokens) {
        if (!conversations.containsKey(conversationId)) {
            return new ArrayList<>();
        }
        
        List<Message> messages = conversations.get(conversationId);
        List<Message> context = new ArrayList<>();
        int totalTokens = 0;
        
        // Start with most recent messages
        for (int i = messages.size() - 1; i >= 0; i--) {
            Message message = messages.get(i);
            // Estimate tokens (rough approximation)
            int messageTokens = (int) (message.getContent().split("\\s+").length * 1.3);
            
            if (totalTokens + messageTokens > maxTokens) {
                break;
            }
            
            context.add(0, message);
            totalTokens += messageTokens;
        }
        
        return context;
    }
    
    /**
     * Clear conversation history
     */
    public void clearHistory(String conversationId) {
        conversations.remove(conversationId);
        summaries.remove(conversationId);
        log.info("Cleared conversation: {}", conversationId);
    }
    
    /**
     * Trim history to max length
     */
    private void trimHistory(String conversationId) {
        List<Message> history = conversations.get(conversationId);
        if (history != null && history.size() > maxHistoryLength * 2) {
            List<Message> trimmed = new ArrayList<>(
                history.subList(history.size() - maxHistoryLength, history.size())
            );
            conversations.put(conversationId, Collections.synchronizedList(trimmed));
            log.debug("Trimmed conversation {} to {} messages", conversationId, trimmed.size());
        }
    }
    
    /**
     * Message data class
     */
    @Data
    public static class Message {
        private String role;
        private String content;
        private LocalDateTime timestamp;
        private Map<String, Object> metadata;
    }
}
