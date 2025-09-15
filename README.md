# Dementia Simulation Document Processing

A system for processing PDFs and CSV files related to dementia care, creating text chunks, and building a searchable FAISS index for document retrieval.

## Overview

This project provides tools to:
1. Clean and preprocess uploaded PDF and CSV documents
2. Chunk text into manageable passages
3. Generate embeddings using sentence transformers
4. Create a FAISS index for efficient similarity search

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create necessary directories (done automatically):
```
data/
├── uploads/       # Place your PDF and CSV files here
├── processed/     # Processed chunks and metadata
└── index/         # FAISS index and embeddings
```

## Usage

### Step 1: Preprocess Documents

Place your PDF and CSV files in the `data/uploads/` directory, then run the preprocessing notebook:

```bash
jupyter notebook notebooks/preprocess_docs.ipynb
```

The notebook will:
- Extract text from PDFs using PyPDF2
- Process CSV files and combine text columns
- Clean and normalize text content
- Split text into overlapping chunks
- Save processed data to `data/processed/`

If no files are found in uploads, sample data will be created for demonstration.

### Step 2: Build FAISS Index

After preprocessing, run the index building script. Two versions are available:

**Option A: TF-IDF based indexing (works offline):**
```bash
python build_index_tfidf.py
```

**Option B: Sentence transformer based indexing (requires internet):**
```bash
python build_index.py
```

The TF-IDF version is recommended for offline use and creates a functional search index. The sentence transformer version provides better semantic understanding but requires downloading models from Hugging Face.

Both will:
- Load processed text chunks
- Generate embeddings (TF-IDF or sentence transformers)
- Create a FAISS index for similarity search
- Save the index and metadata to `data/index/`

### Step 3: Search Documents

Use the corresponding search utility:

**For TF-IDF index:**
```bash
python search_tfidf.py "memory loss symptoms"
```

**For sentence transformer index:**
```bash
python search.py "memory loss symptoms"
```

## File Structure

```
dementia_simulation/
├── notebooks/
│   └── preprocess_docs.ipynb    # Document preprocessing notebook
├── data/
│   ├── uploads/                 # Input PDFs and CSVs
│   ├── processed/               # Processed chunks and metadata
│   └── index/                   # FAISS index and embeddings
├── build_index.py               # FAISS index creation (sentence transformers)
├── build_index_tfidf.py         # FAISS index creation (TF-IDF, offline)
├── search.py                    # Document search utility (sentence transformers)
├── search_tfidf.py              # Document search utility (TF-IDF)
├── run_preprocessing.py         # Standalone preprocessing script
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Technical Details

### Text Processing
- PDFs are processed using PyPDF2 for text extraction
- CSV files have all text columns combined
- Text is cleaned and normalized (whitespace, special characters)
- Documents are split into overlapping chunks (default: 512 tokens with 50 token overlap)

### Embeddings and Indexing
- TF-IDF version: Uses scikit-learn's TfidfVectorizer for document embeddings
- Sentence transformer version: Uses `all-MiniLM-L6-v2` model (384-dimensional embeddings)
- FAISS IndexFlatIP for cosine similarity search
- Embeddings are L2 normalized for proper cosine similarity

### Supported File Types
- PDF documents (`.pdf`)
- CSV files (`.csv`)

## Configuration

Key parameters can be modified in the scripts:

**Preprocessing (`preprocess_docs.ipynb`)**:
- `CHUNK_SIZE`: Maximum tokens per chunk (default: 512)
- `OVERLAP`: Token overlap between chunks (default: 50)

**Indexing (`build_index.py`)**:
- `MODEL_NAME`: Sentence transformer model (default: "all-MiniLM-L6-v2")
- `BATCH_SIZE`: Embedding generation batch size (default: 32)

## Example Workflow

1. **Upload documents**: Place PDF and CSV files in `data/uploads/`
2. **Preprocess**: Run the Jupyter notebook or `python run_preprocessing.py` to clean and chunk documents
3. **Index**: Run `python build_index_tfidf.py` (offline) or `python build_index.py` (online) to create searchable index
4. **Search**: Use `python search_tfidf.py "your query"` or `python search.py "your query"` to find relevant content

## Dependencies

- pandas: CSV processing
- PyPDF2: PDF text extraction
- nltk: Text tokenization and processing
- sentence-transformers: Embedding generation
- faiss-cpu: Similarity search indexing
- jupyter: Notebook interface

## Troubleshooting

**No files found error**: Make sure PDF or CSV files are in `data/uploads/` directory

**NLTK download error**: The notebook automatically downloads required NLTK data

**Memory issues**: Reduce `BATCH_SIZE` in `build_index.py` for large document collections

**Search not working**: Ensure you've run both preprocessing and indexing steps first