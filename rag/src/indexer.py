"""
Indexer module for processing and indexing markdown files.
"""
import os
import glob
import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from llama_index.core import Document, Settings, StorageContext
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter, NodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import yaml

from . import config


class MarkdownHeaderSplitter:
    """
    Custom document splitter that respects Markdown headings and structure.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize the Markdown header splitter.

        Args:
            chunk_size: Maximum chunk size in characters.
            chunk_overlap: Overlap between chunks in characters.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Fallback to sentence splitter for text without headings
        self.sentence_splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def get_nodes_from_documents(self, documents: List[Document]) -> List[Document]:
        """
        Compatibility method with NodeParser interface.

        Args:
            documents: List of documents to process.

        Returns:
            List of Document objects after splitting.
        """
        result = []
        for doc in documents:
            result.extend(self.split_text(doc.text, doc.metadata))
        return result

    def _get_heading_level(self, line: str) -> int:
        """Get the heading level of a markdown line."""
        if not line.startswith('#'):
            return 0

        # Count the number of # at the beginning of the line
        level = 0
        for char in line:
            if char == '#':
                level += 1
            else:
                break

        # Verify it's a proper heading with space after #
        if level > 0 and len(line) > level and line[level] == ' ':
            return level
        return 0

    def _extract_sections(self, text: str) -> List[Tuple[int, str, str]]:
        """
        Extract sections from markdown text based on headings.

        Returns:
            List of tuples (heading_level, heading_text, section_content)
        """
        lines = text.split('\n')
        sections = []

        current_level = 0
        current_heading = "Document"
        current_content = []

        for line in lines:
            heading_level = self._get_heading_level(line)

            if heading_level > 0:
                # Save previous section if it exists
                if current_content:
                    sections.append((current_level, current_heading, '\n'.join(current_content)))

                # Start new section
                current_level = heading_level
                current_heading = line.strip('# \t')
                current_content = []
            else:
                current_content.append(line)

        # Add the last section
        if current_content:
            sections.append((current_level, current_heading, '\n'.join(current_content)))

        return sections

    def _should_split_section(self, section_text: str) -> bool:
        """Determine if a section should be split further based on size."""
        return len(section_text) > self.chunk_size

    def split_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Split markdown text into chunks respecting headings and structure.

        Args:
            text: Markdown text to split.
            metadata: Metadata to include with each document.

        Returns:
            List of Document objects.
        """
        # If the document is smaller than chunk_size, don't split it
        if len(text) <= self.chunk_size:
            return [Document(text=text, metadata=metadata or {})]

        # Extract sections based on headings
        sections = self._extract_sections(text)

        # Handle case with no sections or only default section
        if not sections or (len(sections) == 1 and sections[0][0] == 0):
            return self.sentence_splitter.get_nodes_from_documents(
                [Document(text=text, metadata=metadata or {})]
            )

        documents = []

        for level, heading, content in sections:
            section_metadata = dict(metadata) if metadata else {}
            section_metadata["heading"] = heading
            section_metadata["heading_level"] = level

            # Don't split small sections
            if self._should_split_section(content):
                # For larger sections, use the sentence splitter
                sub_docs = self.sentence_splitter.get_nodes_from_documents(
                    [Document(text=content, metadata=section_metadata)]
                )

                # Update metadata to include heading information
                for doc in sub_docs:
                    if hasattr(doc, 'metadata'):
                        doc.metadata.update(section_metadata)

                documents.extend(sub_docs)
            else:
                documents.append(Document(
                    text=content,
                    metadata=section_metadata
                ))

        return documents


class MarkdownIndexer:
    """Indexes markdown files using LlamaIndex and ChromaDB."""

    def __init__(self, markdown_dir: Optional[str] = None):
        """
        Initialize the indexer.

        Args:
            markdown_dir: Directory containing markdown files to index.
                          If None, uses the value from config.
        """
        self.markdown_dir = markdown_dir or config.MARKDOWN_DIR
        self.chroma_db_dir = config.CHROMA_DB_DIR
        self.setup_llama_index()

    def setup_llama_index(self):
        """Configure LlamaIndex settings."""
        # Set up embedding model
        embed_model = HuggingFaceEmbedding(
            model_name=config.EMBEDDING_MODEL
        )

        # Configure custom markdown-aware node parser
        node_parser = MarkdownHeaderSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )

        # Apply settings globally
        Settings.embed_model = embed_model
        Settings.node_parser = node_parser

        # Set up ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=self.chroma_db_dir
        )
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            "markdown_collection"
        )

        # Create vector store
        self.vector_store = ChromaVectorStore(
            chroma_collection=self.chroma_collection
        )

        # Create storage context
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )

    def _find_markdown_files(self) -> List[str]:
        """
        Find all markdown files in the configured directory.

        Returns:
            List of file paths.
        """
        markdown_files = []
        for extension in ["*.md", "*.markdown"]:
            pattern = os.path.join(self.markdown_dir, "**", extension)
            markdown_files.extend(glob.glob(pattern, recursive=True))

        return markdown_files

    def _extract_front_matter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """
        Extract YAML front matter from markdown content if present.

        Returns:
            Tuple of (front_matter_dict, content_without_front_matter)
        """
        front_matter = {}

        # Check for YAML front matter (between --- delimiters)
        front_matter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)

        if front_matter_match:
            try:
                front_matter_yaml = front_matter_match.group(1)
                content_without_front_matter = front_matter_match.group(2)
                front_matter = yaml.safe_load(front_matter_yaml)
                if front_matter is None:  # Handle empty front matter
                    front_matter = {}
                return front_matter, content_without_front_matter
            except Exception as e:
                print(f"Error parsing front matter: {e}")

        return front_matter, content

    def _process_markdown_file(self, file_path: str) -> List[Document]:
        """
        Process a single markdown file into document chunks.

        Args:
            file_path: Path to the markdown file.

        Returns:
            List of Document objects.
        """
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract front matter if present
            front_matter, content = self._extract_front_matter(content)

            # Create base metadata
            relative_path = os.path.relpath(file_path, self.markdown_dir)
            metadata = {
                "source": relative_path,
                "filename": os.path.basename(file_path),
                "filepath": file_path,
            }

            # Add front matter to metadata if available
            if front_matter:
                metadata.update({f"front_matter_{k}": v for k, v in front_matter.items()})

            # Split document using our custom splitter
            splitter = MarkdownHeaderSplitter(
                chunk_size=config.CHUNK_SIZE,
                chunk_overlap=config.CHUNK_OVERLAP
            )

            try:
                doc_chunks = splitter.split_text(content, metadata)
                print(f"Split '{relative_path}' into {len(doc_chunks)} chunks")
                return doc_chunks
            except Exception as split_error:
                print(f"Error splitting '{relative_path}': {split_error}")
                # Fallback to adding the document without splitting
                return [Document(text=content, metadata=metadata)]

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []

    def index_documents(self, force_reindex: bool = False) -> VectorStoreIndex:
        """
        Load and index documents from the markdown directory.

        Args:
            force_reindex: If True, delete existing index and reindex all documents.
                           If False, append to existing index if one exists.

        Returns:
            The created or updated VectorStoreIndex.
        """
        # Check if we need to force reindexing
        if force_reindex and self.chroma_collection.count() > 0:
            print("Force reindexing: deleting existing index...")
            self.chroma_client.delete_collection("markdown_collection")
            self.chroma_collection = self.chroma_client.get_or_create_collection("markdown_collection")
            self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        # Find all markdown files
        markdown_files = self._find_markdown_files()

        if not markdown_files:
            print("No markdown files found in the specified directory.")
            return None

        print(f"Found {len(markdown_files)} markdown files to process...")

        # Create or get the index
        if self.chroma_collection.count() > 0:
            print("Appending to existing index...")
            index = VectorStoreIndex.from_vector_store(
                self.vector_store,
            )
        else:
            print("Creating new index...")
            # Create empty index with our storage context
            index = VectorStoreIndex.from_documents(
                [],  # Start with empty documents list
                storage_context=self.storage_context,
            )

        # Process files one by one
        total_chunks = 0
        batch_size = 10  # Number of files to process in a batch

        for i, file_path in enumerate(markdown_files):
            relative_path = os.path.relpath(file_path, self.markdown_dir)
            print(f"Processing [{i+1}/{len(markdown_files)}]: {relative_path}")

            doc_chunks = self._process_markdown_file(file_path)
            total_chunks += len(doc_chunks)

            # Index chunks from this file
            for chunk in doc_chunks:
                index.insert(chunk)

            # Optional: Commit to disk periodically to avoid memory buildup
            if (i + 1) % batch_size == 0:
                print(f"Processed {i+1} files so far with {total_chunks} total chunks")

        print(f"Indexing complete. Processed {len(markdown_files)} files with {total_chunks} total chunks.")
        return index

    def get_or_create_index(self) -> VectorStoreIndex:
        """
        Get the existing index or create a new one if needed.

        Returns:
            VectorStoreIndex: The vector store index.
        """
        # Check if we have existing vectors
        if self.chroma_collection.count() > 0:
            print("Loading existing index...")
            return VectorStoreIndex.from_vector_store(
                self.vector_store,
            )
        else:
            print("Creating new index...")
            return self.index_documents()