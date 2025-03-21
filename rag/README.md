# RAG (Retrieval-Augmented Generation) System

This directory contains a RAG system that indexes and retrieves information from markdown files to enhance LLM responses with personal context.

## Overview

The RAG system uses LlamaIndex to:
1. Index markdown files from a configurable directory
2. Store embeddings in a ChromaDB vector database
3. Retrieve relevant information to enhance LLM responses

## Project Structure

```
rag/
├── data/                 # Storage for indexed data
├── docker/               # Docker configuration files
├── scripts/              # Utility scripts
├── src/                  # Core implementation
│   ├── indexer.py        # Document indexing functionality
│   ├── query_engine.py   # Retrieval and query functionality
│   └── config.py         # Configuration management
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker container orchestration
└── requirements.txt      # Python dependencies
```

## Setup and Usage

### Configuration

Configure the system by modifying the settings in `src/config.py` or by setting environment variables:

- `MARKDOWN_DIR`: Path to directory containing markdown files to index
- `CHROMA_DB_DIR`: Path to store the ChromaDB database (default: `./data/chroma`)
- `EMBEDDING_MODEL`: Embedding model to use (default: `sentence-transformers/all-mpnet-base-v2`)

### Running with Docker

1. Build and start the containers:
   ```
   docker-compose up -d
   ```

2. Index documents:
   ```
   docker-compose exec rag python scripts/index_documents.py
   ```

3. Query the system:
   ```
   docker-compose exec rag python scripts/query.py "Your query here"
   ```

### Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Index documents:
   ```
   python scripts/index_documents.py
   ```

3. Query the system:
   ```
   python scripts/query.py "Your query here"
   ```

## Customization

- Add custom preprocessing steps in `src/indexer.py`
- Modify retrieval parameters in `src/query_engine.py`
- Extend with additional data sources by adding new indexers
