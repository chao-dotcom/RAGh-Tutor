package com.ragtutor.retrieval;

import com.ragtutor.schemas.Chunk;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * In-memory vector store implementation
 * This is a simple implementation using cosine similarity
 * For production, consider using Pinecone, Weaviate, or Qdrant
 */
@Slf4j
@Component
public class InMemoryVectorStore {
    
    private final int dimension;
    private final List<Chunk> chunks;
    private final List<float[]> embeddings;
    private final Map<String, Integer> idToIdx;
    
    public InMemoryVectorStore() {
        this(768); // Default dimension
    }
    
    public InMemoryVectorStore(int dimension) {
        this.dimension = dimension;
        this.chunks = Collections.synchronizedList(new ArrayList<>());
        this.embeddings = Collections.synchronizedList(new ArrayList<>());
        this.idToIdx = new ConcurrentHashMap<>();
        log.info("Initialized InMemoryVectorStore with dimension: {}", dimension);
    }
    
    /**
     * Add embeddings and chunks to store
     */
    public synchronized void add(List<float[]> newEmbeddings, List<Chunk> newChunks) {
        if (newEmbeddings.size() != newChunks.size()) {
            throw new IllegalArgumentException("Number of embeddings must match number of chunks");
        }
        
        int startIdx = chunks.size();
        
        for (int i = 0; i < newChunks.size(); i++) {
            Chunk chunk = newChunks.get(i);
            float[] embedding = newEmbeddings.get(i);
            
            // Normalize embedding for cosine similarity
            float[] normalizedEmbedding = normalize(embedding);
            
            chunks.add(chunk);
            embeddings.add(normalizedEmbedding);
            idToIdx.put(chunk.getChunkId(), startIdx + i);
        }
        
        log.info("Added {} chunks to vector store. Total size: {}", newChunks.size(), chunks.size());
    }
    
    /**
     * Search for most similar chunks
     */
    public List<ChunkWithScore> search(float[] queryEmbedding, int topK) {
        if (chunks.isEmpty()) {
            return Collections.emptyList();
        }
        
        // Normalize query embedding
        float[] normalizedQuery = normalize(queryEmbedding);
        
        // Compute cosine similarities
        List<ChunkWithScore> scoredChunks = new ArrayList<>();
        for (int i = 0; i < embeddings.size(); i++) {
            float similarity = cosineSimilarity(normalizedQuery, embeddings.get(i));
            scoredChunks.add(new ChunkWithScore(chunks.get(i), similarity));
        }
        
        // Sort by score descending and take top K
        return scoredChunks.stream()
            .sorted((a, b) -> Float.compare(b.getScore(), a.getScore()))
            .limit(Math.min(topK, scoredChunks.size()))
            .collect(Collectors.toList());
    }
    
    /**
     * Get chunk by ID
     */
    public Chunk getById(String chunkId) {
        Integer idx = idToIdx.get(chunkId);
        if (idx != null && idx >= 0 && idx < chunks.size()) {
            return chunks.get(idx);
        }
        return null;
    }
    
    /**
     * Save vector store to disk
     */
    public void save(String path) throws IOException {
        File indexFile = new File(path + ".index");
        File chunksFile = new File(path + ".chunks");
        
        // Create parent directories
        indexFile.getParentFile().mkdirs();
        
        // Save embeddings
        try (ObjectOutputStream oos = new ObjectOutputStream(
            new FileOutputStream(indexFile))) {
            oos.writeObject(embeddings);
        }
        
        // Save chunks and metadata
        Map<String, Object> data = new HashMap<>();
        data.put("chunks", chunks);
        data.put("idToIdx", idToIdx);
        data.put("dimension", dimension);
        
        try (ObjectOutputStream oos = new ObjectOutputStream(
            new FileOutputStream(chunksFile))) {
            oos.writeObject(data);
        }
        
        log.info("Saved vector store to {}", path);
    }
    
    /**
     * Load vector store from disk
     */
    @SuppressWarnings("unchecked")
    public void load(String path) throws IOException, ClassNotFoundException {
        File indexFile = new File(path + ".index");
        File chunksFile = new File(path + ".chunks");
        
        if (!indexFile.exists() || !chunksFile.exists()) {
            throw new FileNotFoundException("Vector store files not found at " + path);
        }
        
        // Load embeddings
        try (ObjectInputStream ois = new ObjectInputStream(
            new FileInputStream(indexFile))) {
            List<float[]> loadedEmbeddings = (List<float[]>) ois.readObject();
            embeddings.clear();
            embeddings.addAll(loadedEmbeddings);
        }
        
        // Load chunks and metadata
        try (ObjectInputStream ois = new ObjectInputStream(
            new FileInputStream(chunksFile))) {
            Map<String, Object> data = (Map<String, Object>) ois.readObject();
            List<Chunk> loadedChunks = (List<Chunk>) data.get("chunks");
            Map<String, Integer> loadedIdToIdx = (Map<String, Integer>) data.get("idToIdx");
            
            chunks.clear();
            chunks.addAll(loadedChunks);
            
            idToIdx.clear();
            idToIdx.putAll(loadedIdToIdx);
        }
        
        log.info("Loaded vector store from {} with {} chunks", path, chunks.size());
    }
    
    /**
     * Clear all data
     */
    public synchronized void clear() {
        chunks.clear();
        embeddings.clear();
        idToIdx.clear();
        log.info("Cleared vector store");
    }
    
    /**
     * Get number of chunks in store
     */
    public int size() {
        return chunks.size();
    }
    
    /**
     * Normalize a vector to unit length
     */
    private float[] normalize(float[] vector) {
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
        return vector.clone();
    }
    
    /**
     * Compute cosine similarity between two normalized vectors
     */
    private float cosineSimilarity(float[] vec1, float[] vec2) {
        float dotProduct = 0.0f;
        for (int i = 0; i < vec1.length; i++) {
            dotProduct += vec1[i] * vec2[i];
        }
        return dotProduct;
    }
    
    /**
     * Inner class to hold chunk with score
     */
    public static class ChunkWithScore {
        private final Chunk chunk;
        private final float score;
        
        public ChunkWithScore(Chunk chunk, float score) {
            this.chunk = chunk;
            this.score = score;
        }
        
        public Chunk getChunk() {
            return chunk;
        }
        
        public float getScore() {
            return score;
        }
    }
}
