"""
RAG (Retrieval-Augmented Generation) system for enhancing LLM responses with personal context.
"""

__version__ = "0.1.0"

# Import main components for easy access
from .config import MARKDOWN_DIR, CHROMA_DB_DIR, EMBEDDING_MODEL
from .indexer import MarkdownIndexer
from .query_engine import RAGQueryEngine

# Expose main classes
__all__ = ["MarkdownIndexer", "RAGQueryEngine"]