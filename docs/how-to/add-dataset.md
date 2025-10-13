# Add Dataset

Learn how to integrate new document sources into your knowledge base for use in the RAG pipeline.

## Overview

Adding a dataset involves:

1. Preparing source documents
2. Placing them in the upload directory
3. Running preprocessing
4. Rebuilding the search index

## Supported Formats

### PDF Documents

**Best for**: Research papers, care guides, clinical documentation

```bash
cp /path/to/research/*.pdf data/uploads/
```

Requirements:
- Text-based PDFs (not scanned images)
- UTF-8 or standard encoding
- Reasonable file size (<50MB per file)

### Plain Text Files

**Best for**: Transcripts, notes, plain documentation

```bash
cp /path/to/notes/*.txt data/uploads/
```

Requirements:
- UTF-8 encoding
- Reasonable structure (paragraphs, sections)

### CSV Files

**Best for**: Structured data, Q&A pairs, tabular information

```bash
cp /path/to/data/*.csv data/uploads/
```

Expected format:
```csv
question,answer,category
"How to handle agitation?","Remain calm and speak in a soothing voice...","behavior"
"What is sundowning?","Increased confusion and agitation in late afternoon...","symptoms"
```

### Markdown Files

**Best for**: Technical documentation, formatted guides

```bash
cp /path/to/docs/*.md data/uploads/
```

Requirements:
- Standard Markdown syntax
- UTF-8 encoding

## Step-by-Step Guide

### 1. Prepare Your Documents

Organize documents by topic or source:

```bash
data/uploads/
├── research_papers/
│   ├── dementia_care_2024.pdf
│   └── communication_strategies.pdf
├── guidelines/
│   ├── clinical_guidelines.pdf
│   └── best_practices.txt
└── qa_pairs/
    └── common_questions.csv
```

### 2. Check Document Quality

Before processing, verify:

```bash
# Check file sizes
du -sh data/uploads/*

# Count files
find data/uploads/ -type f | wc -l

# Verify encodings (for text files)
file data/uploads/*.txt
```

### 3. Run Preprocessing

Process all documents in uploads:

```bash
python run_preprocessing.py
```

This will:
- Extract text from PDFs
- Clean and normalize text
- Split into chunks (default: 500 words)
- Add metadata
- Save to `data/processed/`

Monitor output for errors:
```
Processing documents...
✓ dementia_care_2024.pdf → 45 chunks
✓ communication_strategies.pdf → 32 chunks
✓ clinical_guidelines.pdf → 58 chunks
✗ damaged_file.pdf → Error: Could not extract text

Total: 3 successful, 1 failed
Saved to: data/processed/
```

### 4. Rebuild Search Index

Update the index with new documents:

```bash
# FAISS (semantic search)
python build_index.py

# Or TF-IDF (keyword search)
python build_index_tfidf.py
```

### 5. Verify Addition

Test that new documents are searchable:

```bash
python search.py "new topic from your documents"
```

Check results include content from newly added documents.

## Handling Special Formats

### Scanned PDFs (OCR Required)

For image-based PDFs, use OCR:

```bash
# Install Tesseract OCR
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr
# Mac:
brew install tesseract

# Install Python package
pip install pytesseract pdf2image

# Use OCR preprocessing script
python scripts/ocr_preprocess.py data/uploads/scanned.pdf
```

### Medical Records (HIPAA Compliance)

!!! warning "Privacy & Compliance"
    Remove or redact PHI (Protected Health Information) before uploading:
    
    - Patient names
    - Dates of birth
    - Medical record numbers
    - Social security numbers
    - Contact information

Redaction script example:

```python
import re

def redact_phi(text):
    # Redact common PHI patterns
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN-REDACTED]', text)
    text = re.sub(r'\b\d{2}/\d{2}/\d{4}\b', '[DATE-REDACTED]', text)
    # Add more patterns as needed
    return text
```

### Web Content

Scrape and add web content:

```bash
# Install scraping tools
pip install beautifulsoup4 requests

# Scrape content
python scripts/scrape_content.py "https://example.com/dementia-care" > data/uploads/scraped_content.txt
```

### Video Transcripts

Convert video transcripts:

```bash
# If you have .srt subtitle files
python scripts/convert_srt.py video_transcript.srt > data/uploads/transcript.txt
```

## Incremental Updates

### Adding New Documents to Existing Dataset

```bash
# 1. Add new files
cp new_documents/*.pdf data/uploads/

# 2. Preprocess only new files
python run_preprocessing.py --incremental

# 3. Rebuild index (includes all documents)
python build_index.py
```

### Removing Documents

```bash
# 1. Remove source file
rm data/uploads/outdated_document.pdf

# 2. Clear processed files
rm -rf data/processed/*

# 3. Reprocess remaining documents
python run_preprocessing.py

# 4. Rebuild index
python build_index.py
```

### Updating Existing Documents

```bash
# 1. Replace file
cp updated_version.pdf data/uploads/old_version.pdf

# 2. Clear and reprocess
rm -rf data/processed/*
python run_preprocessing.py

# 3. Rebuild index
python build_index.py
```

## Data Quality Guidelines

### Document Structure

✅ **Good**:
- Clear headings and sections
- Logical paragraph structure
- Consistent terminology
- Complete sentences

❌ **Poor**:
- Wall of text without breaks
- Excessive formatting/tables
- Mixed languages
- Fragments and incomplete thoughts

### Content Guidelines

Include documents that:

- Provide accurate, evidence-based information
- Are relevant to dementia care
- Have clear, readable text
- Are properly formatted

Avoid documents with:

- Outdated medical information
- Poor quality scans
- Heavy use of specialized jargon without explanation
- Duplicate content

### Metadata

Add metadata for better retrieval:

```python
# In run_preprocessing.py, add metadata to chunks
chunk_metadata = {
    'source_file': filename,
    'chunk_id': chunk_id,
    'category': 'clinical_guidelines',  # Add category
    'date_added': '2024-01-15',        # Add date
    'authority': 'WHO',                 # Add source authority
}
```

## Troubleshooting

### PDF Extraction Fails

**Problem**: "Could not extract text from PDF"

**Solutions**:

1. Check if PDF is text-based:
   ```bash
   pdftotext file.pdf - | head
   ```

2. Try alternative extraction:
   ```bash
   pip install pdfminer.six
   ```

3. Use OCR for scanned PDFs (see above)

### Encoding Errors

**Problem**: UnicodeDecodeError during preprocessing

**Solution**:

```bash
# Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 input.txt > output.txt

# Or specify encoding in code
with open('file.txt', 'r', encoding='latin-1') as f:
    content = f.read()
```

### Large Files

**Problem**: Out of memory processing large PDFs

**Solution**:

```bash
# Split large PDF
pdftk large.pdf burst output page_%04d.pdf

# Process each page separately
for page in page_*.pdf; do
    cp $page data/uploads/
done
```

### Poor Search Results

**Problem**: New documents don't show up in search

**Solutions**:

1. Verify preprocessing:
   ```bash
   ls data/processed/
   cat data/processed/manifest.json | jq
   ```

2. Rebuild index from scratch:
   ```bash
   rm -rf data/index/*
   python build_index.py
   ```

3. Test directly:
   ```bash
   python search.py "specific phrase from new document"
   ```

## Batch Processing

For large dataset additions:

```bash
#!/bin/bash
# batch_add_documents.sh

# 1. Download documents
wget -i document_urls.txt -P data/uploads/

# 2. Process in batches of 100
find data/uploads/ -type f | xargs -n 100 -P 4 python run_preprocessing.py --batch

# 3. Rebuild index once
python build_index.py

# 4. Test
python search.py "test query"
```

## Next Steps

- **[Build Index Tutorial](../tutorials/build-index.md)** - Detailed indexing guide
- **[Data Pipeline](../explanation/data-pipeline.md)** - Understand the processing flow
- **[Enable FAISS](enable-faiss.md)** - Improve search quality

## Need Help?

- 📖 [Data Pipeline Explanation](../explanation/data-pipeline.md)
- 🐛 [Report Issues](https://github.com/iloveangpao/dementia_simulation/issues)
- 💬 [Ask Questions](https://github.com/iloveangpao/dementia_simulation/discussions)
