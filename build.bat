@echo off
REM Build script for RAG Tutor Java (Windows)

echo ======================================
echo Building RAG Tutor - Java Edition
echo ======================================

REM Check Java version
echo Checking Java version...
java -version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Java not found. Please install Java 17 or higher.
    exit /b 1
)

REM Check Maven
echo Checking Maven...
mvn -version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Maven not found. Please install Maven 3.6+
    exit /b 1
)

REM Clean and build
echo Cleaning project...
call mvn clean

echo Building project...
call mvn install -DskipTests

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed!
    exit /b 1
)

echo Running tests...
call mvn test

if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Some tests failed, but build succeeded.
)

echo.
echo ======================================
echo Build completed successfully!
echo ======================================
echo.
echo To run the application:
echo   mvn spring-boot:run
echo.
echo Or run the JAR:
echo   java -jar target\rag-tutor-1.0.0.jar
echo.
echo API will be available at:
echo   http://localhost:8000
echo   http://localhost:8000/swagger-ui.html
echo.
