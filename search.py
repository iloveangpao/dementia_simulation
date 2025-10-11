#!/usr/bin/env python3
"""
Search utility for the dementia simulation document index.
"""

import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple

INDEX_DIR = "data/index/"

def load_index() -> Tuple[faiss.Index, List[Dict[str, Any]], SentenceTransformer]:
    """Load the FAISS index and associated metadata."""
    
    # Load configuration
    config_file = os.path.join(INDEX_DIR, "index_config.json")
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Load FAISS index
    index_file = os.path.join(INDEX_DIR, "document_index.faiss")
    index = faiss.read_index(index_file)
    
    # Load chunk metadata
    metadata_file = os.path.join(INDEX_DIR, "chunk_metadata.json")
    with open(metadata_file, 'r') as f:
        chunks = json.load(f)
    
    # Load model
    model = SentenceTransformer(config['model_name'])
    
    return index, chunks, model

def search_documents(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search for relevant documents given a query."""
    
    index, chunks, model = load_index()
    
    # Generate query embedding
    query_embedding = model.encode([query], convert_to_numpy=True).astype('float32')
    faiss.normalize_L2(query_embedding)
    
    # Search
    scores, indices = index.search(query_embedding, k)
    
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(chunks):
            chunk = chunks[idx]
            results.append({
                'score': float(score),
                'text': chunk['text'],
                'source_file': chunk['source_file'],
                'chunk_id': chunk['id']
            })
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python search.py 'your search query'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    results = search_documents(query)
    
    print(f"Search results for: '{query}'")
    print("=" * 50)
    
    for i, result in enumerate(results):
        print(f"{i+1}. Score: {result['score']:.3f}")
        print(f"   Source: {result['source_file']}")
        print(f"   Text: {result['text'][:200]}...")
        print()