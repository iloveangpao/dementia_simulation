# Dementia Simulation Chat System

A Python-based chat system that simulates conversations with patients experiencing dementia. The system includes persona management, memory/forgetting patterns, mood changes, and a RAG (Retrieval-Augmented Generation) pipeline for generating realistic responses.

## Features

- **Chat Loop**: Implements a conversation loop that stores complete chat history
- **Persona State Management**: Tracks and evolves the patient's cognitive and emotional state
- **Forgetting Rules**: Simulates memory degradation patterns typical in dementia
- **Mood System**: Models emotional states and mood changes during conversations
- **RAG Pipeline**: Generates contextually appropriate responses based on persona state
- **Persistence**: Save and load conversation sessions
- **Comprehensive Testing**: Full test suite validating all components

## Quick Start

```python
from src.chat import DementiaSimulationChat

# Initialize the chat system
chat = DementiaSimulationChat()

# Have a conversation
response, persona_state = chat.chat_loop("Hello, how are you feeling today?")
print(f"Patient: {response}")
print(f"Current mood: {persona_state['current_mood']}")
print(f"Confusion level: {persona_state['confusion_level']}")
```

## Running Examples

```bash
# Run automated demonstration
python example.py

# Run interactive chat session
python example.py interactive

# Run tests
python -m unittest tests.test_chat -v
```

## Architecture

### Core Components

1. **PersonaState**: Tracks the patient's cognitive and emotional state
   - Short-term and long-term memory
   - Confusion level and mood
   - Behavioral patterns and preferences

2. **ChatMessage**: Represents individual messages with timestamps and persona snapshots

3. **DementiaSimulationRules**: Implements forgetting and mood change logic
   - Memory degradation patterns
   - Mood triggers and transitions

4. **RAG Pipeline**: Generates responses based on query, context, and persona state
   - Mood-influenced responses
   - Confusion-level appropriate replies
   - Topic-aware response selection

5. **DementiaSimulationChat**: Main chat system orchestrating all components
   - Chat loop with history storage
   - Persona state evolution
   - Conversation persistence

### Chat Loop Flow

1. **Input Processing**: Store user message in chat history
2. **Forgetting Rules**: Apply memory degradation to persona state
3. **Mood Rules**: Update mood based on conversation context
4. **Response Generation**: Use RAG pipeline to generate patient response
5. **State Storage**: Save patient response and updated persona state
6. **Return**: Provide both response and current persona state

## Example Output

```
User: Tell me about your family.
Patient: My husband used to say something like that. But that's nice to think about.
[Mood: happy, Confusion: 0.23]

User: What year is it?
Patient: Is it time for lunch? I thought we just had breakfast.
[Mood: comfortable, Confusion: 0.28]
```

## API Reference

### Main Chat Interface

```python
chat = DementiaSimulationChat()

# Primary chat function - returns (response, persona_state_dict)
response, state = chat.chat_loop(user_input: str) -> Tuple[str, Dict[str, Any]]

# Get full conversation history
history = chat.get_chat_history() -> List[Dict[str, Any]]

# Reset conversation
chat.reset_conversation()

# Save/load conversations
chat.save_conversation(filepath: str)
chat.load_conversation(filepath: str)
```

### Persona State Structure

```python
{
    "short_term_memory": ["recent", "topics"],
    "long_term_memory": ["older", "memories"],
    "forgotten_topics": ["forgotten", "items"],
    "confusion_level": 0.25,  # 0.0 to 1.0
    "current_mood": "happy",  # neutral, happy, sad, agitated, confused, etc.
    "mood_intensity": 0.7,   # 0.0 to 1.0
    "repetition_tendency": 0.3,
    "time_orientation": 0.8,
    "last_topics": ["recent", "conversation", "topics"],
    "preferred_topics": ["family", "past", "home"]
}
```

## Implementation Notes

- The system uses rule-based response generation for predictable, testable behavior
- Randomness is controlled to simulate natural variation in dementia symptoms
- Memory patterns follow research-based forgetting curves
- Mood changes are triggered by conversational context and content
- All components are designed to be easily extensible and modifiable

## Testing

The system includes comprehensive unit tests covering:
- Persona state management and serialization
- Chat message handling
- Forgetting and mood rule application
- RAG pipeline functionality
- Full chat system integration
- Conversation persistence

Run tests with: `python -m unittest tests.test_chat -v`
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
