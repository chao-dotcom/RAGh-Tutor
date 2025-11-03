#!/bin/bash
set -e

echo "🚀 Starting RAG System..."

# Wait for any dependencies (if needed)
# Add health checks here if you have external services

# Run migrations or setup if needed
if [ "$AUTO_INDEX" = "true" ]; then
    echo "📚 Auto-indexing documents..."
    python scripts/index_documents.py || echo "⚠️  Indexing failed, continuing..."
fi

# Execute the main command
exec "$@"

