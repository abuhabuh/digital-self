#!/usr/bin/env python
"""
Script to query the RAG system.
"""
import argparse
import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.query_engine import RAGQueryEngine


def main():
    """Query the RAG system."""
    parser = argparse.ArgumentParser(description="Query the RAG system.")
    parser.add_argument(
        "query",
        type=str,
        help="Query text"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--documents-only",
        action="store_true",
        help="Retrieve only relevant documents without generating a response"
    )

    args = parser.parse_args()

    # Initialize query engine
    query_engine = RAGQueryEngine()

    # Process query
    if args.documents_only:
        result = query_engine.get_relevant_documents(args.query)
    else:
        result = query_engine.query(args.query)

    # Format and display results
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if args.documents_only:
            print(f"Query: {args.query}\n")
            print(f"Found {len(result)} relevant documents:\n")
            for i, doc in enumerate(result, 1):
                print(f"Document {i}:")
                print(f"  Source: {doc['metadata'].get('source', 'Unknown')}")
                print(f"  Score: {doc['score']}")
                print(f"  Excerpt: {doc['text'][:200]}...\n")
        else:
            print(f"Query: {args.query}\n")
            print(f"Response: {result['response']}\n")
            print(f"Sources:")
            for i, source in enumerate(result['source_nodes'], 1):
                print(f"  {i}. {source['metadata'].get('source', 'Unknown')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())