#!/bin/bash

# Build script for RAG Tutor Java

echo "======================================"
echo "Building RAG Tutor - Java Edition"
echo "======================================"

# Check Java version
echo "Checking Java version..."
java -version

if [ $? -ne 0 ]; then
    echo "❌ Java not found. Please install Java 17 or higher."
    exit 1
fi

# Check Maven
echo "Checking Maven..."
mvn -version

if [ $? -ne 0 ]; then
    echo "❌ Maven not found. Please install Maven 3.6+."
    exit 1
fi

# Clean and build
echo "Cleaning project..."
mvn clean

echo "Building project..."
mvn install -DskipTests

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "Running tests..."
mvn test

if [ $? -ne 0 ]; then
    echo "⚠️  Some tests failed, but build succeeded."
fi

echo ""
echo "======================================"
echo "✅ Build completed successfully!"
echo "======================================"
echo ""
echo "To run the application:"
echo "  mvn spring-boot:run"
echo ""
echo "Or run the JAR:"
echo "  java -jar target/rag-tutor-1.0.0.jar"
echo ""
echo "API will be available at:"
echo "  http://localhost:8000"
echo "  http://localhost:8000/swagger-ui.html"
echo ""
