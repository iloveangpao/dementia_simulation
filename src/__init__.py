"""
Dementia Simulation RAG Pipeline

This package provides a Retrieval-Augmented Generation (RAG) pipeline
for simulating patient responses in dementia care scenarios.
"""

from .rag_pipeline import generate_response, create_rag_pipeline, RAGPipeline

__version__ = "1.0.0"
__author__ = "Dementia Simulation Team"

__all__ = [
    "generate_response",
    "create_rag_pipeline", 
    "RAGPipeline"
]