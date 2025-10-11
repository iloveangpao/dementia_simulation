#!/usr/bin/env python3
"""
Run the preprocessing pipeline (notebook converted to script for testing)
"""

import os
import pandas as pd
import PyPDF2
import nltk
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Configuration
UPLOAD_DIR = "data/uploads/"
PROCESSED_DIR = "data/processed/"
CHUNK_SIZE = 512
OVERLAP = 50

def create_sample_data():
    """Create sample data for demonstration purposes."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Create sample CSV
    sample_csv_data = {
        'Patient_ID': ['P001', 'P002', 'P003', 'P004', 'P005'],
        'Age': [75, 68, 82, 71, 79],
        'Diagnosis': ['Mild Cognitive Impairment', 'Early-stage Alzheimer\'s', 
                     'Moderate Dementia', 'Vascular Dementia', 'Frontotemporal Dementia'],
        'Symptoms': [
            'Memory lapses, difficulty with complex tasks',
            'Short-term memory loss, confusion with familiar places',
            'Severe memory problems, behavioral changes, difficulty recognizing family',
            'Problems with planning and organizing, mood changes',
            'Personality changes, language difficulties, impaired judgment'
        ],
        'Care_Notes': [
            'Patient benefits from routine and familiar environments',
            'Requires assistance with medication management',
            'Needs constant supervision and assistance with daily activities',
            'Responds well to structured activities and social interaction',
            'Benefits from calm environment and clear, simple communication'
        ]
    }
    
    sample_df = pd.DataFrame(sample_csv_data)
    sample_df.to_csv(os.path.join(UPLOAD_DIR, 'sample_patient_data.csv'), index=False)
    
    # Create sample text file (simulating PDF content)
    sample_text = """
Dementia Care Guidelines

Introduction
Dementia is a syndrome characterized by deterioration in memory, thinking, behavior and the ability to perform everyday activities. While dementia mainly affects older people, it is not a normal part of ageing.

Types of Dementia
Alzheimer's disease is the most common form of dementia and may contribute to 60–70% of cases. Other major forms include vascular dementia, dementia with Lewy bodies, and frontotemporal dementia.

Symptoms and Stages
Early stage symptoms include forgetfulness, losing track of time, and becoming lost in familiar places. Middle stage symptoms involve forgetting recent events and people's names, becoming confused at home, and having difficulty with communication. Late stage symptoms include becoming unaware of time and place, having difficulty recognizing relatives and friends, and needing assisted self-care.

Care Strategies
Effective care strategies include maintaining routine, providing clear and simple instructions, ensuring a safe environment, and promoting social interaction. Family involvement and professional support are crucial for quality care.

Communication Tips
When communicating with dementia patients, speak slowly and clearly, use simple words, maintain eye contact, and be patient. Avoid arguing or correcting, and instead redirect attention to positive activities.

Environmental Considerations
The environment should be safe, familiar, and calming. Remove potential hazards, ensure good lighting, minimize noise, and provide clear pathways. Personal items and photos can help maintain connection to identity.
"""
    
    with open(os.path.join(UPLOAD_DIR, 'dementia_care_guide.txt'), 'w') as f:
        f.write(sample_text)
    
    print("Sample data created in upload directory")

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[^\w\s.,!?;:()\"\'-]', '', text)
    return text.strip()

def process_csv_file(csv_path: str) -> str:
    """Process CSV file and extract text content."""
    try:
        df = pd.read_csv(csv_path)
        text_content = ""
        
        for column in df.columns:
            if df[column].dtype == 'object':
                column_text = df[column].fillna('').astype(str)
                text_content += f"\n{column}: \n" + "\n".join(column_text.tolist()) + "\n"
        
        return clean_text(text_content)
        
    except Exception as e:
        print(f"Error reading CSV {csv_path}: {str(e)}")
        return ""

def process_text_file(txt_path: str) -> str:
    """Process text file content."""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return clean_text(text)
    except Exception as e:
        print(f"Error reading text file {txt_path}: {str(e)}")
        return ""

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> List[str]:
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
            overlap_text = " ".join(overlap_sentences[-2:]) if len(overlap_sentences) > 1 else ""
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
    
    if file_extension == '.csv':
        text = process_csv_file(file_path)
        file_type = 'csv'
    elif file_extension == '.txt':
        text = process_text_file(file_path)
        file_type = 'text'
    else:
        print(f"Unsupported file type: {file_extension}")
        return None
    
    if not text.strip():
        print(f"No text extracted from {file_name}")
        return None
    
    chunks = chunk_text(text)
    
    return {
        'file_name': file_name,
        'file_type': file_type,
        'file_path': file_path,
        'text_length': len(text),
        'num_chunks': len(chunks),
        'chunks': chunks
    }

def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Create sample data if no files exist
    upload_path = Path(UPLOAD_DIR)
    csv_files = list(upload_path.glob("*.csv"))
    txt_files = list(upload_path.glob("*.txt"))
    pdf_files = list(upload_path.glob("*.pdf"))
    
    all_files = csv_files + txt_files + pdf_files
    
    if not all_files:
        print("No files found in uploads directory. Creating sample data...")
        create_sample_data()
        # Recheck for files
        csv_files = list(upload_path.glob("*.csv"))
        txt_files = list(upload_path.glob("*.txt"))
        all_files = csv_files + txt_files
    
    print(f"Found {len(all_files)} files to process")
    
    processed_documents = []
    all_chunks = []
    
    for file_path in tqdm(all_files, desc="Processing documents"):
        doc_data = process_document(str(file_path))
        
        if doc_data:
            processed_documents.append(doc_data)
            
            for i, chunk in enumerate(doc_data['chunks']):
                chunk_data = {
                    'id': f"{doc_data['file_name']}_chunk_{i}",
                    'text': chunk,
                    'source_file': doc_data['file_name'],
                    'file_type': doc_data['file_type'],
                    'chunk_index': i
                }
                all_chunks.append(chunk_data)
    
    print(f"\nProcessing Summary:")
    print(f"- Processed {len(processed_documents)} documents")
    print(f"- Generated {len(all_chunks)} text chunks")
    
    # Save results
    metadata_file = os.path.join(PROCESSED_DIR, 'document_metadata.json')
    with open(metadata_file, 'w') as f:
        json.dump(processed_documents, f, indent=2)
    
    chunks_file = os.path.join(PROCESSED_DIR, 'text_chunks.json')
    with open(chunks_file, 'w') as f:
        json.dump(all_chunks, f, indent=2)
    
    chunks_df = pd.DataFrame(all_chunks)
    chunks_csv = os.path.join(PROCESSED_DIR, 'text_chunks.csv')
    chunks_df.to_csv(chunks_csv, index=False)
    
    print(f"\nSaved processed data:")
    print(f"- Document metadata: {metadata_file}")
    print(f"- Text chunks (JSON): {chunks_file}")
    print(f"- Text chunks (CSV): {chunks_csv}")
    
    print("\nSample chunks:")
    for i, chunk in enumerate(all_chunks[:3]):
        print(f"\nChunk {i+1} (ID: {chunk['id']}):")
        print(f"Source: {chunk['source_file']}")
        print(f"Text: {chunk['text'][:200]}...")

if __name__ == "__main__":
    main()