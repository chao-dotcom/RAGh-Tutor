package com.ragtutor.security;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;
import java.util.regex.Pattern;

/**
 * Content moderation service
 */
@Slf4j
@Component
public class ContentModerator {
    
    private final List<String> bannedWords;
    private final List<Pattern> bannedPatterns;
    
    public ContentModerator() {
        // Initialize with some basic banned content
        this.bannedWords = Arrays.asList(
            "spam", "hack", "exploit"
        );
        
        this.bannedPatterns = Arrays.asList(
            Pattern.compile("\\b(viagra|cialis)\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\b(password|pwd)\\s*:\\s*\\w+", Pattern.CASE_INSENSITIVE)
        );
    }
    
    /**
     * Check if content is safe
     * @return true if safe, false if contains violations
     */
    public boolean isSafe(String content) {
        CheckResult result = checkContent(content);
        return result.isSafe();
    }
    
    /**
     * Check content and return detailed result
     */
    public CheckResult checkContent(String content) {
        if (content == null || content.trim().isEmpty()) {
            return new CheckResult(true, null);
        }
        
        String lowerContent = content.toLowerCase();
        
        // Check banned words
        for (String word : bannedWords) {
            if (lowerContent.contains(word)) {
                log.warn("Content contains banned word: {}", word);
                return new CheckResult(false, "Content contains prohibited words");
            }
        }
        
        // Check patterns
        for (Pattern pattern : bannedPatterns) {
            if (pattern.matcher(content).find()) {
                log.warn("Content matches banned pattern");
                return new CheckResult(false, "Content matches prohibited pattern");
            }
        }
        
        return new CheckResult(true, null);
    }
    
    /**
     * Result of content check
     */
    public static class CheckResult {
        private final boolean safe;
        private final String reason;
        
        public CheckResult(boolean safe, String reason) {
            this.safe = safe;
            this.reason = reason;
        }
        
        public boolean isSafe() {
            return safe;
        }
        
        public String getReason() {
            return reason;
        }
    }
}
