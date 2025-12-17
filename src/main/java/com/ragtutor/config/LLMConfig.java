package com.ragtutor.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * LLM client configuration
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "llm")
public class LLMConfig {
    
    private String provider = "openai";
    private OpenAIConfig openai = new OpenAIConfig();
    private AnthropicConfig anthropic = new AnthropicConfig();
    private double temperature = 0.7;
    private int maxTokens = 2000;
    
    @Data
    public static class OpenAIConfig {
        private String apiKey;
        private String model = "gpt-4";
    }
    
    @Data
    public static class AnthropicConfig {
        private String apiKey;
        private String model = "claude-3-opus-20240229";
    }
}
