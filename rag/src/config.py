"""
Configuration management for the RAG system.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Base directories
ROOT_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = os.path.join(ROOT_DIR, "data")

# Directory containing markdown files to index
# This can be overridden by setting the MARKDOWN_DIR environment variable
MARKDOWN_DIR = os.environ.get(
    "MARKDOWN_DIR",
    os.path.join(ROOT_DIR, "../data")  # Default to data directory at repo root
)

# Directory for ChromaDB storage
CHROMA_DB_DIR = os.environ.get(
    "CHROMA_DB_DIR",
    os.path.join(DATA_DIR, "chroma")
)

# Ensure data directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# Embedding model configuration
EMBEDDING_MODEL = os.environ.get(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-mpnet-base-v2"
)

# Chunk size for text splitting
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "100"))

# Number of results to return in queries
TOP_K = int(os.environ.get("TOP_K", "5"))

# API configuration
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "8000"))