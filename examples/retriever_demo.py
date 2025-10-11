#!/usr/bin/env python3
"""
Demo script showing how to use the FAISSRetriever for document retrieval.

This demonstrates the core retrieval functionality that powers the RAG pipeline.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dementia_simulation.retriever import FAISSRetriever


def main():
    """Run retriever demo."""
    print("=" * 60)
    print("FAISS Retriever Demo")
    print("=" * 60)

    # Initialize retriever
    print("\n1. Initializing retriever...")
    retriever = FAISSRetriever(
        index_path="embeddings/faiss_index.index",
        documents_path="embeddings/documents.json",
    )

    # Try to load existing index
    print("\n2. Loading prebuilt index...")
    if retriever.load_index():
        print("   ✓ Successfully loaded prebuilt index")
        stats = retriever.get_stats()
        print(f"   ✓ Model: {stats['model_name']}")
        print(f"   ✓ Documents: {stats['total_documents']}")
        print(f"   ✓ Vectors: {stats['index_total_vectors']}")
    else:
        print("   ✗ No prebuilt index found")
        print("\n   Creating new index from knowledge base...")
        from src.dementia_simulation.retriever import (
            initialize_retriever_with_knowledge_base,
        )

        initialize_retriever_with_knowledge_base(retriever)
        print("   ✓ Index created and saved")

    # Test queries
    print("\n3. Testing retrieval with sample queries...")
    test_queries = [
        "How to communicate with dementia patients?",
        "What are the symptoms of severe dementia?",
        "How to handle patient agitation?",
        "Memory care strategies",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: '{query}'")
        results = retriever.search(query, k=2)

        if results:
            print(f"   Found {len(results)} relevant documents:")
            for j, (doc, score) in enumerate(results, 1):
                text_preview = (
                    doc["text"][:80] + "..." if len(doc["text"]) > 80 else doc["text"]
                )
                print(f"      {j}. Score: {score:.3f}")
                print(f"         {text_preview}")
        else:
            print("   No results found")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
