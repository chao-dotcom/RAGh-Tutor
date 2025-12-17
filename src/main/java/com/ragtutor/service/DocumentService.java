package com.ragtutor.service;

import com.ragtutor.chunking.DocumentChunker;
import com.ragtutor.config.AppConfig;
import com.ragtutor.embedding.EmbeddingModelService;
import com.ragtutor.processing.DocumentLoader;
import com.ragtutor.retrieval.InMemoryVectorStore;
import com.ragtutor.schemas.Chunk;
import com.ragtutor.schemas.Document;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

/**
 * Document processing and indexing service
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DocumentService {
    
    private final InMemoryVectorStore vectorStore;
    private final EmbeddingModelService embeddingModel;
    private final DocumentChunker documentChunker;
    private final DocumentLoader documentLoader;
    private final AppConfig appConfig;
    
    public Map<String, Object> uploadAndIndexDocument(MultipartFile file) throws IOException {
        // Save file
        String documentsPath = appConfig.getDocumentFolder();
        Path dirPath = Paths.get(documentsPath);
        Files.createDirectories(dirPath);
        
        Path filePath = dirPath.resolve(file.getOriginalFilename());
        file.transferTo(filePath.toFile());
        
        log.info("Saved uploaded file: {}", filePath);
        
        try {
            // Load document
            Document document = documentLoader.loadSingleDocument(filePath.toString());
            
            // Chunk document
            List<Chunk> chunks = documentChunker.chunkDocument(document);
            
            // Generate embeddings
            List<String> texts = new ArrayList<>();
            for (Chunk chunk : chunks) {
                texts.add(chunk.getContent());
            }
            List<float[]> embeddings = embeddingModel.encode(texts);
            
            // Add to vector store
            vectorStore.add(embeddings, chunks);
            
            Map<String, Object> result = new HashMap<>();
            result.put("status", "success");
            result.put("filename", file.getOriginalFilename());
            result.put("chunks_created", chunks.size());
            result.put("total_chunks", vectorStore.size());
            
            log.info("Indexed document: {} with {} chunks", file.getOriginalFilename(), chunks.size());
            return result;
        } catch (Exception e) {
            log.error("Failed to index document", e);
            throw new RuntimeException("Failed to index document: " + e.getMessage(), e);
        }
    }
    
    public Map<String, Object> indexAllDocuments() {
        // Clear existing
        vectorStore.clear();
        
        String documentsPath = appConfig.getDocumentFolder();
        
        // Load all documents
        List<Document> documents = documentLoader.loadAllDocuments(documentsPath);
        
        // Chunk all documents
        List<Chunk> allChunks = new ArrayList<>();
        for (Document doc : documents) {
            List<Chunk> chunks = documentChunker.chunkDocument(doc);
            allChunks.addAll(chunks);
        }
        
        // Generate embeddings
        List<String> texts = new ArrayList<>();
        for (Chunk chunk : allChunks) {
            texts.add(chunk.getContent());
        }
        List<float[]> embeddings = embeddingModel.encode(texts);
        
        // Add to vector store
        vectorStore.add(embeddings, allChunks);
        
        // Save vector store
        try {
            String vectorStorePath = appConfig.getDataFolder() + "/vector_store";
            vectorStore.save(vectorStorePath);
        } catch (IOException e) {
            log.error("Failed to save vector store", e);
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("status", "success");
        result.put("documents", documents.size());
        result.put("chunks", allChunks.size());
        result.put("vector_store_size", vectorStore.size());
        
        log.info("Indexed {} documents with {} chunks", documents.size(), allChunks.size());
        return result;
    }
}
