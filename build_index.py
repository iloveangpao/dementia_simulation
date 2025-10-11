#!/usr/bin/env python3
"""
Build FAISS Index for Dementia Simulation

This script loads preprocessed text chunks or knowledge base documents,
generates embeddings using sentence-transformers (MiniLM), and creates
a FAISS index for efficient similarity search.

The script can work with:
- Preprocessed JSON chunks from data/processed/
- Markdown files from data/knowledge_base/
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from src.dementia_simulation.retriever.faiss_retriever import (
    FAISSRetriever,
    create_dementia_knowledge_base
)


def load_processed_chunks(processed_dir: str = "data/processed") -> List[Dict[str, Any]]:
    """
    Load preprocessed text chunks from JSON file.
    
    Args:
        processed_dir: Directory containing processed chunks
        
    Returns:
        List of document dictionaries
    """
    chunks_file = os.path.join(processed_dir, "text_chunks.json")
    
    if not os.path.exists(chunks_file):
        logger.warning(f"Processed chunks file not found: {chunks_file}")
        return []
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    logger.info(f"Loaded {len(chunks)} text chunks from {chunks_file}")
    return chunks


def load_knowledge_base_markdown(kb_dir: str = "data/knowledge_base") -> List[Dict[str, Any]]:
    """
    Load and parse markdown files from knowledge base directory.
    
    Args:
        kb_dir: Directory containing knowledge base markdown files
        
    Returns:
        List of document dictionaries with text and metadata
    """
    documents = []
    kb_path = Path(kb_dir)
    
    if not kb_path.exists():
        logger.warning(f"Knowledge base directory not found: {kb_dir}")
        return documents
    
    # Find all markdown files
    md_files = list(kb_path.glob("*.md"))
    
    if not md_files:
        logger.warning(f"No markdown files found in {kb_dir}")
        return documents
    
    for md_file in md_files:
        logger.info(f"Processing {md_file.name}...")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by headers or paragraphs for better chunking
        # Simple approach: split by double newlines
        chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
        
        for i, chunk in enumerate(chunks):
            # Skip very short chunks (likely just headers)
            if len(chunk) < 50:
                continue
            
            documents.append({
                'text': chunk,
                'source_file': md_file.name,
                'chunk_id': i,
                'category': 'knowledge_base'
            })
    
    logger.info(f"Extracted {len(documents)} chunks from {len(md_files)} markdown files")
    return documents


def build_index(
    output_dir: str = "embeddings",
    source: str = "auto",
    processed_dir: str = "data/processed",
    kb_dir: str = "data/knowledge_base",
    model_name: str = "all-MiniLM-L6-v2",
    device: str = None
) -> None:
    """
    Build FAISS index from documents.
    
    Args:
        output_dir: Directory to save the index and metadata
        source: Source of documents ('auto', 'processed', 'knowledge_base', 'default')
        processed_dir: Directory containing processed chunks
        kb_dir: Directory containing knowledge base markdown files
        model_name: Sentence transformer model name
        device: Device to use ('cpu', 'cuda', or None for auto-detect)
    """
    logger.info("=" * 60)
    logger.info("Building FAISS Index for Dementia Simulation")
    logger.info("=" * 60)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")
    
    # Initialize retriever with custom paths
    index_path = os.path.join(output_dir, "faiss_index.index")
    documents_path = os.path.join(output_dir, "documents.json")
    
    retriever = FAISSRetriever(
        model_name=model_name,
        index_path=index_path,
        documents_path=documents_path,
        device=device
    )
    
    # Load documents based on source
    documents = []
    
    if source == "auto":
        # Try processed first, then knowledge base, then default
        logger.info("Auto-detecting document source...")
        documents = load_processed_chunks(processed_dir)
        
        if not documents:
            logger.info("No processed chunks found, trying knowledge base...")
            documents = load_knowledge_base_markdown(kb_dir)
        
        if not documents:
            logger.info("No documents found, using default knowledge base...")
            source = "default"
    
    elif source == "processed":
        documents = load_processed_chunks(processed_dir)
        
    elif source == "knowledge_base":
        documents = load_knowledge_base_markdown(kb_dir)
    
    if source == "default" or not documents:
        logger.info("Using built-in dementia knowledge base...")
        documents = create_dementia_knowledge_base()
    
    if not documents:
        logger.error("No documents to index!")
        return
    
    logger.info(f"Total documents to index: {len(documents)}")
    logger.info(f"Using model: {model_name}")
    
    # Add documents to retriever (this creates the index)
    retriever.add_documents(documents)
    
    # Save the index
    retriever.save_index()
    
    # Test the index with a sample query
    logger.info("\n" + "=" * 60)
    logger.info("Testing the index with sample queries...")
    logger.info("=" * 60)
    
    test_queries = [
        "How to handle agitation in dementia patients?",
        "Communication tips for moderate dementia",
        "Memory care strategies"
    ]
    
    for query in test_queries:
        results = retriever.search(query, k=3)
        logger.info(f"\nQuery: '{query}'")
        logger.info(f"Found {len(results)} results:")
        
        for i, (doc, score) in enumerate(results, 1):
            text_preview = doc['text'][:100] + "..." if len(doc['text']) > 100 else doc['text']
            logger.info(f"  {i}. Score: {score:.3f} - {text_preview}")
    
    # Print stats
    stats = retriever.get_stats()
    logger.info("\n" + "=" * 60)
    logger.info("Index Statistics:")
    logger.info("=" * 60)
    for key, value in stats.items():
        logger.info(f"{key}: {value}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Index building completed successfully!")
    logger.info(f"Index saved to: {index_path}")
    logger.info(f"Documents saved to: {documents_path}")
    logger.info("=" * 60)


def main():
    """Main function to build the FAISS index."""
    parser = argparse.ArgumentParser(
        description="Build FAISS index for dementia simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect source (tries processed, then knowledge base, then default)
  python build_index.py
  
  # Use specific source
  python build_index.py --source knowledge_base
  python build_index.py --source processed
  python build_index.py --source default
  
  # Specify custom directories
  python build_index.py --output-dir my_embeddings --kb-dir data/docs
  
  # Use different model
  python build_index.py --model all-mpnet-base-v2
        """
    )
    
    parser.add_argument(
        "--output-dir",
        default="embeddings",
        help="Directory to save the index (default: embeddings)"
    )
    
    parser.add_argument(
        "--source",
        choices=["auto", "processed", "knowledge_base", "default"],
        default="auto",
        help="Source of documents (default: auto)"
    )
    
    parser.add_argument(
        "--processed-dir",
        default="data/processed",
        help="Directory containing processed chunks (default: data/processed)"
    )
    
    parser.add_argument(
        "--kb-dir",
        default="data/knowledge_base",
        help="Directory containing knowledge base files (default: data/knowledge_base)"
    )
    
    parser.add_argument(
        "--model",
        default="all-MiniLM-L6-v2",
        help="Sentence transformer model name (default: all-MiniLM-L6-v2)"
    )
    
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda", "auto"],
        default=None,
        help="Device to use for model (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    try:
        build_index(
            output_dir=args.output_dir,
            source=args.source,
            processed_dir=args.processed_dir,
            kb_dir=args.kb_dir,
            model_name=args.model,
            device=args.device
        )
    except Exception as e:
        logger.error(f"Error building index: {e}")
        raise


if __name__ == "__main__":
    main()
