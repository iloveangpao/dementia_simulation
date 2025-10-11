"""Retriever module for FAISS-based document retrieval."""

from .faiss_retriever import (
    FAISSRetriever,
    create_dementia_knowledge_base,
    initialize_retriever_with_knowledge_base,
)

__all__ = [
    "FAISSRetriever",
    "create_dementia_knowledge_base",
    "initialize_retriever_with_knowledge_base",
]
