# Build Index

Learn how to create and manage the document search index for the RAG (Retrieval-Augmented Generation) pipeline.

## Overview

The search index enables the system to retrieve relevant information from your knowledge base documents. This tutorial covers both semantic search (FAISS) and keyword search (TF-IDF) approaches.

## Prerequisites

- Dementia Simulation installed and set up
- Documents added to `data/uploads/` directory
- Basic understanding of document retrieval

## Index Types

### FAISS (Semantic Search)

**Best for**: Natural language queries, contextual understanding

- Uses sentence embeddings
- Finds semantically similar content
- Requires internet for initial model download
- Higher quality results

### TF-IDF (Keyword Search)

**Best for**: Offline operation, keyword matching

- Statistical text analysis
- Fast and lightweight
- Works completely offline
- Good for exact term matching

## Step 1: Prepare Documents

### Add Documents

Place your documents in the uploads directory:

```bash
cp /path/to/documents/*.pdf data/uploads/
cp /path/to/documents/*.txt data/uploads/
```

Supported formats:
- **PDF** (`.pdf`) - Research papers, guides, manuals
- **Text** (`.txt`) - Plain text documents
- **CSV** (`.csv`) - Tabular data
- **Markdown** (`.md`) - Documentation

### Verify Documents

Check what's in your uploads:

```bash
ls -lh data/uploads/
```

Example output:
```
-rw-r--r-- 1 user user 2.4M dementia_care_guide.pdf
-rw-r--r-- 1 user user 1.8M communication_strategies.pdf
-rw-r--r-- 1 user user 856K caregiver_handbook.txt
```

## Step 2: Preprocess Documents

Run the preprocessing pipeline:

```bash
python run_preprocessing.py
```

This script:

1. **Extracts text** from PDFs
2. **Cleans** whitespace and formatting
3. **Chunks** into semantic passages (300-500 words)
4. **Adds metadata** (source file, chunk ID)
5. **Saves** to `data/processed/`

Example output:
```
Processing documents...
✓ dementia_care_guide.pdf → 42 chunks
✓ communication_strategies.pdf → 35 chunks
✓ caregiver_handbook.txt → 28 chunks

Total: 3 documents, 105 chunks
Saved to: data/processed/
```

### Verify Preprocessing

Check processed files:

```bash
ls data/processed/
cat data/processed/manifest.json | head -20
```

## Step 3: Build Index

Choose your indexing method:

=== "FAISS (Recommended)"

    Build semantic search index:
    
    ```bash
    python build_index.py
    ```
    
    Process:
    
    1. **Load** processed chunks
    2. **Generate** embeddings with `all-MiniLM-L6-v2`
    3. **Normalize** vectors for cosine similarity
    4. **Build** FAISS index
    5. **Save** index files
    
    Output:
    ```
    Building FAISS index...
    Loading model: all-MiniLM-L6-v2
    Processing 105 chunks...
    Generating embeddings: 100%|██████████| 105/105
    Building index...
    Saved: data/index/faiss.index (384 dims, 105 vectors)
    ```
    
    Time: ~2-5 minutes (first run downloads model)

=== "TF-IDF (Offline)"

    Build keyword-based index:
    
    ```bash
    python build_index_tfidf.py
    ```
    
    Process:
    
    1. **Load** processed chunks
    2. **Tokenize** text
    3. **Calculate** TF-IDF scores
    4. **Build** sparse matrix
    5. **Save** index
    
    Output:
    ```
    Building TF-IDF index...
    Loading chunks from: data/processed/
    Vectorizing 105 documents...
    Vocabulary size: 2,847 terms
    Saved: data/index/tfidf_index.pkl
    ```
    
    Time: ~10-30 seconds

### Index Files Created

After building, you'll have:

```bash
data/index/
├── faiss.index           # FAISS vector index (or tfidf_index.pkl)
├── chunks.json          # Chunk metadata and text
└── model_name.txt       # Embedding model used (FAISS only)
```

## Step 4: Test the Index

Search your knowledge base:

```bash
python search.py "memory loss symptoms"
```

Expected output:
```
Search results for: 'memory loss symptoms'
==================================================
1. Score: 0.892
   Source: dementia_care_guide.pdf
   Text: Memory loss is one of the most common early signs of 
         dementia. Short-term memory is typically affected first, 
         with patients having difficulty remembering recent events...

2. Score: 0.847
   Source: communication_strategies.pdf
   Text: When addressing memory issues, it's important to validate
         the person's feelings rather than correcting them...

3. Score: 0.821
   Source: caregiver_handbook.txt
   Text: Memory problems in dementia progress gradually. Initially,
         the person may forget appointments or recent conversations...
```

### Test Multiple Queries

Try different searches to verify coverage:

```bash
python search.py "communication strategies"
python search.py "how to handle agitation"
python search.py "daily care routines"
python search.py "sundowning behavior"
```

### Adjust Number of Results

Get more or fewer results:

```python
# In search.py or modify command
from search import search_documents

results = search_documents("memory loss", k=10)  # Get top 10 results
```

## Step 5: Integrate with RAG Pipeline

The index is automatically used by the RAG pipeline:

```python
from dementia_simulation.rag import DementiaRAGPipeline

# Initialize pipeline (automatically loads index)
pipeline = DementiaRAGPipeline(
    knowledge_base_path="data/knowledge_base",
    disable_faiss=False  # Use FAISS if available
)

# Generate response with retrieved context
response = pipeline.generate_response(
    patient_message="I keep forgetting things",
    caregiver_message="That's okay, tell me more",
    persona_stage="mild"
)

print(f"Retrieved docs: {response['retrieved_docs_count']}")
```

## Maintenance

### Rebuild Index

When you add new documents:

```bash
# Add new documents
cp new_documents/*.pdf data/uploads/

# Reprocess
python run_preprocessing.py

# Rebuild index
python build_index.py  # or build_index_tfidf.py
```

### Clear and Rebuild

Start fresh:

```bash
# Clear everything
rm -rf data/processed/*
rm -rf data/index/*

# Rebuild from scratch
python run_preprocessing.py
python build_index.py
```

### Check Index Stats

View index information:

```bash
# Check index size
du -sh data/index/

# Count chunks
jq '. | length' data/index/chunks.json

# View sample chunk
jq '.[0]' data/index/chunks.json
```

## Advanced Configuration

### Customize Chunk Size

Edit `run_preprocessing.py`:

```python
# Default: 500 words per chunk, 50 word overlap
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# For larger contexts:
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
```

### Use Different Embedding Model

Edit `build_index.py`:

```python
# Default
MODEL_NAME = "all-MiniLM-L6-v2"

# Better quality (slower, larger)
MODEL_NAME = "all-mpnet-base-v2"

# Faster (lower quality)
MODEL_NAME = "all-MiniLM-L12-v2"
```

### Disable FAISS in Production

Set environment variable:

```bash
export DISABLE_FAISS=1
dementia-sim server
```

Or in `.env`:
```
DISABLE_FAISS=1
```

## Performance Optimization

### Batch Processing

For large document sets, process in batches:

```bash
# Split uploads
mkdir -p data/uploads/batch1 data/uploads/batch2

# Process each batch
for batch in data/uploads/batch*; do
    python run_preprocessing.py --input-dir $batch
done

# Combine and index
python build_index.py
```

### Use GPU Acceleration

If you have a GPU:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")

# Embedding generation automatically uses GPU if available
```

### Reduce Memory Usage

For large indexes:

```bash
# Use smaller embedding model
MODEL_NAME = "all-MiniLM-L6-v2"  # 384 dims, ~80MB

# Instead of
MODEL_NAME = "all-mpnet-base-v2"  # 768 dims, ~420MB
```

## Troubleshooting

### No Results from Search

1. **Check index exists**:
   ```bash
   ls data/index/
   ```

2. **Verify chunks were created**:
   ```bash
   cat data/index/chunks.json | jq '. | length'
   ```

3. **Try rebuilding**:
   ```bash
   python build_index.py
   ```

### FAISS Import Error

Install FAISS:

```bash
pip install faiss-cpu
# Or for GPU
pip install faiss-gpu
```

### Out of Memory

Use TF-IDF instead:

```bash
python build_index_tfidf.py
export DISABLE_FAISS=1
```

### Poor Search Quality

1. **Try FAISS** instead of TF-IDF
2. **Check chunk quality** in `data/processed/`
3. **Add more documents** to improve coverage
4. **Use better embedding model** (see Advanced Configuration)

## Next Steps

- **[Add Dataset](../how-to/add-dataset.md)** - Integrate new document sources
- **[Enable FAISS](../how-to/enable-faiss.md)** - Advanced FAISS configuration
- **[Data Pipeline](../explanation/data-pipeline.md)** - Understand the indexing process
- **[RAG Reference](../reference/modules/rag.md)** - API documentation

## Need Help?

- 📖 [Data Pipeline Explanation](../explanation/data-pipeline.md)
- 🐛 [Report Issues](https://github.com/iloveangpao/dementia_simulation/issues)
- 💬 [Ask Questions](https://github.com/iloveangpao/dementia_simulation/discussions)
