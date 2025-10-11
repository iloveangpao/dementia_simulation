# Dementia Simulation Chatbot

A comprehensive simulation tool for dementia patients to help caregivers practice empathetic communication skills.

## 🎯 Purpose

This application provides realistic simulations of conversations with dementia patients at different stages (mild, moderate, severe) to help caregivers, family members, and healthcare professionals develop empathetic communication skills and learn appropriate responses to various dementia-related behaviors.

## ✨ Features

- **🎭 Realistic Personas**: Three distinct dementia stages with unique characteristics
- **🤖 AI-Powered Responses**: Uses RAG (Retrieval-Augmented Generation) with knowledge base
- **📊 Empathy Evaluation**: Real-time assessment of communication empathy
- **🌐 Multiple Interfaces**: CLI, Web API, and Streamlit UI
- **📚 Knowledge Base**: Comprehensive dementia care information
- **🔍 FAISS Retrieval**: Semantic search for relevant care information
- **📝 Logging & Analytics**: Detailed conversation and performance tracking

## 🏗️ Architecture

```
dementia_simulation/
├── src/
│   ├── dementia_simulation/   # Core package
│   │   ├── persona/           # Dementia personas and stages (DementiaPersona)
│   │   ├── retriever/         # FAISS-based document retrieval
│   │   ├── rag/               # RAG pipeline with LLaMA2/Mistral
│   │   ├── api/               # FastAPI server
│   │   ├── cli/               # Command-line interface
│   │   ├── evaluator/         # Empathy evaluation system
│   │   └── utils/             # Utilities and logging
│   └── persona.py             # PatientPersona simulation module
├── data/                      # Data storage
│   ├── knowledge_base/        # Dementia care information
│   ├── personas/              # Persona definitions
│   └── sessions/              # Conversation sessions
├── embeddings/                # FAISS indices and embeddings
├── frontend/                  # Streamlit web interface
├── tests/                     # Unit and integration tests
└── logs/                      # Application logs
```

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/iloveangpao/dementia_simulation.git
cd dementia_simulation
```

2. **Install dependencies:**
```bash
# Using Poetry (recommended)
pip install poetry
poetry install

# Or using pip
pip install -r requirements.txt
```

3. **Setup environment:**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (optional)
# OPENAI_API_KEY=your_key_here
# HUGGINGFACE_TOKEN=your_token_here
```

4. **Initialize the application:**
```bash
# Using Poetry
poetry run dementia-sim setup

# Or direct Python
python -m dementia_simulation.cli.main setup
```

5. **Build the FAISS index (optional):**
```bash
# Build index from knowledge base (auto-detect source)
python build_index.py

# Build from specific source
python build_index.py --source knowledge_base
python build_index.py --source default

# Specify custom directories
python build_index.py --output-dir embeddings --kb-dir data/knowledge_base
```

### Usage

#### 🖥️ Command Line Interface

Start an interactive conversation:
```bash
poetry run dementia-sim chat
```

List available personas:
```bash
poetry run dementia-sim personas
```

Analyze a saved conversation:
```bash
poetry run dementia-sim analyze data/sessions/conversation_margaret_20240101_120000.json
```

#### 🌐 Web Interface

Start the Streamlit web app:
```bash
poetry run dementia-sim streamlit
# Opens http://localhost:8501
```

#### 🔗 API Server

Start the FastAPI server:
```bash
poetry run dementia-sim server
# API available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

## 🎭 Dementia Personas

The system includes two persona implementations:

### PatientPersona Module (`src/persona.py`)

A simulation-focused persona for training purposes with:
- **Dementia Stages**: Mild, Moderate, Severe
- **Mood States**: Calm, Agitated, Withdrawn
- **Memory Degradation**: Random key forgetting based on stage
- **Recent Memory**: Time-based forgetting with capacity limits
- **Methods**: `update_mood()`, `forget_recent()`, `add_memory_key()`, `get_memory_key()`

Example usage:
```python
from src.persona import PatientPersona, DementiaStage, MoodState

# Create a patient with moderate dementia
patient = PatientPersona("Alice", DementiaStage.MODERATE, MoodState.CALM)

# Add memory keys
patient.add_memory_key("daughter_name", "Sarah")

# Retrieve memory (may be forgotten randomly)
name = patient.get_memory_key("daughter_name")

# Update mood
new_mood = patient.update_mood()

# Add and forget recent memories
patient.add_recent_memory("Had breakfast")
forgotten = patient.forget_recent()
```

### Sample Personas (DementiaPersona)

### Mild Dementia - Margaret (78 years old)
- **Background**: Retired teacher, widow
- **Symptoms**: Occasional memory lapses, word-finding difficulties
- **Communication**: Generally coherent, may need gentle reminders

### Moderate Dementia - Robert (82 years old) 
- **Background**: Retired engineer, married 55 years
- **Symptoms**: Significant memory problems, confusion about time/place
- **Communication**: May not recognize familiar people, repetitive questions

### Severe Dementia - Eleanor (85 years old)
- **Background**: Former nurse, widow
- **Symptoms**: Severe memory impairment, limited communication
- **Communication**: Very simple words, focuses on emotions over facts

## 📊 Empathy Evaluation

The system evaluates caregiver responses across multiple dimensions:

- **Validation**: Acknowledging feelings without correction
- **Emotional Support**: Providing comfort and reassurance  
- **Respect & Dignity**: Maintaining the person's dignity
- **Patience**: Handling repetition and confusion gracefully
- **Communication Clarity**: Using clear, simple language
- **Non-confrontational**: Avoiding arguments and corrections

## 🧠 Using the RAG Pipeline

The RAG (Retrieval-Augmented Generation) pipeline can be used programmatically in your own code:

### Basic Usage

```python
import asyncio
from dementia_simulation.rag import generate_response
from dementia_simulation.persona.models import create_sample_personas

async def main():
    # Create a persona
    personas = create_sample_personas()
    persona = personas[0]  # Mild dementia - Margaret
    
    # Generate a response
    response = await generate_response(
        user_input="How are you feeling today?",
        persona=persona
    )
    
    print(f"Patient: {response.response_text}")
    print(f"Mood: {response.persona_mood}")
    print(f"Confidence: {response.confidence_score:.2f}")

asyncio.run(main())
```

### Advanced Usage with Custom Pipeline

```python
from dementia_simulation.rag import DementiaRAGPipeline
from dementia_simulation.retriever.faiss_retriever import FAISSRetriever

# Initialize with custom settings
retriever = FAISSRetriever()
pipeline = DementiaRAGPipeline(
    retriever=retriever,
    model_name="microsoft/DialoGPT-medium",
    use_openai=False,
    temperature=0.7
)

# Generate response with conversation history
conversation_history = [
    {"speaker": "caregiver", "message": "Good morning!"},
    {"speaker": "patient", "message": "Good morning dear."}
]

response = await pipeline.generate_response(
    user_input="Would you like some breakfast?",
    persona=persona,
    conversation_history=conversation_history
)
```

### Response Object

The `generate_response` function returns a `RAGResponse` object with:

- `response_text`: The generated patient reply
- `retrieved_documents`: List of relevant knowledge base documents
- `confidence_score`: Confidence in the response (0.0-1.0)
- `persona_mood`: Current mood state of the persona
- `processing_time`: Time taken to generate response (seconds)
- `model_used`: Name of the language model used

## 🛠️ Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_persona.py
```

### Code Quality

```bash
# Lint and format code with ruff
ruff check src/ tests/
ruff format src/ tests/

# Or auto-fix issues
ruff check --fix src/ tests/

# Type checking
poetry run mypy src/
```

### Building FAISS Index

The `build_index.py` utility creates embeddings from your knowledge base:

```bash
# Auto-detect source (tries processed chunks, then knowledge base, then default)
python build_index.py

# Build from knowledge base markdown files
python build_index.py --source knowledge_base --kb-dir data/knowledge_base

# Build from preprocessed chunks
python build_index.py --source processed --processed-dir data/processed

# Use built-in default knowledge base
python build_index.py --source default

# Specify output directory
python build_index.py --output-dir embeddings

# Use different embedding model
python build_index.py --model all-mpnet-base-v2
```

**Options:**
- `--source`: Document source (`auto`, `processed`, `knowledge_base`, `default`)
- `--output-dir`: Directory to save index (default: `embeddings`)
- `--processed-dir`: Location of processed chunks (default: `data/processed`)
- `--kb-dir`: Location of knowledge base files (default: `data/knowledge_base`)
- `--model`: Sentence-transformer model (default: `all-MiniLM-L6-v2`)

The utility creates:
- `embeddings/faiss_index.index`: FAISS vector index
- `embeddings/documents.json`: Document metadata

### Adding New Personas

1. Create persona in `data/personas/`
2. Update `persona/models.py` if needed
3. Add to knowledge base in `data/knowledge_base/`
4. Rebuild the FAISS index with `python build_index.py`
5. Test with unit tests

## 🔧 Configuration

### Environment Variables

```bash
# API Keys (optional)
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_TOKEN=your_hf_token

# Model Configuration
DEFAULT_MODEL=microsoft/DialoGPT-medium
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Server Configuration
API_HOST=localhost
API_PORT=8000
LOG_LEVEL=INFO

# Data Paths
FAISS_INDEX_PATH=embeddings/faiss_index
KNOWLEDGE_BASE_PATH=data/knowledge_base
```

### Models

The system supports multiple language models:

- **Local Models**: Uses HuggingFace transformers (DialoGPT, Mistral, LLaMA2)
- **OpenAI API**: GPT-3.5-turbo, GPT-4 (requires API key)
- **Mock Mode**: Fallback responses for testing without models

## 📚 API Reference

### Chat Endpoint

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How are you feeling today?",
    "persona_id": "persona_1",
    "session_id": "my_session"
  }'
```

### Evaluation Endpoint

```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_history": [...],
    "caregiver_responses": ["How are you feeling?", "I understand..."]
  }'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`poetry run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/), [Streamlit](https://streamlit.io/), and [HuggingFace Transformers](https://huggingface.co/transformers/)
- Dementia care guidelines based on clinical best practices
- FAISS for efficient similarity search
- Thanks to the dementia care community for feedback and insights

## 📞 Support

- 📧 Email: support@dementiasimulation.com
- 💬 GitHub Issues: [Create an issue](https://github.com/iloveangpao/dementia_simulation/issues)
- 📖 Documentation: [Wiki](https://github.com/iloveangpao/dementia_simulation/wiki)

---

**⚠️ Disclaimer**: This is a training simulation tool and should not replace professional medical advice or training. Always consult healthcare professionals for actual dementia care guidance.