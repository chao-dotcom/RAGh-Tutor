package com.ragtutor.schemas;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Feedback request schema
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FeedbackRequest {
    
    @NotBlank
    private String query;
    
    @NotBlank
    private String response;
    
    private Integer rating;
    
    private String feedback;
    
    private String sessionId;
}
