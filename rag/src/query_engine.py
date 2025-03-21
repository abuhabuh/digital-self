"""
Query engine module for retrieving information from the indexed documents.
"""
from typing import Dict, List, Optional, Any

from llama_index.core.indices import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import ResponseMode, get_response_synthesizer
from llama_index.core import Settings

from . import config
from .indexer import MarkdownIndexer


class RAGQueryEngine:
    """Query engine for retrieving information from indexed documents."""

    def __init__(self, index: Optional[VectorStoreIndex] = None):
        """
        Initialize the query engine.

        Args:
            index: VectorStoreIndex to use for querying.
                   If None, loads or creates the index.
        """
        if index is None:
            indexer = MarkdownIndexer()
            self.index = indexer.get_or_create_index()
        else:
            self.index = index

        self.setup_query_engine()

    def setup_query_engine(self):
        """Configure the query engine."""
        # Create retriever
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=config.TOP_K,
        )

        # Create response synthesizer
        self.response_synthesizer = get_response_synthesizer(
            response_mode=ResponseMode.COMPACT,
        )

        # Create query engine
        self.query_engine = RetrieverQueryEngine(
            retriever=self.retriever,
            response_synthesizer=self.response_synthesizer,
        )

    def query(self, query_text: str) -> Dict[str, Any]:
        """
        Query the index and return relevant information.

        Args:
            query_text: The query text.

        Returns:
            Dict containing response and source metadata.
        """
        # Perform query
        response = self.query_engine.query(query_text)

        # Collect source metadata
        source_nodes = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                source_nodes.append({
                    "text": node.text[:500] + "..." if len(node.text) > 500 else node.text,
                    "metadata": node.metadata,
                    "score": node.score if hasattr(node, 'score') else None,
                })

        return {
            "query": query_text,
            "response": str(response),
            "source_nodes": source_nodes,
        }

    def get_relevant_documents(self, query_text: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query without generating a response.

        Args:
            query_text: The query text.

        Returns:
            List of dictionaries containing document text and metadata.
        """
        nodes = self.retriever.retrieve(query_text)

        results = []
        for node in nodes:
            results.append({
                "text": node.text,
                "metadata": node.metadata,
                "score": node.score if hasattr(node, 'score') else None,
            })

        return results