#!/usr/bin/env python
"""
Script to index markdown documents from the configured directory.
"""
import os
import argparse
import time
from pathlib import Path
import sys

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indexer import MarkdownIndexer
from src import config


def main():
    """Index documents from the configured directory."""
    parser = argparse.ArgumentParser(description="Index markdown documents for RAG system.")
    parser.add_argument(
        "--markdown-dir",
        type=str,
        help=f"Directory containing markdown files to index (default: {config.MARKDOWN_DIR})",
        default=config.MARKDOWN_DIR
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reindexing even if index already exists"
    )

    args = parser.parse_args()

    # Validate markdown directory
    if not os.path.isdir(args.markdown_dir):
        print(f"Error: Directory not found: {args.markdown_dir}")
        return 1

    print(f"Indexing markdown files from: {args.markdown_dir}")

    # Start timing
    start_time = time.time()

    # Initialize indexer and run indexing
    indexer = MarkdownIndexer(markdown_dir=args.markdown_dir)
    indexer.index_documents(force_reindex=args.force)

    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Indexing completed in {elapsed_time:.2f} seconds.")
    print(f"Index stored at: {config.CHROMA_DB_DIR}")

    return 0


if __name__ == "__main__":
    sys.exit(main())