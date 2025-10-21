# Enable FAISS

Configure semantic search with FAISS (Facebook AI Similarity Search) for improved document retrieval quality.

## Overview

FAISS provides:
- **Semantic Search**: Find conceptually similar content, not just keyword matches
- **Fast Similarity**: Efficient nearest-neighbor search in high-dimensional space
- **Scalability**: Handle millions of documents

## Quick Start

### 1. Install FAISS

```bash
# CPU version (most systems)
pip install faiss-cpu

# GPU version (if you have CUDA)
pip install faiss-gpu
```

### 2. Verify Installation

```python
import faiss
print(f"FAISS version: {faiss.__version__}")
```

### 3. Build FAISS Index

```bash
python build_index.py
```

This creates:
- `data/index/faiss.index` - Vector index
- `data/index/chunks.json` - Document metadata
- `data/index/model_name.txt` - Embedding model info

### 4. Test Semantic Search

```bash
python search.py "memory problems in elderly patients"
```

Should return semantically related results about memory loss, cognition, etc.

## Configuration

### Environment Variables

Edit `.env`:

```bash
# Enable FAISS (default if index exists)
DISABLE_FAISS=0

# Embedding model for FAISS
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Index type
FAISS_INDEX_TYPE=Flat  # or IVF, HNSW
```

### Choose Embedding Model

Available models (ordered by quality vs. speed):

```bash
# Fast & Small (default)
EMBEDDING_MODEL=all-MiniLM-L6-v2
# 384 dimensions, ~80MB, fastest

# Balanced
EMBEDDING_MODEL=all-MiniLM-L12-v2
# 384 dimensions, ~120MB

# High Quality
EMBEDDING_MODEL=all-mpnet-base-v2
# 768 dimensions, ~420MB, best quality

# Multilingual
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
# 384 dimensions, supports 50+ languages
```

### Index Types

#### Flat Index (Default)

**Best for**: <100K documents, highest accuracy

```python
# In build_index.py
index = faiss.IndexFlatL2(dimension)
# Or for cosine similarity (recommended)
index = faiss.IndexFlatIP(dimension)
```

Characteristics:
- ✅ Exact search
- ✅ Best quality
- ⚠️ Linear scan (O(n))
- ❌ Not scalable to millions

#### IVF Index (Inverted File)

**Best for**: 100K-10M documents

```python
# build_index.py
nlist = 100  # Number of clusters
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

# Train on data
index.train(embeddings)
index.add(embeddings)
```

Characteristics:
- ✅ Fast search
- ✅ Scalable
- ⚠️ Approximate (99%+ accuracy)
- ⚠️ Requires training

#### HNSW Index (Hierarchical NSW)

**Best for**: Fast queries, moderate size

```python
# build_index.py
M = 32  # Number of connections
index = faiss.IndexHNSWFlat(dimension, M)
index.hnsw.efConstruction = 40
index.hnsw.efSearch = 16
```

Characteristics:
- ✅ Very fast search
- ✅ Good quality
- ⚠️ Higher memory usage
- ✅ No training needed

## Advanced Configuration

### GPU Acceleration

Use GPU for faster indexing and search:

```python
# build_index.py
import faiss

# Move index to GPU
res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)  # 0 = GPU device ID

# Search on GPU
distances, indices = gpu_index.search(query_vectors, k)
```

Environment variable:

```bash
FAISS_USE_GPU=true
FAISS_GPU_ID=0
```

### Index Compression

For large indexes, use compression:

```python
# Product Quantization (lossy compression)
# build_index.py

# Original: 768 dims * 4 bytes = 3KB per vector
# Compressed: 96 * 1 byte = 96 bytes per vector

m = 96  # Subquantizers
nbits = 8  # Bits per subquantizer

quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFPQ(quantizer, dimension, nlist, m, nbits)
```

Saves ~97% space with minimal quality loss.

### Batch Processing

For large document sets:

```python
# build_index.py
batch_size = 1000
index = faiss.IndexFlatIP(dimension)

for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    embeddings = model.encode(batch)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
```

## Optimization Tips

### Choose Right k Value

Number of results to retrieve:

```python
# In retriever code
k = 5  # Default - good for most cases
k = 10  # More context, slower
k = 3  # Faster, might miss relevant docs
```

### Pre-filtering

Filter documents before FAISS search:

```python
# retriever.py
def search_with_filter(query, category=None):
    # Get FAISS results
    scores, indices = index.search(query_vector, k=20)
    
    # Post-filter by category
    if category:
        results = [r for r in results if r['category'] == category]
        return results[:5]
    return results[:5]
```

### Caching

Cache frequent queries:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query_text):
    return search_documents(query_text)
```

## Comparison: FAISS vs TF-IDF

| Feature | FAISS | TF-IDF |
|---------|-------|--------|
| **Search Type** | Semantic | Keyword |
| **Quality** | High | Medium |
| **Speed** | Fast (indexed) | Fast |
| **Offline** | Yes* | Yes |
| **Memory** | Higher | Lower |
| **Setup** | Complex | Simple |

*After initial model download

### When to Use FAISS

✅ Use FAISS when:
- Need semantic understanding
- Have varied query phrasing
- Want best retrieval quality
- Have >1000 documents
- Can afford setup complexity

### When to Use TF-IDF

✅ Use TF-IDF when:
- Need keyword matching
- Completely offline operation
- Limited system resources
- Simple setup required
- Small document set (<500)

## Migration from TF-IDF

Switch from TF-IDF to FAISS:

```bash
# 1. Install FAISS
pip install faiss-cpu

# 2. Build FAISS index
python build_index.py

# 3. Update config
echo "DISABLE_FAISS=0" >> .env

# 4. Restart service
dementia-sim server
```

The system automatically uses FAISS if `data/index/faiss.index` exists.

## Troubleshooting

### FAISS Import Error

```bash
# Reinstall
pip uninstall faiss-cpu faiss-gpu
pip install faiss-cpu
```

### Index Build Fails

**Problem**: Out of memory during indexing

**Solution**:
```bash
# Use batch processing
python build_index.py --batch-size 100

# Or smaller embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Poor Search Quality

**Problem**: Results not relevant

**Solutions**:

1. Use better embedding model:
   ```bash
   EMBEDDING_MODEL=all-mpnet-base-v2
   ```

2. Increase k:
   ```python
   results = search_documents(query, k=10)
   ```

3. Rebuild index:
   ```bash
   rm data/index/faiss.index
   python build_index.py
   ```

### GPU Not Used

**Problem**: FAISS not using GPU

**Check**:
```python
import faiss
print(f"GPU available: {faiss.get_num_gpus()}")
```

**Install GPU version**:
```bash
pip uninstall faiss-cpu
pip install faiss-gpu
```

## Benchmarking

Compare FAISS vs TF-IDF:

```python
import time
from search import search_documents

queries = [
    "memory loss symptoms",
    "how to handle agitation",
    "communication strategies"
]

# Test FAISS
start = time.time()
for q in queries:
    search_documents(q, use_faiss=True, k=5)
faiss_time = time.time() - start

# Test TF-IDF
start = time.time()
for q in queries:
    search_documents(q, use_faiss=False, k=5)
tfidf_time = time.time() - start

print(f"FAISS: {faiss_time:.3f}s")
print(f"TF-IDF: {tfidf_time:.3f}s")
```

## Next Steps

- **[Build Index Tutorial](../tutorials/build-index.md)** - Step-by-step indexing
- **[Data Pipeline](../explanation/data-pipeline.md)** - Understanding retrieval
- **[Retriever API](../reference/modules/retriever.md)** - Module documentation

## Resources

- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [FAISS Wiki](https://github.com/facebookresearch/faiss/wiki)
- [Sentence Transformers](https://www.sbert.net/)

## Need Help?

- 📖 [Data Pipeline Explanation](../explanation/data-pipeline.md)
- 🐛 [Report Issues](https://github.com/iloveangpao/dementia_simulation/issues)
- 💬 [Ask Questions](https://github.com/iloveangpao/dementia_simulation/discussions)
