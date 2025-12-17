package com.ragtutor.processing;

import com.ragtutor.schemas.Document;
import lombok.extern.slf4j.Slf4j;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Document loader for various file types
 */
@Slf4j
@Component
public class DocumentLoader {
    
    public Document loadSingleDocument(String filePath) {
        File file = new File(filePath);
        if (!file.exists()) {
            throw new RuntimeException("File not found: " + filePath);
        }
        
        String docId = UUID.randomUUID().toString();
        String content = extractContent(file);
        
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("source", filePath);
        metadata.put("filename", file.getName());
        metadata.put("file_size", file.length());
        
        return Document.builder()
            .docId(docId)
            .content(content)
            .metadata(metadata)
            .source(filePath)
            .title(file.getName())
            .build();
    }
    
    public List<Document> loadAllDocuments(String directoryPath) {
        List<Document> documents = new ArrayList<>();
        
        try (Stream<Path> paths = Files.walk(Paths.get(directoryPath))) {
            List<Path> files = paths
                .filter(Files::isRegularFile)
                .filter(p -> isSupportedFile(p.toString()))
                .collect(Collectors.toList());
            
            for (Path path : files) {
                try {
                    Document doc = loadSingleDocument(path.toString());
                    documents.add(doc);
                    log.debug("Loaded document: {}", path.getFileName());
                } catch (Exception e) {
                    log.error("Failed to load document: {}", path, e);
                }
            }
        } catch (IOException e) {
            log.error("Failed to walk directory: {}", directoryPath, e);
        }
        
        log.info("Loaded {} documents from {}", documents.size(), directoryPath);
        return documents;
    }
    
    private String extractContent(File file) {
        String filename = file.getName().toLowerCase();
        
        try {
            if (filename.endsWith(".pdf")) {
                return extractPDF(file);
            } else if (filename.endsWith(".txt") || filename.endsWith(".md")) {
                return Files.readString(file.toPath());
            } else {
                // Default to text reading
                return Files.readString(file.toPath());
            }
        } catch (IOException e) {
            log.error("Failed to extract content from: {}", file, e);
            return "";
        }
    }
    
    private String extractPDF(File file) throws IOException {
        try (PDDocument document = PDDocument.load(file)) {
            PDFTextStripper stripper = new PDFTextStripper();
            return stripper.getText(document);
        }
    }
    
    private boolean isSupportedFile(String filename) {
        String lower = filename.toLowerCase();
        return lower.endsWith(".pdf") || 
               lower.endsWith(".txt") || 
               lower.endsWith(".md") ||
               lower.endsWith(".doc") ||
               lower.endsWith(".docx");
    }
}
