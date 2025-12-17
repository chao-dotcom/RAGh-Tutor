package com.ragtutor.generation;

import com.ragtutor.config.LLMConfig;
import com.theokanning.openai.completion.chat.ChatCompletionRequest;
import com.theokanning.openai.completion.chat.ChatMessage;
import com.theokanning.openai.service.OpenAiService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Flux;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

/**
 * LLM client for various providers
 */
@Slf4j
@Component
public class LLMClient {
    
    private final String provider;
    private final String model;
    private final double temperature;
    private final int maxTokens;
    private final OpenAiService openAiService;
    
    public LLMClient(LLMConfig config) {
        this.provider = config.getProvider();
        this.temperature = config.getTemperature();
        this.maxTokens = config.getMaxTokens();
        
        if ("openai".equalsIgnoreCase(provider)) {
            this.model = config.getOpenai().getModel();
            String apiKey = config.getOpenai().getApiKey();
            if (apiKey == null || apiKey.isEmpty()) {
                apiKey = System.getenv("OPENAI_API_KEY");
            }
            this.openAiService = new OpenAiService(apiKey, Duration.ofSeconds(60));
            log.info("Initialized OpenAI LLM client with model: {}", model);
        } else if ("anthropic".equalsIgnoreCase(provider)) {
            this.model = config.getAnthropic().getModel();
            this.openAiService = null;
            log.warn("Anthropic provider not yet fully implemented");
            // TODO: Implement Anthropic client
        } else {
            this.model = null;
            this.openAiService = null;
            throw new IllegalArgumentException("Unsupported provider: " + provider);
        }
    }
    
    /**
     * Generate completion (non-streaming)
     */
    public String generate(String prompt, String system) {
        return generate(prompt, system, null, null, null);
    }
    
    /**
     * Generate completion with custom parameters
     */
    public String generate(
        String prompt,
        String system,
        Double temperature,
        Integer maxTokens,
        List<String> stopSequences
    ) {
        if ("openai".equalsIgnoreCase(provider)) {
            return generateOpenAI(prompt, system, temperature, maxTokens, stopSequences);
        } else {
            throw new UnsupportedOperationException("Provider not implemented: " + provider);
        }
    }
    
    /**
     * Generate completion asynchronously
     */
    public CompletableFuture<String> generateAsync(String prompt, String system) {
        return CompletableFuture.supplyAsync(() -> generate(prompt, system));
    }
    
    /**
     * Generate completion with streaming (reactive)
     */
    public Flux<String> generateStream(String prompt, String system) {
        return Flux.create(sink -> {
            try {
                List<ChatMessage> messages = new ArrayList<>();
                if (system != null && !system.isEmpty()) {
                    messages.add(new ChatMessage("system", system));
                }
                messages.add(new ChatMessage("user", prompt));
                
                ChatCompletionRequest request = ChatCompletionRequest.builder()
                    .model(model)
                    .messages(messages)
                    .temperature(temperature)
                    .maxTokens(maxTokens)
                    .stream(true)
                    .build();
                
                openAiService.streamChatCompletion(request)
                    .doOnError(sink::error)
                    .doOnComplete(sink::complete)
                    .blockingForEach(chunk -> {
                        if (chunk.getChoices() != null && !chunk.getChoices().isEmpty()) {
                            String content = chunk.getChoices().get(0).getMessage().getContent();
                            if (content != null) {
                                sink.next(content);
                            }
                        }
                    });
            } catch (Exception e) {
                sink.error(e);
            }
        });
    }
    
    /**
     * OpenAI specific implementation
     */
    private String generateOpenAI(
        String prompt,
        String system,
        Double temperature,
        Integer maxTokens,
        List<String> stopSequences
    ) {
        List<ChatMessage> messages = new ArrayList<>();
        if (system != null && !system.isEmpty()) {
            messages.add(new ChatMessage("system", system));
        }
        messages.add(new ChatMessage("user", prompt));
        
        ChatCompletionRequest.ChatCompletionRequestBuilder builder = ChatCompletionRequest.builder()
            .model(model)
            .messages(messages)
            .temperature(temperature != null ? temperature : this.temperature)
            .maxTokens(maxTokens != null ? maxTokens : this.maxTokens);
        
        if (stopSequences != null && !stopSequences.isEmpty()) {
            builder.stop(stopSequences);
        }
        
        try {
            var completion = openAiService.createChatCompletion(builder.build());
            return completion.getChoices().get(0).getMessage().getContent();
        } catch (Exception e) {
            log.error("OpenAI API error", e);
            throw new RuntimeException("Failed to generate completion: " + e.getMessage(), e);
        }
    }
    
    public String getModel() {
        return model;
    }
    
    public String getProvider() {
        return provider;
    }
}
