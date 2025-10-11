"""Retriever module for memory retrieval using FAISS index."""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import faiss


@dataclass
class Document:
    """Represents a document with content and metadata."""
    content: str
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MemoryRetriever:
    """FAISS-based retriever for memory documents."""
    
    def __init__(self, embedding_dim: int = 384):
        """Initialize the retriever with specified embedding dimension."""
        self.embedding_dim = embedding_dim
        self.index = None
        self.documents: List[Document] = []
        self.is_trained = False
    
    def _create_dummy_embedding(self, text: str) -> np.ndarray:
        """Create a dummy embedding for testing purposes."""
        # Simple hash-based embedding for reproducible results
        hash_val = hash(text)
        np.random.seed(abs(hash_val) % (2**32))
        embedding = np.random.normal(0, 1, self.embedding_dim).astype(np.float32)
        return embedding / np.linalg.norm(embedding)  # Normalize
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the retriever."""
        for doc in documents:
            if doc.embedding is None:
                doc.embedding = self._create_dummy_embedding(doc.content)
            self.documents.append(doc)
        
        self._build_index()
    
    def _build_index(self):
        """Build or rebuild the FAISS index."""
        if not self.documents:
            return
        
        # Create embeddings matrix
        embeddings = np.vstack([doc.embedding for doc in self.documents])
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add embeddings to index
        self.index.add(embeddings)
        self.is_trained = True
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """
        Search for similar documents.
        
        Args:
            query: Query string
            k: Number of results to return
            
        Returns:
            List of (document, similarity_score) tuples
        """
        if not self.is_trained or not self.documents:
            return []
        
        # Create query embedding
        query_embedding = self._create_dummy_embedding(query)
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        k = min(k, len(self.documents))
        similarities, indices = self.index.search(query_embedding, k)
        
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx != -1:  # Valid result
                results.append((self.documents[idx], float(similarity)))
        
        return results
    
    def get_document_count(self) -> int:
        """Get the number of documents in the retriever."""
        return len(self.documents)
    
    def clear(self):
        """Clear all documents and reset the index."""
        self.documents = []
        self.index = None
        self.is_trained = False
    
    def get_similar_memories(self, query: str, threshold: float = 0.7) -> List[Document]:
        """
        Get memories similar to the query above a threshold.
        
        Args:
            query: Query string
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            List of similar documents
        """
        results = self.search(query, k=10)
        similar_docs = []
        
        for doc, similarity in results:
            if similarity >= threshold:
                similar_docs.append(doc)
        
        return similar_docs
    
    def update_document(self, index: int, new_content: str):
        """Update a document's content and rebuild index."""
        if 0 <= index < len(self.documents):
            self.documents[index].content = new_content
            self.documents[index].embedding = self._create_dummy_embedding(new_content)
            self._build_index()
    
    def remove_document(self, index: int):
        """Remove a document by index and rebuild index."""
        if 0 <= index < len(self.documents):
            del self.documents[index]
            self._build_index()