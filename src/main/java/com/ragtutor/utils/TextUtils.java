package com.ragtutor.utils;

import lombok.extern.slf4j.Slf4j;

import java.util.ArrayList;
import java.util.List;

/**
 * Text utilities
 */
@Slf4j
public class TextUtils {
    
    /**
     * Truncate text to maximum length
     */
    public static String truncate(String text, int maxLength) {
        if (text == null || text.length() <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength) + "...";
    }
    
    /**
     * Count tokens (rough approximation)
     */
    public static int countTokens(String text) {
        if (text == null || text.isEmpty()) {
            return 0;
        }
        // Rough approximation: 1 token ≈ 4 characters
        return (int) Math.ceil(text.length() / 4.0);
    }
    
    /**
     * Split text into sentences
     */
    public static List<String> splitSentences(String text) {
        if (text == null || text.isEmpty()) {
            return new ArrayList<>();
        }
        
        String[] sentences = text.split("[\\.\\!\\?]+");
        List<String> result = new ArrayList<>();
        
        for (String sentence : sentences) {
            String trimmed = sentence.trim();
            if (!trimmed.isEmpty()) {
                result.add(trimmed);
            }
        }
        
        return result;
    }
    
    /**
     * Clean whitespace
     */
    public static String cleanWhitespace(String text) {
        if (text == null) {
            return null;
        }
        return text.replaceAll("\\s+", " ").trim();
    }
    
    /**
     * Extract keywords (simple implementation)
     */
    public static List<String> extractKeywords(String text, int maxKeywords) {
        if (text == null || text.isEmpty()) {
            return new ArrayList<>();
        }
        
        // Simple word frequency based extraction
        String[] words = text.toLowerCase().split("\\W+");
        java.util.Map<String, Integer> frequency = new java.util.HashMap<>();
        
        for (String word : words) {
            if (word.length() > 3) { // Ignore short words
                frequency.merge(word, 1, Integer::sum);
            }
        }
        
        return frequency.entrySet().stream()
            .sorted(java.util.Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(maxKeywords)
            .map(java.util.Map.Entry::getKey)
            .toList();
    }
}
