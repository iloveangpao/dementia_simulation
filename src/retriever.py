"""
Retriever class using sentence-transformers (MiniLM) + FAISS for document retrieval.
"""

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional


class Retriever:
    """
    Document retriever using sentence-transformers and FAISS for similarity search.
    
    This class loads a prebuilt FAISS index and provides functionality to retrieve
    the top_k most relevant document chunks for a given query.
    """
    
    def __init__(self, 
                 embeddings_dir: str = "embeddings",
                 model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the Retriever.
        
        Args:
            embeddings_dir: Directory containing the prebuilt FAISS index and metadata
            model_name: Name of the sentence-transformer model to use
        """
        self.embeddings_dir = embeddings_dir
        self.model_name = model_name
        self.model = None
        self.index = None
        self.documents = None
        
    def load_index(self) -> bool:
        """
        Load the prebuilt FAISS index and associated metadata.
        
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        try:
            # Load the sentence transformer model
            self.model = SentenceTransformer(self.model_name)
            
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
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Retrieve the top_k most relevant document chunks for a query.
        
        Args:
            query: Query string to search for
            top_k: Number of top results to return
            
        Returns:
            List of tuples (document_chunk, similarity_score)
        """
        if self.model is None or self.index is None or self.documents is None:
            if not self.load_index():
                return []
        
        try:
            # Encode the query
            query_embedding = self.model.encode([query])
            query_vector = np.array(query_embedding, dtype=np.float32)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_vector, top_k)
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx != -1:  # Valid index
                    document_chunk = self.documents[idx]
                    # Convert FAISS distance to similarity score (higher is better)
                    similarity_score = float(score)
                    results.append((document_chunk, similarity_score))
            
            return results
            
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []
    
    def get_index_info(self) -> dict:
        """
        Get information about the loaded index.
        
        Returns:
            Dictionary containing index information
        """
        if self.index is None:
            return {"status": "No index loaded"}
        
        return {
            "total_vectors": self.index.ntotal,
            "vector_dimension": self.index.d,
            "total_documents": len(self.documents) if self.documents else 0,
            "model_name": self.model_name,
            "embeddings_dir": self.embeddings_dir
        }