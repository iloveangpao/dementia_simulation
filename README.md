# Dementia Simulation - Document Retrieval System

A document retrieval system using sentence-transformers (MiniLM) and FAISS for efficient similarity search in dementia-related information.

## Features

- **Document Retrieval**: Uses sentence-transformers with MiniLM model for semantic search
- **Efficient Search**: FAISS vector index for fast similarity search
- **Flexible Input**: Supports text files in `data/processed/` directory
- **Top-K Results**: Retrieve the most relevant document chunks for queries

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Prepare Documents

Place your text documents (`.txt`, `.md`, `.text` files) in the `data/processed/` directory.

### 2. Build the Index

Generate embeddings and build the FAISS index:

```bash
python build_index.py
```

Options:
- `--data-dir`: Directory containing documents (default: `data/processed`)
- `--embeddings-dir`: Directory to save index (default: `embeddings`)
- `--model-name`: Sentence transformer model (default: `all-MiniLM-L6-v2`)
- `--chunk-size`: Maximum characters per chunk (default: 500)
- `--overlap`: Character overlap between chunks (default: 50)

### 3. Use the Retriever

#### Interactive Example
```bash
python example_usage.py
```

#### Programmatic Usage
```python
from src.retriever import Retriever

# Initialize retriever
retriever = Retriever(embeddings_dir="embeddings")

# Load the index
if retriever.load_index():
    # Search for relevant documents
    results = retriever.retrieve("What is dementia?", top_k=5)
    
    for document, score in results:
        print(f"Score: {score:.4f}")
        print(f"Text: {document}")
        print("-" * 40)
```

### 4. Testing

Run the test script with mock data:
```bash
python test_retriever.py
```

## Project Structure

```
dementia_simulation/
├── src/
│   └── retriever.py          # Main Retriever class
├── data/
│   └── processed/            # Input documents
├── embeddings/               # Generated FAISS index and metadata
├── build_index.py           # Index building utility
├── example_usage.py         # Usage example
├── test_retriever.py        # Test script with mock data
└── requirements.txt         # Dependencies
```

## Files Description

- **`src/retriever.py`**: Main Retriever class with FAISS and sentence-transformers integration
- **`build_index.py`**: Utility to create FAISS index from documents
- **`example_usage.py`**: Interactive example demonstrating the retriever
- **`test_retriever.py`**: Test script that works with mock data (useful for testing without internet)

## Dependencies

- `sentence-transformers`: For generating document embeddings
- `faiss-cpu`: For efficient vector similarity search
- `numpy`: For numerical operations

## Notes

- The system chunks documents into smaller pieces for better retrieval accuracy
- Uses cosine similarity for document matching
- Requires internet connection to download the sentence-transformer model on first use
- Once the model is cached locally, no internet connection is needed for operation
