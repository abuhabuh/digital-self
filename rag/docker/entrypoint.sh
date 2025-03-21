#!/bin/bash
set -e

# Create any required directories
mkdir -p /app/data/chroma
mkdir -p /app/markdown_data

# Command dispatcher
case "$1" in
  api)
    echo "Starting RAG API server..."
    exec python -m src.api
    ;;
  index)
    echo "Indexing documents..."
    shift
    exec python scripts/index_documents.py "$@"
    ;;
  query)
    echo "Querying RAG system..."
    shift
    exec python scripts/query.py "$@"
    ;;
  shell)
    echo "Starting shell..."
    exec /bin/bash
    ;;
  *)
    echo "Running custom command: $@"
    exec "$@"
    ;;
esac