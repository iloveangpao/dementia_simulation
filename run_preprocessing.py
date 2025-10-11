#!/usr/bin/env python3
"""
Run the preprocessing pipeline (notebook converted to script for testing)
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

import nltk
import pandas as pd
import PyPDF2
from tqdm import tqdm

# Download required NLTK data
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

from nltk.tokenize import sent_tokenize, word_tokenize

# Configuration
UPLOAD_DIR = "data/uploads/"
PROCESSED_DIR = "data/processed/"
CHUNK_SIZE = 512
OVERLAP = 50


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,;:!?\'"()-]', "", text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def process_pdf_file(pdf_path: str) -> str:
    """Extract text from PDF file."""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

    return clean_text(text)


def process_csv_file(csv_path: str) -> str:
    """Process CSV file and extract text content."""
    try:
        df = pd.read_csv(csv_path)
        # Convert all columns to text and combine
        text_parts = []
        for col in df.columns:
            text_parts.append(f"{col}: {' '.join(df[col].astype(str).tolist())}")
        text = " ".join(text_parts)
        return clean_text(text)
    except Exception as e:
        print(f"Error reading CSV {csv_path}: {e}")
        return ""


def chunk_text(
    text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP
) -> List[str]:
    """Split text into overlapping chunks."""
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    current_length = 0

    for sentence in sentences:
        sentence_length = len(word_tokenize(sentence))

        if current_length + sentence_length > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())

            overlap_sentences = sent_tokenize(current_chunk)
            overlap_text = (
                " ".join(overlap_sentences[-2:]) if len(overlap_sentences) > 1 else ""
            )
            overlap_length = len(word_tokenize(overlap_text))

            if overlap_length <= overlap:
                current_chunk = overlap_text + " " + sentence
                current_length = overlap_length + sentence_length
            else:
                current_chunk = sentence
                current_length = sentence_length
        else:
            current_chunk += " " + sentence if current_chunk else sentence
            current_length += sentence_length

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def process_document(file_path: str) -> Dict[str, Any]:
    """Process a single document and return metadata and chunks."""
    file_extension = Path(file_path).suffix.lower()
    file_name = Path(file_path).name

    if file_extension == ".pdf":
        text = process_pdf_file(file_path)
        file_type = "pdf"
    elif file_extension == ".csv":
        text = process_csv_file(file_path)
        file_type = "csv"
    else:
        print(f"Unsupported file type: {file_extension}")
        return None

    if not text.strip():
        print(f"No text extracted from {file_name}")
        return None

    chunks = chunk_text(text)

    return {
        "file_name": file_name,
        "file_type": file_type,
        "file_path": file_path,
        "text_length": len(text),
        "num_chunks": len(chunks),
        "chunks": chunks,
    }


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Process all uploaded files
    upload_path = Path(UPLOAD_DIR)
    csv_files = list(upload_path.glob("*.csv"))
    pdf_files = list(upload_path.glob("*.pdf"))

    all_files = csv_files + pdf_files

    if not all_files:
        print(f"No PDF or CSV files found in {UPLOAD_DIR}")
        print("Please add files to the upload directory and run again.")
        return

    print(f"Found {len(all_files)} files to process")

    processed_documents = []
    all_chunks = []

    for file_path in tqdm(all_files, desc="Processing documents"):
        doc_data = process_document(str(file_path))

        if doc_data:
            processed_documents.append(doc_data)

            for i, chunk in enumerate(doc_data["chunks"]):
                chunk_data = {
                    "id": f"{doc_data['file_name']}_chunk_{i}",
                    "text": chunk,
                    "source_file": doc_data["file_name"],
                    "file_type": doc_data["file_type"],
                    "chunk_index": i,
                }
                all_chunks.append(chunk_data)

    print("\nProcessing Summary:")
    print(f"- Processed {len(processed_documents)} documents")
    print(f"- Generated {len(all_chunks)} text chunks")

    # Save results
    metadata_file = os.path.join(PROCESSED_DIR, "document_metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(processed_documents, f, indent=2)

    chunks_file = os.path.join(PROCESSED_DIR, "text_chunks.json")
    with open(chunks_file, "w") as f:
        json.dump(all_chunks, f, indent=2)

    chunks_df = pd.DataFrame(all_chunks)
    chunks_csv = os.path.join(PROCESSED_DIR, "text_chunks.csv")
    chunks_df.to_csv(chunks_csv, index=False)

    print("\nSaved processed data:")
    print(f"- Document metadata: {metadata_file}")
    print(f"- Text chunks (JSON): {chunks_file}")
    print(f"- Text chunks (CSV): {chunks_csv}")

    print("\nSample chunks:")
    for i, chunk in enumerate(all_chunks[:3]):
        print(f"\nChunk {i + 1} (ID: {chunk['id']}):")
        print(f"Source: {chunk['source_file']}")
        print(f"Text: {chunk['text'][:200]}...")


if __name__ == "__main__":
    main()
