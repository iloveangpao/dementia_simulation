#!/usr/bin/env python3
"""
Build FAISS Index for Dementia Simulation (Offline Version)

This script loads preprocessed text chunks, generates embeddings using TF-IDF,
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
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

# Configuration
PROCESSED_DIR = "data/processed/"
INDEX_DIR = "data/index/"
MAX_FEATURES = 5000  # Maximum number of TF-IDF features

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

def generate_tfidf_embeddings(chunks: List[Dict[str, Any]]) -> Tuple[np.ndarray, TfidfVectorizer]:
    """Generate TF-IDF embeddings for text chunks."""
    texts = [chunk['text'] for chunk in chunks]
    
    print(f"Generating TF-IDF embeddings for {len(texts)} chunks...")
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=MAX_FEATURES,
        stop_words='english',
        ngram_range=(1, 2),  # Include unigrams and bigrams
        min_df=1,  # Minimum document frequency
        max_df=0.8  # Maximum document frequency
    )
    
    # Fit and transform texts
    tfidf_matrix = vectorizer.fit_transform(texts)
    embeddings = tfidf_matrix.toarray().astype('float32')
    
    print(f"Generated TF-IDF embeddings shape: {embeddings.shape}")
    print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")
    
    return embeddings, vectorizer

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
    vectorizer: TfidfVectorizer
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
    
    # Save vectorizer for query processing
    vectorizer_file = os.path.join(INDEX_DIR, "tfidf_vectorizer.pkl")
    with open(vectorizer_file, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    # Save index configuration
    config = {
        "embedding_type": "tfidf",
        "embedding_dimension": embeddings.shape[1],
        "num_chunks": len(chunks),
        "index_type": "IndexFlatIP",
        "similarity_metric": "cosine",
        "max_features": MAX_FEATURES,
        "vocabulary_size": len(vectorizer.vocabulary_)
    }
    
    config_file = os.path.join(INDEX_DIR, "index_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nIndex and metadata saved:")
    print(f"- FAISS index: {index_file}")
    print(f"- Chunk metadata: {metadata_file}")
    print(f"- Embeddings: {embeddings_file}")
    print(f"- TF-IDF vectorizer: {vectorizer_file}")
    print(f"- Configuration: {config_file}")

def test_index(index: faiss.Index, chunks: List[Dict[str, Any]], vectorizer: TfidfVectorizer):
    """Test the created index with sample queries."""
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
        
        # Generate query embedding using the same vectorizer
        query_tfidf = vectorizer.transform([query])
        query_embedding = query_tfidf.toarray().astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search index
        k = min(3, len(chunks))  # Top 3 results or all chunks if fewer
        scores, indices = index.search(query_embedding, k)
        
        print("Top results:")
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(chunks) and idx >= 0:
                chunk = chunks[idx]
                print(f"  {i+1}. Score: {score:.3f}")
                print(f"     Source: {chunk['source_file']}")
                print(f"     Text: {chunk['text'][:100]}...")
            print()

def main():
    """Main function to build the FAISS index."""
    print("Building FAISS Index for Dementia Simulation (TF-IDF Version)")
    print("=" * 60)
    
    try:
        # Setup
        setup_directories()
        
        # Load processed chunks
        chunks = load_processed_chunks()
        
        if not chunks:
            print("No chunks found. Please run the preprocessing script first.")
            return
        
        # Generate TF-IDF embeddings
        embeddings, vectorizer = generate_tfidf_embeddings(chunks)
        
        # Create FAISS index
        index = create_faiss_index(embeddings)
        
        # Save everything
        save_index_and_metadata(index, chunks, embeddings, vectorizer)
        
        # Test the index
        test_index(index, chunks, vectorizer)
        
        print("\n" + "=" * 60)
        print("Index building completed successfully!")
        print(f"Created TF-IDF index with {len(chunks)} text chunks")
        print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")
        print(f"Index saved to: {INDEX_DIR}")
        
    except Exception as e:
        print(f"Error building index: {str(e)}")
        raise

if __name__ == "__main__":
    main()