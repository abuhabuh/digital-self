"""
FastAPI service for the RAG system.
"""
import os
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from src.query_engine import RAGQueryEngine
from src.indexer import MarkdownIndexer
from src import config


# Initialize FastAPI app
app = FastAPI(
    title="RAG API",
    description="API for querying the RAG system",
    version="1.0.0",
)

# Initialize query engine
query_engine = None

class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    documents_only: bool = False

class IndexRequest(BaseModel):
    """Index request model."""
    markdown_dir: Optional[str] = None
    force: bool = False


@app.on_event("startup")
async def startup_event():
    """Initialize the query engine on startup."""
    global query_engine
    query_engine = RAGQueryEngine()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "RAG API is running"}


@app.post("/query")
async def query(request: QueryRequest) -> Dict[str, Any]:
    """
    Query the RAG system.

    Args:
        request: Query request.

    Returns:
        Query results.
    """
    global query_engine

    if query_engine is None:
        query_engine = RAGQueryEngine()

    if request.documents_only:
        return {
            "query": request.query,
            "documents": query_engine.get_relevant_documents(request.query)
        }
    else:
        return query_engine.query(request.query)


@app.post("/index")
async def index(request: IndexRequest) -> Dict[str, Any]:
    """
    Index markdown documents.

    Args:
        request: Index request.

    Returns:
        Indexing results.
    """
    global query_engine

    markdown_dir = request.markdown_dir or config.MARKDOWN_DIR

    if not os.path.isdir(markdown_dir):
        raise HTTPException(status_code=400, detail=f"Directory not found: {markdown_dir}")

    # Initialize indexer
    indexer = MarkdownIndexer(markdown_dir=markdown_dir)

    # Index documents
    index = indexer.index_documents(force_reindex=request.force)

    # Get document count
    document_count = indexer.chroma_collection.count()

    # Reinitialize query engine
    query_engine = RAGQueryEngine(index=index)

    return {
        "status": "success",
        "message": f"Indexed documents from {markdown_dir}",
        "document_count": document_count
    }


@app.get("/status")
async def status() -> Dict[str, Any]:
    """
    Get system status.

    Returns:
        System status information.
    """
    indexer = MarkdownIndexer()
    doc_count = indexer.chroma_collection.count()

    return {
        "status": "running",
        "documents_indexed": doc_count,
        "markdown_dir": config.MARKDOWN_DIR,
        "database_dir": config.CHROMA_DB_DIR,
        "embedding_model": config.EMBEDDING_MODEL,
    }


def start():
    """Start the API server."""
    import uvicorn
    uvicorn.run(
        "src.api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )


if __name__ == "__main__":
    start()