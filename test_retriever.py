"""
Test script to demonstrate the Retriever functionality.
This creates a simple mock setup for testing when models can't be downloaded.
"""

import os
import sys
import numpy as np
import pickle
import faiss
from typing import List

# Add src to path
sys.path.append('src')

def create_mock_embeddings_and_index():
    """Create a mock FAISS index for testing purposes."""
    
    # Sample documents (same as our test files)
    documents = [
        "Dementia is a general term for loss of memory, language, problem-solving and other thinking abilities that are severe enough to interfere with daily life. Alzheimer's disease is the most common cause of dementia.",
        "Dementia is not a single disease; it's an overall term that describes a group of symptoms associated with a decline in memory or other thinking skills severe enough to reduce a person's ability to perform everyday activities.",
        "Early signs of dementia include difficulty remembering recent events, problems with planning or solving problems, confusion with time or place, trouble understanding visual images and spatial relationships.",
        "Alzheimer's disease is a progressive disorder that causes brain cells to waste away and die. Alzheimer's disease is the most common cause of dementia.",
        "The exact cause of Alzheimer's disease isn't fully understood, but at its core are problems with brain proteins that fail to function normally, disrupt the work of brain cells.",
        "Symptoms of Alzheimer's disease include memory loss that disrupts daily life, challenges in planning or solving problems, difficulty completing familiar tasks.",
        "Caring for someone with dementia can be physically and emotionally challenging. Support services can help both the person with dementia and their caregivers.",
        "Key strategies for dementia care include maintaining routines, creating a safe environment, encouraging physical activity, providing emotional support.",
        "Family caregivers often experience stress, depression, and health problems. It's important for caregivers to take care of their own physical and emotional needs."
    ]
    
    # Create mock embeddings (random vectors for demonstration)
    # In real usage, these would come from sentence-transformers
    np.random.seed(42)  # For reproducible results
    embeddings = np.random.randn(len(documents), 384).astype(np.float32)
    
    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    
    # Create embeddings directory
    os.makedirs('embeddings', exist_ok=True)
    
    # Save index
    faiss.write_index(index, 'embeddings/faiss_index.bin')
    
    # Save documents
    with open('embeddings/documents.pkl', 'wb') as f:
        pickle.dump(documents, f)
    
    # Save metadata
    metadata = {
        'model_name': 'all-MiniLM-L6-v2',
        'total_documents': len(documents),
        'embedding_dimension': dimension
    }
    with open('embeddings/metadata.pkl', 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"Created mock index with {len(documents)} documents")
    print(f"Embedding dimension: {dimension}")
    return documents


def test_retriever():
    """Test the Retriever class with mock data."""
    from retriever import Retriever
    
    # Create a custom retriever class that uses mock embeddings
    class MockRetriever(Retriever):
        def __init__(self, embeddings_dir="embeddings"):
            self.embeddings_dir = embeddings_dir
            self.model_name = "mock-model"
            self.model = None
            self.index = None
            self.documents = None
        
        def load_index(self):
            """Load the mock index."""
            try:
                # Load FAISS index
                index_path = os.path.join(self.embeddings_dir, "faiss_index.bin")
                if not os.path.exists(index_path):
                    print(f"FAISS index not found at {index_path}")
                    return False
                
                self.index = faiss.read_index(index_path)
                
                # Load document metadata
                docs_path = os.path.join(self.embeddings_dir, "documents.pkl")
                if not os.path.exists(docs_path):
                    print(f"Documents metadata not found at {docs_path}")
                    return False
                    
                with open(docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                
                print(f"Successfully loaded index with {self.index.ntotal} vectors")
                print(f"Loaded {len(self.documents)} document chunks")
                return True
                
            except Exception as e:
                print(f"Error loading index: {e}")
                return False
        
        def retrieve(self, query: str, top_k: int = 5):
            """Mock retrieval using random query vector."""
            if self.index is None or self.documents is None:
                if not self.load_index():
                    return []
            
            try:
                # Create a mock query embedding (random vector)
                # In real usage, this would come from sentence-transformers
                np.random.seed(hash(query) % (2**32))  # Deterministic based on query
                query_vector = np.random.randn(1, 384).astype(np.float32)
                faiss.normalize_L2(query_vector)
                
                # Search in FAISS index
                scores, indices = self.index.search(query_vector, top_k)
                
                # Prepare results
                results = []
                for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                    if idx != -1:  # Valid index
                        document_chunk = self.documents[idx]
                        similarity_score = float(score)
                        results.append((document_chunk, similarity_score))
                
                return results
                
            except Exception as e:
                print(f"Error during retrieval: {e}")
                return []
    
    # Test the retriever
    retriever = MockRetriever()
    
    # Test queries
    test_queries = [
        "What is dementia?",
        "Alzheimer's disease symptoms",
        "How to care for dementia patients",
        "Memory loss problems"
    ]
    
    print("\n" + "="*50)
    print("TESTING RETRIEVER FUNCTIONALITY")
    print("="*50)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)
        
        results = retriever.retrieve(query, top_k=3)
        
        if results:
            for i, (doc, score) in enumerate(results, 1):
                print(f"{i}. Score: {score:.4f}")
                print(f"   Text: {doc[:100]}...")
                print()
        else:
            print("No results found")
    
    # Test index info
    print("\n" + "="*50)
    print("INDEX INFORMATION")
    print("="*50)
    info = retriever.get_index_info()
    for key, value in info.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    print("Creating mock embeddings and index...")
    create_mock_embeddings_and_index()
    
    print("\nTesting retriever...")
    test_retriever()