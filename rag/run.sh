#!/bin/bash
# Helper script for RAG operations

# Default values
MARKDOWN_DIR="../data"

# Function to show usage
show_usage() {
  echo "Usage: $(basename $0) COMMAND [OPTIONS]"
  echo ""
  echo "Commands:"
  echo "  start           Start the RAG system"
  echo "  stop            Stop the RAG system"
  echo "  restart         Restart the RAG system"
  echo "  index           Index markdown documents"
  echo "  query \"TEXT\"    Query the RAG system"
  echo "  status          Show status of the RAG system"
  echo "  logs            Show logs"
  echo ""
  echo "Options:"
  echo "  --markdown-dir DIR   Set the markdown directory (default: $MARKDOWN_DIR)"
  echo "  --force              Force reindexing (with index command)"
  echo "  --help               Show this help"
}

# Parse command line arguments
CMD=""
FORCE=""
QUERY_TEXT=""

while [[ $# -gt 0 ]]; do
  case $1 in
    start|stop|restart|index|query|status|logs)
      CMD="$1"
      shift
      ;;
    --markdown-dir)
      MARKDOWN_DIR="$2"
      shift 2
      ;;
    --force)
      FORCE="--force"
      shift
      ;;
    --help)
      show_usage
      exit 0
      ;;
    *)
      if [[ "$CMD" == "query" && -z "$QUERY_TEXT" ]]; then
        QUERY_TEXT="$1"
        shift
      else
        echo "Unknown option: $1"
        show_usage
        exit 1
      fi
      ;;
  esac
done

# Check if command is provided
if [[ -z "$CMD" ]]; then
  show_usage
  exit 1
fi

# Export markdown directory for docker-compose
export MARKDOWN_DIR

# Execute command
case "$CMD" in
  start)
    echo "Starting RAG system..."
    docker-compose up -d
    ;;
  stop)
    echo "Stopping RAG system..."
    docker-compose down
    ;;
  restart)
    echo "Restarting RAG system..."
    docker-compose restart
    ;;
  index)
    echo "Indexing documents from $MARKDOWN_DIR..."
    docker-compose exec rag python scripts/index_documents.py --markdown-dir /app/markdown_data $FORCE
    ;;
  query)
    if [[ -z "$QUERY_TEXT" ]]; then
      echo "Error: No query text provided"
      show_usage
      exit 1
    fi
    echo "Querying: $QUERY_TEXT"
    docker-compose exec rag python scripts/query.py "$QUERY_TEXT"
    ;;
  status)
    echo "Checking RAG system status..."
    docker-compose ps
    echo ""
    curl -s http://localhost:8000/status | python -m json.tool
    ;;
  logs)
    docker-compose logs -f
    ;;
  *)
    echo "Unknown command: $CMD"
    show_usage
    exit 1
    ;;
esac