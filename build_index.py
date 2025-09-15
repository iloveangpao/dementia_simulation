#!/usr/bin/env python3
"""
Build FAISS Index for Dementia Simulation

This script loads preprocessed text chunks, generates embeddings using sentence transformers,
and creates a FAISS index for efficient similarity search.
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
import faiss
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Configuration
PROCESSED_DIR = "data/processed/"
INDEX_DIR = "data/index/"
MODEL_NAME = "all-MiniLM-L6-v2"  # Fast and efficient sentence transformer model
BATCH_SIZE = 32  # Batch size for embedding generation

def setup_directories():
    """Create necessary directories."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(INDEX_DIR, exist_ok=True)
    print(f"Processed data directory: {PROCESSED_DIR}")
    print(f"Index directory: {INDEX_DIR}")

def load_processed_chunks(chunks_file: str = None) -> List[Dict[str, Any]]:
    """Load preprocessed text chunks from JSON file."""
    if chunks_file is None:
        chunks_file = os.path.join(PROCESSED_DIR, "text_chunks.json")
    
    if not os.path.exists(chunks_file):
        raise FileNotFoundError(
            f"Text chunks file not found: {chunks_file}\n"
            "Please run the preprocessing notebook first."
        )
    
    with open(chunks_file, 'r') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} text chunks from {chunks_file}")
    return chunks

def load_embedding_model(model_name: str = MODEL_NAME) -> SentenceTransformer:
    """Load sentence transformer model for embedding generation."""
    print(f"Loading sentence transformer model: {model_name}")
    
    try:
        model = SentenceTransformer(model_name)
        print(f"Model loaded successfully. Embedding dimension: {model.get_sentence_embedding_dimension()}")
        return model
    except Exception as e:
        print(f"Error loading model {model_name}: {str(e)}")
        raise

def generate_embeddings(chunks: List[Dict[str, Any]], model: SentenceTransformer) -> np.ndarray:
    """Generate embeddings for text chunks."""
    texts = [chunk['text'] for chunk in chunks]
    
    print(f"Generating embeddings for {len(texts)} chunks...")
    
    # Generate embeddings in batches
    embeddings = []
    for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Generating embeddings"):
        batch_texts = texts[i:i + BATCH_SIZE]
        batch_embeddings = model.encode(batch_texts, convert_to_numpy=True)
        embeddings.extend(batch_embeddings)
    
    embeddings_array = np.array(embeddings).astype('float32')
    print(f"Generated embeddings shape: {embeddings_array.shape}")
    
    return embeddings_array

def create_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """Create FAISS index for efficient similarity search."""
    dimension = embeddings.shape[1]
    
    print(f"Creating FAISS index with dimension {dimension}")
    
    # Use IndexFlatIP for cosine similarity (inner product)
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Create index
    index = faiss.IndexFlatIP(dimension)
    
    # Add embeddings to index
    index.add(embeddings)
    
    print(f"FAISS index created with {index.ntotal} vectors")
    
    return index

def save_index_and_metadata(
    index: faiss.Index, 
    chunks: List[Dict[str, Any]], 
    embeddings: np.ndarray,
    model_name: str
):
    """Save FAISS index and associated metadata."""
    
    # Save FAISS index
    index_file = os.path.join(INDEX_DIR, "document_index.faiss")
    faiss.write_index(index, index_file)
    
    # Save chunk metadata (for retrieving original text)
    metadata_file = os.path.join(INDEX_DIR, "chunk_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(chunks, f, indent=2)
    
    # Save embeddings as numpy array (for backup/analysis)
    embeddings_file = os.path.join(INDEX_DIR, "embeddings.npy")
    np.save(embeddings_file, embeddings)
    
    # Save index configuration
    config = {
        "model_name": model_name,
        "embedding_dimension": embeddings.shape[1],
        "num_chunks": len(chunks),
        "index_type": "IndexFlatIP",
        "similarity_metric": "cosine"
    }
    
    config_file = os.path.join(INDEX_DIR, "index_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nIndex and metadata saved:")
    print(f"- FAISS index: {index_file}")
    print(f"- Chunk metadata: {metadata_file}")
    print(f"- Embeddings: {embeddings_file}")
    print(f"- Configuration: {config_file}")

def test_index(index: faiss.Index, chunks: List[Dict[str, Any]], model: SentenceTransformer):
    """Test the created index with a sample query."""
    print("\nTesting index with sample queries...")
    
    # Sample queries
    test_queries = [
        "memory loss and forgetfulness",
        "patient care strategies",
        "dementia symptoms",
        "communication with patients"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        # Generate query embedding
        query_embedding = model.encode([query], convert_to_numpy=True).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search index
        k = 3  # Top 3 results
        scores, indices = index.search(query_embedding, k)
        
        print("Top results:")
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(chunks):
                chunk = chunks[idx]
                print(f"  {i+1}. Score: {score:.3f}")
                print(f"     Source: {chunk['source_file']}")
                print(f"     Text: {chunk['text'][:100]}...")
            print()

def main():
    """Main function to build the FAISS index."""
    print("Building FAISS Index for Dementia Simulation")
    print("=" * 50)
    
    try:
        # Setup
        setup_directories()
        
        # Load processed chunks
        chunks = load_processed_chunks()
        
        if not chunks:
            print("No chunks found. Please run the preprocessing notebook first.")
            return
        
        # Load embedding model
        model = load_embedding_model()
        
        # Generate embeddings
        embeddings = generate_embeddings(chunks, model)
        
        # Create FAISS index
        index = create_faiss_index(embeddings)
        
        # Save everything
        save_index_and_metadata(index, chunks, embeddings, MODEL_NAME)
        
        # Test the index
        test_index(index, chunks, model)
        
        print("\n" + "=" * 50)
        print("Index building completed successfully!")
        print(f"Created index with {len(chunks)} text chunks")
        print(f"Index saved to: {INDEX_DIR}")
        
    except Exception as e:
        print(f"Error building index: {str(e)}")
        raise

if __name__ == "__main__":
    main()