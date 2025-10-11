#!/usr/bin/env python3
"""
Build FAISS Index for Dementia Simulation

This utility script loads preprocessed documents, generates embeddings using
sentence-transformers (MiniLM), and creates a FAISS index for efficient retrieval.
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from src.dementia_simulation.retriever.faiss_retriever import FAISSRetriever


def load_documents_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Load documents from a JSON file.

    Args:
        file_path: Path to JSON file containing documents

    Returns:
        List of document dictionaries
    """
    with open(file_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    logger.info(f"Loaded {len(documents)} documents from {file_path}")
    return documents


def load_documents_from_markdown(file_path: str) -> List[Dict[str, Any]]:
    """
    Load and chunk documents from a Markdown file.

    Args:
        file_path: Path to Markdown file

    Returns:
        List of document dictionaries with text chunks
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by headers (## sections)
    sections = []
    current_section = []
    current_title = ""

    for line in content.split("\n"):
        if line.startswith("## "):
            # Save previous section
            if current_section:
                sections.append(
                    {
                        "text": "\n".join(current_section).strip(),
                        "title": current_title,
                        "source_file": os.path.basename(file_path),
                    }
                )
            # Start new section
            current_title = line.replace("## ", "").strip()
            current_section = [line]
        else:
            current_section.append(line)

    # Add last section
    if current_section:
        sections.append(
            {
                "text": "\n".join(current_section).strip(),
                "title": current_title,
                "source_file": os.path.basename(file_path),
            }
        )

    # Filter out empty sections
    documents = [doc for doc in sections if doc["text"] and len(doc["text"]) > 50]

    logger.info(f"Extracted {len(documents)} sections from {file_path}")
    return documents


def discover_documents(
    processed_dir: str, knowledge_base_dir: str
) -> List[Dict[str, Any]]:
    """
    Discover and load all documents from available directories.

    Args:
        processed_dir: Path to processed data directory
        knowledge_base_dir: Path to knowledge base directory

    Returns:
        List of all discovered documents
    """
    all_documents = []

    # Try to load from processed directory first
    if os.path.exists(processed_dir):
        for file_path in Path(processed_dir).glob("*.json"):
            try:
                docs = load_documents_from_json(str(file_path))
                all_documents.extend(docs)
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}")

    # Load from knowledge base directory
    if os.path.exists(knowledge_base_dir):
        for file_path in Path(knowledge_base_dir).glob("*.md"):
            try:
                docs = load_documents_from_markdown(str(file_path))
                all_documents.extend(docs)
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}")

        for file_path in Path(knowledge_base_dir).glob("*.json"):
            try:
                docs = load_documents_from_json(str(file_path))
                all_documents.extend(docs)
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}")

    return all_documents


def main():
    """Main function to build the FAISS index."""
    parser = argparse.ArgumentParser(
        description="Build FAISS index from processed documents"
    )
    parser.add_argument(
        "--processed-dir",
        type=str,
        default="data/processed",
        help="Directory containing processed documents (default: data/processed)",
    )
    parser.add_argument(
        "--knowledge-base-dir",
        type=str,
        default="data/knowledge_base",
        help="Directory containing knowledge base files (default: data/knowledge_base)",
    )
    parser.add_argument(
        "--embeddings-dir",
        type=str,
        default="embeddings",
        help="Directory to save embeddings and index (default: embeddings)",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="all-MiniLM-L6-v2",
        help="Sentence transformer model to use (default: all-MiniLM-L6-v2)",
    )
    parser.add_argument(
        "--index-type",
        type=str,
        default="flat",
        choices=["flat", "ivf", "hnsw"],
        help="Type of FAISS index to create (default: flat)",
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Building FAISS Index for Dementia Simulation")
    logger.info("=" * 60)

    # Create embeddings directory
    os.makedirs(args.embeddings_dir, exist_ok=True)

    # Discover documents
    logger.info("Searching for documents in:")
    logger.info(f"  - {args.processed_dir}")
    logger.info(f"  - {args.knowledge_base_dir}")

    documents = discover_documents(args.processed_dir, args.knowledge_base_dir)

    if not documents:
        logger.error("No documents found! Please add documents to process.")
        logger.info("Expected locations:")
        logger.info(f"  - {args.processed_dir}/*.json")
        logger.info(f"  - {args.knowledge_base_dir}/*.md")
        logger.info(f"  - {args.knowledge_base_dir}/*.json")
        return 1

    logger.info(f"Found {len(documents)} documents to index")

    # Initialize retriever
    index_path = os.path.join(args.embeddings_dir, "faiss_index.index")
    documents_path = os.path.join(args.embeddings_dir, "documents.json")

    logger.info(f"Initializing retriever with model: {args.model_name}")
    retriever = FAISSRetriever(
        model_name=args.model_name, index_path=index_path, documents_path=documents_path
    )

    # Create index
    logger.info(f"Creating {args.index_type} FAISS index...")
    retriever.create_index(index_type=args.index_type)

    # Add documents
    logger.info("Generating embeddings and adding documents to index...")
    retriever.add_documents(documents)

    # Save index
    logger.info("Saving index and metadata...")
    retriever.save_index()

    # Print statistics
    stats = retriever.get_stats()
    logger.info("=" * 60)
    logger.info("Index built successfully!")
    logger.info("=" * 60)
    logger.info(f"Model: {stats['model_name']}")
    logger.info(f"Embedding dimension: {stats['embedding_dimension']}")
    logger.info(f"Total documents: {stats['total_documents']}")
    logger.info(f"Total vectors: {stats['index_total_vectors']}")
    logger.info(f"Index saved to: {index_path}")
    logger.info(f"Documents saved to: {documents_path}")
    logger.info("=" * 60)

    # Test retrieval
    logger.info("\nTesting retrieval with sample query...")
    test_query = "How to communicate with dementia patients?"
    results = retriever.search(test_query, k=3)

    logger.info(f"\nQuery: '{test_query}'")
    logger.info(f"Top {len(results)} results:")
    for i, (doc, score) in enumerate(results, 1):
        logger.info(f"\n{i}. Score: {score:.3f}")
        text_preview = (
            doc["text"][:100] + "..." if len(doc["text"]) > 100 else doc["text"]
        )
        logger.info(f"   Text: {text_preview}")
        if "title" in doc:
            logger.info(f"   Title: {doc['title']}")
        if "source_file" in doc:
            logger.info(f"   Source: {doc['source_file']}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
