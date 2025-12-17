package com.ragtutor.embedding;

import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;

/**
 * Wrapper for embedding model with batching support
 */
@Slf4j
@Component
public class EmbeddingModelService {
    
    private final EmbeddingModel embeddingModel;
    private final int dimension;
    private final ExecutorService executorService;
    
    public EmbeddingModelService() {
        log.info("Initializing embedding model...");
        this.embeddingModel = new AllMiniLmL6V2EmbeddingModel();
        this.dimension = 384; // AllMiniLmL6V2 dimension
        this.executorService = Executors.newFixedThreadPool(
            Runtime.getRuntime().availableProcessors()
        );
        log.info("Embedding model initialized with dimension: {}", dimension);
    }
    
    /**
     * Generate embeddings for a list of texts
     */
    public List<float[]> encode(List<String> texts) {
        return encode(texts, 32);
    }
    
    /**
     * Generate embeddings for a list of texts with batch size
     */
    public List<float[]> encode(List<String> texts, int batchSize) {
        List<float[]> allEmbeddings = new ArrayList<>();
        
        // Process in batches
        for (int i = 0; i < texts.size(); i += batchSize) {
            int end = Math.min(i + batchSize, texts.size());
            List<String> batch = texts.subList(i, end);
            
            List<Embedding> embeddings = embeddingModel.embedAll(batch).content();
            
            for (Embedding embedding : embeddings) {
                allEmbeddings.add(embedding.vector());
            }
        }
        
        return allEmbeddings;
    }
    
    /**
     * Generate embedding for a single text
     */
    public float[] encodeSingle(String text) {
        Embedding embedding = embeddingModel.embed(text).content();
        return embedding.vector();
    }
    
    /**
     * Async wrapper for encoding
     */
    public CompletableFuture<List<float[]>> encodeAsync(List<String> texts) {
        return CompletableFuture.supplyAsync(() -> encode(texts), executorService);
    }
    
    /**
     * Async wrapper for encoding with batch size
     */
    public CompletableFuture<List<float[]>> encodeAsync(List<String> texts, int batchSize) {
        return CompletableFuture.supplyAsync(() -> encode(texts, batchSize), executorService);
    }
    
    /**
     * Get embedding dimension
     */
    public int getDimension() {
        return dimension;
    }
    
    /**
     * Normalize a vector to unit length
     */
    public static float[] normalize(float[] vector) {
        float norm = 0.0f;
        for (float v : vector) {
            norm += v * v;
        }
        norm = (float) Math.sqrt(norm);
        
        if (norm > 0) {
            float[] normalized = new float[vector.length];
            for (int i = 0; i < vector.length; i++) {
                normalized[i] = vector[i] / norm;
            }
            return normalized;
        }
        return vector;
    }
    
    /**
     * Compute cosine similarity between two vectors
     */
    public static float cosineSimilarity(float[] vec1, float[] vec2) {
        if (vec1.length != vec2.length) {
            throw new IllegalArgumentException("Vectors must have same dimension");
        }
        
        float dotProduct = 0.0f;
        float norm1 = 0.0f;
        float norm2 = 0.0f;
        
        for (int i = 0; i < vec1.length; i++) {
            dotProduct += vec1[i] * vec2[i];
            norm1 += vec1[i] * vec1[i];
            norm2 += vec2[i] * vec2[i];
        }
        
        return dotProduct / (float) (Math.sqrt(norm1) * Math.sqrt(norm2));
    }
    
    public void shutdown() {
        executorService.shutdown();
    }
}
