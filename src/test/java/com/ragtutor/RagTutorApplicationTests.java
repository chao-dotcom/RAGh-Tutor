package com.ragtutor;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

@SpringBootTest
@TestPropertySource(properties = {
    "llm.openai.api-key=test-key",
    "llm.anthropic.api-key=test-key"
})
class RagTutorApplicationTests {

    @Test
    void contextLoads() {
        // This test verifies that the application context loads successfully
    }
}
