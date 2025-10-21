# Retriever Module

Document search and indexing for the RAG pipeline.

## Overview

The `retriever` module handles:

- FAISS semantic search
- TF-IDF keyword search
- Document chunking
- Index management
- Relevance scoring

## Quick Example

```python
from dementia_simulation.retriever import DocumentRetriever

# Initialize retriever
retriever = DocumentRetriever(
    index_path="data/index",
    use_faiss=True
)

# Search documents
results = retriever.search(
    query="memory loss symptoms",
    k=5
)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Source: {result['source_file']}")
    print(f"Text: {result['text'][:200]}...")
    print()
```

## Module Reference

The retriever module is located in `src/dementia_simulation/retriever/`.

**Key Classes**:

- `DocumentRetriever` - Main retrieval class with FAISS/TF-IDF support
- `FAISSIndex` - FAISS vector index wrapper
- `TFIDFIndex` - TF-IDF sparse index wrapper
- `DocumentChunker` - Text chunking utilities

**Key Functions**:

- `build_faiss_index()` - Create FAISS vector index
- `build_tfidf_index()` - Create TF-IDF keyword index
- `search()` - Search for relevant documents

For full module documentation, see the source code with inline docstrings.

## Related

- **[Data Pipeline](../../explanation/data-pipeline.md)** - Processing workflow
- **[Build Index Tutorial](../../tutorials/build-index.md)** - Create search index
- **[Enable FAISS](../../how-to/enable-faiss.md)** - Setup semantic search
