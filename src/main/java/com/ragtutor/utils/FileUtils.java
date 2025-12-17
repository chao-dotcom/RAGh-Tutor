package com.ragtutor.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * File utilities
 */
@Slf4j
public class FileUtils {
    
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    /**
     * Ensure directory exists
     */
    public static void ensureDirectoryExists(String path) {
        try {
            Path dirPath = Paths.get(path);
            if (!Files.exists(dirPath)) {
                Files.createDirectories(dirPath);
                log.info("Created directory: {}", path);
            }
        } catch (IOException e) {
            log.error("Failed to create directory: {}", path, e);
            throw new RuntimeException("Failed to create directory: " + path, e);
        }
    }
    
    /**
     * Read JSON file
     */
    public static <T> T readJson(String filePath, Class<T> clazz) {
        try {
            Path path = Paths.get(filePath);
            String content = Files.readString(path);
            return objectMapper.readValue(content, clazz);
        } catch (IOException e) {
            log.error("Failed to read JSON file: {}", filePath, e);
            throw new RuntimeException("Failed to read JSON file: " + filePath, e);
        }
    }
    
    /**
     * Write JSON file
     */
    public static void writeJson(String filePath, Object object) {
        try {
            Path path = Paths.get(filePath);
            ensureDirectoryExists(path.getParent().toString());
            String json = objectMapper.writerWithDefaultPrettyPrinter()
                .writeValueAsString(object);
            Files.writeString(path, json);
        } catch (IOException e) {
            log.error("Failed to write JSON file: {}", filePath, e);
            throw new RuntimeException("Failed to write JSON file: " + filePath, e);
        }
    }
    
    /**
     * Get file extension
     */
    public static String getExtension(String filename) {
        if (filename == null || filename.isEmpty()) {
            return "";
        }
        int lastDot = filename.lastIndexOf('.');
        if (lastDot == -1) {
            return "";
        }
        return filename.substring(lastDot + 1).toLowerCase();
    }
    
    /**
     * Get file size in MB
     */
    public static double getFileSizeMB(String filePath) {
        try {
            Path path = Paths.get(filePath);
            long bytes = Files.size(path);
            return bytes / (1024.0 * 1024.0);
        } catch (IOException e) {
            log.error("Failed to get file size: {}", filePath, e);
            return 0;
        }
    }
}
