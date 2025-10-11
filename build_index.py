"""
Utility to build FAISS index from documents in data/processed directory.

This script reads documents from data/processed/, generates embeddings using 
sentence-transformers (MiniLM), and builds a FAISS index for efficient retrieval.
"""

import os
import pickle
import argparse
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import glob


def read_documents(data_dir: str) -> List[str]:
    """
    Read all text documents from the data directory.
    
    Args:
        data_dir: Directory containing text files
        
    Returns:
        List of document contents
    """
    documents = []
    
    # Look for common text file extensions
    patterns = ['*.txt', '*.md', '*.text']
    
    for pattern in patterns:
        file_pattern = os.path.join(data_dir, pattern)
        files = glob.glob(file_pattern)
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Only add non-empty documents
                        documents.append(content)
                        print(f"Loaded document: {file_path}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return documents


def chunk_documents(documents: List[str], chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split documents into chunks for better retrieval.
    
    Args:
        documents: List of document contents
        chunk_size: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of document chunks
    """
    chunks = []
    
    for doc in documents:
        if len(doc) <= chunk_size:
            chunks.append(doc)
        else:
            # Split document into overlapping chunks
            start = 0
            while start < len(doc):
                end = min(start + chunk_size, len(doc))
                chunk = doc[start:end]
                
                # Try to break at word boundaries
                if end < len(doc) and not doc[end].isspace():
                    last_space = chunk.rfind(' ')
                    if last_space > chunk_size // 2:  # Only if we don't lose too much
                        chunk = chunk[:last_space]
                        end = start + last_space
                
                chunks.append(chunk)
                
                if end >= len(doc):
                    break
                    
                start = end - overlap
    
    return chunks


def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Build FAISS index from embeddings.
    
    Args:
        embeddings: Array of document embeddings
        
    Returns:
        FAISS index
    """
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Create index (Inner Product for normalized vectors = cosine similarity)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    
    # Add embeddings to index
    index.add(embeddings)
    
    return index


def main():
    parser = argparse.ArgumentParser(description='Build FAISS index from documents')
    parser.add_argument('--data-dir', default='data/processed', 
                       help='Directory containing documents to index')
    parser.add_argument('--embeddings-dir', default='embeddings',
                       help='Directory to save the index and metadata')
    parser.add_argument('--model-name', default='all-MiniLM-L6-v2',
                       help='Sentence transformer model name')
    parser.add_argument('--chunk-size', type=int, default=500,
                       help='Maximum characters per chunk')
    parser.add_argument('--overlap', type=int, default=50,
                       help='Character overlap between chunks')
    
    args = parser.parse_args()
    
    # Create embeddings directory if it doesn't exist
    os.makedirs(args.embeddings_dir, exist_ok=True)
    
    print(f"Reading documents from {args.data_dir}...")
    documents = read_documents(args.data_dir)
    
    if not documents:
        print("No documents found! Please add some text files to the data/processed directory.")
        return
    
    print(f"Found {len(documents)} documents")
    
    print("Chunking documents...")
    chunks = chunk_documents(documents, args.chunk_size, args.overlap)
    print(f"Created {len(chunks)} chunks")
    
    print(f"Loading sentence transformer model: {args.model_name}")
    try:
        model = SentenceTransformer(args.model_name)
    except Exception as e:
        print(f"Error loading model {args.model_name}: {e}")
        print("This might be due to network connectivity issues.")
        print("You can still test the retriever using the provided test_retriever.py script.")
        return
    
    print("Generating embeddings...")
    embeddings = model.encode(chunks, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype=np.float32)
    
    print(f"Generated embeddings shape: {embeddings.shape}")
    
    print("Building FAISS index...")
    index = build_faiss_index(embeddings)
    
    # Save index
    index_path = os.path.join(args.embeddings_dir, "faiss_index.bin")
    faiss.write_index(index, index_path)
    print(f"Saved FAISS index to {index_path}")
    
    # Save document chunks
    docs_path = os.path.join(args.embeddings_dir, "documents.pkl")
    with open(docs_path, 'wb') as f:
        pickle.dump(chunks, f)
    print(f"Saved document chunks to {docs_path}")
    
    # Save metadata
    metadata = {
        'model_name': args.model_name,
        'chunk_size': args.chunk_size,
        'overlap': args.overlap,
        'total_documents': len(documents),
        'total_chunks': len(chunks),
        'embedding_dimension': embeddings.shape[1]
    }
    
    metadata_path = os.path.join(args.embeddings_dir, "metadata.pkl")
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"Saved metadata to {metadata_path}")
    
    print("\nIndex building completed successfully!")
    print(f"Index contains {index.ntotal} vectors of dimension {index.d}")


if __name__ == "__main__":
    main()