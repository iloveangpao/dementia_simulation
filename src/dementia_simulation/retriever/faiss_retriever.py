"""
FAISS-based document retriever using sentence transformers.

This module provides functionality to embed and retrieve relevant documents
for the RAG pipeline, specifically tailored for dementia care knowledge.
"""

import json
import os
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np
from loguru import logger
from sentence_transformers import SentenceTransformer


class FAISSRetriever:
    """
    FAISS-based semantic retriever for dementia care knowledge base.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        index_path: Optional[str] = None,
        documents_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize the FAISS retriever.

        Args:
            model_name: Name of the sentence transformer model
            index_path: Path to save/load FAISS index
            documents_path: Path to save/load document metadata
            device: Device to use ('cpu', 'cuda', or None for auto-detect)
        """
        self.model_name = model_name

        # Determine device - use CPU by default, or auto-detect if available
        if device is None:
            try:
                import torch

                # Check if CUDA is available and actually works
                if torch.cuda.is_available():
                    try:
                        # Try to create a small tensor on CUDA to verify it works
                        _ = torch.zeros(1).cuda()
                        device = "cuda"
                    except Exception:
                        # CUDA is reported as available but doesn't work, use CPU
                        device = "cpu"
                else:
                    device = "cpu"
            except ImportError:
                device = "cpu"
        self.device = device

        # Initialize model with explicit device, fallback to CPU on any error
        try:
            self.encoder = SentenceTransformer(model_name, device=self.device)
        except Exception:
            # If initialization fails with specified device, try CPU
            if self.device != "cpu":
                logger.warning(
                    f"Failed to initialize model on {self.device}, falling back to CPU"
                )
                self.device = "cpu"
                self.encoder = SentenceTransformer(model_name, device="cpu")
            else:
                raise

        self.dimension = self.encoder.get_sentence_embedding_dimension()

        # FAISS index
        self.index: Optional[faiss.Index] = None
        self.documents: List[Dict] = []

        # File paths
        self.index_path = index_path or "embeddings/faiss_index.index"
        self.documents_path = documents_path or "embeddings/documents.json"

        # Ensure directories exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.documents_path), exist_ok=True)

        logger.info(
            f"Initialized FAISS retriever with model: {model_name} on device: {self.device}"
        )

    def create_index(self, index_type: str = "flat") -> faiss.Index:
        """
        Create a new FAISS index.

        Args:
            index_type: Type of FAISS index ('flat', 'ivf', 'hnsw')

        Returns:
            Created FAISS index
        """
        if index_type == "flat":
            # Simple flat index for small datasets
            index = faiss.IndexFlatIP(
                self.dimension
            )  # Inner product (cosine similarity)
        elif index_type == "ivf":
            # Inverted file index for larger datasets
            nlist = 100  # number of clusters
            quantizer = faiss.IndexFlatIP(self.dimension)
            index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
        elif index_type == "hnsw":
            # Hierarchical Navigable Small World for fast approximate search
            index = faiss.IndexHNSWFlat(self.dimension, 32)
        else:
            raise ValueError(f"Unknown index type: {index_type}")

        self.index = index
        logger.info(f"Created {index_type} FAISS index with dimension {self.dimension}")
        return index

    def add_documents(self, documents: List[Dict]) -> None:
        """
        Add documents to the knowledge base and index them.

        Args:
            documents: List of document dictionaries with 'text' and metadata
        """
        if self.index is None:
            self.create_index()

        # Extract text for embedding
        texts = [doc.get("text", "") for doc in documents]

        if not texts:
            logger.warning("No texts found in documents")
            return

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.encoder.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,  # Normalize for cosine similarity
        )

        # Add to FAISS index
        if hasattr(self.index, "train") and not self.index.is_trained:
            logger.info("Training FAISS index...")
            self.index.train(embeddings)

        self.index.add(embeddings.astype(np.float32))

        # Store document metadata
        start_idx = len(self.documents)
        for i, doc in enumerate(documents):
            doc_with_id = doc.copy()
            doc_with_id["id"] = start_idx + i
            self.documents.append(doc_with_id)

        logger.info(
            f"Added {len(documents)} documents to index. Total: {len(self.documents)}"
        )

    def search(
        self, query: str, k: int = 5, score_threshold: float = 0.0
    ) -> List[Tuple[Dict, float]]:
        """
        Search for relevant documents.

        Args:
            query: Search query text
            k: Number of results to return
            score_threshold: Minimum similarity score threshold

        Returns:
            List of (document, score) tuples
        """
        if self.index is None or len(self.documents) == 0:
            logger.warning("Index is empty or not initialized")
            return []

        # Encode query
        query_embedding = self.encoder.encode(
            [query], convert_to_numpy=True, normalize_embeddings=True
        )

        # Search FAISS index
        scores, indices = self.index.search(query_embedding.astype(np.float32), k)

        # Prepare results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and score >= score_threshold:  # Valid index and above threshold
                doc = self.documents[idx]
                results.append((doc, float(score)))

        logger.debug(
            f"Found {len(results)} relevant documents for query: '{query[:50]}...'"
        )
        return results

    def save_index(
        self, index_path: Optional[str] = None, documents_path: Optional[str] = None
    ) -> None:
        """
        Save the FAISS index and document metadata to disk.

        Args:
            index_path: Path to save FAISS index (optional)
            documents_path: Path to save documents (optional)
        """
        index_path = index_path or self.index_path
        documents_path = documents_path or self.documents_path

        if self.index is not None:
            # Save FAISS index
            faiss.write_index(self.index, index_path)
            logger.info(f"Saved FAISS index to {index_path}")

            # Save documents metadata
            with open(documents_path, "w", encoding="utf-8") as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.documents)} documents to {documents_path}")
        else:
            logger.warning("No index to save")

    def load_index(
        self, index_path: Optional[str] = None, documents_path: Optional[str] = None
    ) -> bool:
        """
        Load FAISS index and document metadata from disk.

        Args:
            index_path: Path to load FAISS index from (optional)
            documents_path: Path to load documents from (optional)

        Returns:
            True if successful, False otherwise
        """
        index_path = index_path or self.index_path
        documents_path = documents_path or self.documents_path

        try:
            # Load FAISS index
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
                logger.info(f"Loaded FAISS index from {index_path}")
            else:
                logger.warning(f"Index file not found: {index_path}")
                return False

            # Load documents
            if os.path.exists(documents_path):
                with open(documents_path, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
                logger.info(
                    f"Loaded {len(self.documents)} documents from {documents_path}"
                )
            else:
                logger.warning(f"Documents file not found: {documents_path}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False

    def get_stats(self) -> Dict:
        """Get statistics about the current index."""
        stats = {
            "model_name": self.model_name,
            "embedding_dimension": self.dimension,
            "total_documents": len(self.documents),
            "index_trained": self.index.is_trained if self.index else False,
            "index_total_vectors": self.index.ntotal if self.index else 0,
        }
        return stats


def create_dementia_knowledge_base() -> List[Dict]:
    """
    Create a sample knowledge base with dementia care information.

    Returns:
        List of document dictionaries
    """
    documents = [
        {
            "text": "When a person with dementia becomes agitated, it's important to remain calm and speak in a soothing voice. Avoid arguing or trying to reason with them during episodes of confusion.",
            "category": "behavioral_management",
            "severity": ["mild", "moderate", "severe"],
            "topic": "agitation",
        },
        {
            "text": "Memory loss in mild dementia often affects recent events while long-term memories remain intact. Patients may repeat questions or forget recent conversations.",
            "category": "symptoms",
            "severity": ["mild"],
            "topic": "memory_loss",
        },
        {
            "text": "Establishing a daily routine can help reduce anxiety and confusion in dementia patients. Consistent meal times, activities, and sleep schedules provide comfort.",
            "category": "care_strategies",
            "severity": ["mild", "moderate", "severe"],
            "topic": "routine",
        },
        {
            "text": "Validation therapy involves acknowledging the person's feelings without correcting their reality. This approach often reduces distress and improves cooperation.",
            "category": "communication",
            "severity": ["moderate", "severe"],
            "topic": "validation",
        },
        {
            "text": "In moderate dementia, patients may have difficulty recognizing familiar faces or places. They might confuse family members or think they're in a different time period.",
            "category": "symptoms",
            "severity": ["moderate"],
            "topic": "recognition_issues",
        },
        {
            "text": "Severe dementia often involves significant language difficulties. Patients may speak very little or use words inappropriately. Non-verbal communication becomes crucial.",
            "category": "symptoms",
            "severity": ["severe"],
            "topic": "communication_difficulties",
        },
        {
            "text": "Sundowning refers to increased confusion and agitation in the late afternoon or evening. This is common in dementia and can be managed with proper lighting and calming activities.",
            "category": "behavioral_management",
            "severity": ["moderate", "severe"],
            "topic": "sundowning",
        },
        {
            "text": "Personal care assistance becomes necessary as dementia progresses. Approach bathing and dressing with patience, maintaining dignity and allowing as much independence as possible.",
            "category": "daily_care",
            "severity": ["moderate", "severe"],
            "topic": "personal_care",
        },
        {
            "text": "Reminiscence therapy using familiar objects, photos, or music from the person's past can stimulate memory and improve mood. Focus on positive memories and experiences.",
            "category": "therapeutic_activities",
            "severity": ["mild", "moderate"],
            "topic": "reminiscence",
        },
        {
            "text": "Safety concerns increase with dementia progression. Remove hazards, install locks on dangerous items, and consider monitoring systems to prevent wandering.",
            "category": "safety",
            "severity": ["moderate", "severe"],
            "topic": "home_safety",
        },
        {
            "text": "Family caregivers need support and respite care. Dementia care is demanding and caregiver burnout is common. Regular breaks and support groups are essential.",
            "category": "caregiver_support",
            "severity": ["mild", "moderate", "severe"],
            "topic": "respite_care",
        },
        {
            "text": "Nutrition management becomes challenging as dementia progresses. Patients may forget to eat, lose appetite, or have difficulty swallowing. Monitor weight and hydration.",
            "category": "daily_care",
            "severity": ["moderate", "severe"],
            "topic": "nutrition",
        },
    ]

    return documents


def initialize_retriever_with_knowledge_base(retriever: FAISSRetriever) -> None:
    """
    Initialize a retriever with the dementia knowledge base.

    Args:
        retriever: FAISSRetriever instance to populate
    """
    # Try to load existing index first
    if not retriever.load_index():
        logger.info("No existing index found, creating new one...")

        # Create knowledge base
        documents = create_dementia_knowledge_base()

        # Add documents to retriever
        retriever.add_documents(documents)

        # Save the index
        retriever.save_index()

        logger.info("Knowledge base initialized and saved")
    else:
        logger.info("Loaded existing knowledge base")


if __name__ == "__main__":
    # Example usage
    retriever = FAISSRetriever()
    initialize_retriever_with_knowledge_base(retriever)

    # Test search
    results = retriever.search("How to handle agitation in dementia patients?", k=3)

    print("Search Results:")
    for doc, score in results:
        print(f"Score: {score:.3f}")
        print(f"Text: {doc['text']}")
        print(f"Category: {doc['category']}")
        print("-" * 50)
