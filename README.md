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