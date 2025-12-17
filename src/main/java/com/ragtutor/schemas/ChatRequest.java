package com.ragtutor.schemas;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Chat request schema
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatRequest {
    
    @NotBlank
    private String message;
    
    private String conversationId;
    
    @Builder.Default
    private Boolean stream = false;
    
    @Builder.Default
    private Boolean useMemory = true;
}
