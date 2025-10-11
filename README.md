# Dementia Simulation RAG Pipeline

A Retrieval-Augmented Generation (RAG) pipeline for simulating patient responses in dementia care scenarios. This system provides persona-aware responses that help caregivers and medical professionals practice interactions with patients experiencing different stages of dementia.

## Features

- **Document Retrieval**: Retrieves relevant information about dementia care and patient management
- **Persona-Aware Responses**: Generates responses tailored to specific patient personas including:
  - Patient name and age
  - Dementia stage/condition
  - Personality characteristics
- **Conversation History**: Maintains context from previous interactions to provide coherent responses
- **HuggingFace Integration**: Uses state-of-the-art language models (LLaMA2/Mistral) for text generation
- **Fallback Handling**: Graceful degradation when models are not available

## Installation

1. Clone the repository:
```bash
git clone https://github.com/iloveangpao/dementia_simulation.git
cd dementia_simulation
```

2. Install dependencies:
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

### Basic Usage

```python
from src.rag_pipeline import generate_response

# Define a patient persona
persona = {
    "name": "Mary",
    "age": "75",
    "condition": "mild dementia",
    "personality": "gentle and caring"
}

# Conversation history (optional)
history = [
    {
        "user": "Good morning! How are you feeling today?",
        "assistant": "Oh, good morning dear. I'm feeling a bit confused this morning."
    }
]

# Generate a response
response = generate_response(
    user_input="Would you like to have breakfast now?",
    persona=persona,
    history=history
)

print(f"Patient: {response}")
```

### Advanced Usage with RAGPipeline Class

```python
from src.rag_pipeline import RAGPipeline

# Create a pipeline instance
rag = RAGPipeline(model_name="microsoft/DialoGPT-medium")

# Generate response
response = rag.generate_response(user_input, persona, history)
```

## API Reference

### `generate_response(user_input, persona, history)`

Main function for generating patient responses.

**Parameters:**
- `user_input` (str): The caregiver's input message
- `persona` (dict): Patient persona information with keys:
  - `name`: Patient's name
  - `age`: Patient's age 
  - `condition`: Dementia stage/condition
  - `personality`: Personality characteristics
- `history` (list): Previous conversation exchanges

**Returns:**
- `str`: Generated patient response

### `RAGPipeline` Class

Advanced class for customized RAG pipeline usage.

**Methods:**
- `retrieve_documents(query, top_k=3)`: Retrieve relevant documents
- `build_persona_prompt(user_input, persona, history, context_docs)`: Build persona-aware prompts
- `generate_response(user_input, persona, history)`: Generate responses

## Examples

See `example_usage.py` for comprehensive usage examples including:
- Basic conversation simulation
- Different patient personas
- Conversation history utilization
- Error handling scenarios

## Testing

Run the test suite:
```bash
python -m unittest tests.test_rag_pipeline -v
```

## Model Support

The pipeline supports various HuggingFace models:
- **Default**: `microsoft/DialoGPT-medium`
- **Recommended**: LLaMA2, Mistral models for better quality
- **Fallback**: Built-in responses when models are unavailable

## Dependencies

- `transformers`: HuggingFace transformers library
- `torch`: PyTorch for model inference
- `tokenizers`: Tokenization support
- `numpy`: Numerical computations
- `scikit-learn`: Utility functions

## Architecture

The RAG pipeline follows these steps:

1. **Document Retrieval**: Searches for relevant dementia care information
2. **Prompt Construction**: Builds persona-aware prompts with context
3. **Text Generation**: Uses HuggingFace models to generate responses
4. **Post-processing**: Cleans and validates generated responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is developed for educational and research purposes in dementia care simulation.
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
