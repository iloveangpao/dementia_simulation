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
│   ├── chat.py                # Chat orchestration system
│   └── dementia_simulation/   # Core package
│       ├── persona/           # Dementia personas and stages
│       ├── retriever/         # FAISS-based document retrieval
│       ├── rag/               # RAG pipeline with LLaMA2/Mistral
│       ├── api/               # FastAPI server
│       ├── cli/               # Command-line interface
│       ├── evaluator/         # Empathy evaluation system
│       └── utils/             # Utilities and logging
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

## 💬 Chat Orchestration System

The `src/chat.py` module implements a sophisticated chat loop that orchestrates conversations with dementia patients. Key features include:

### Core Components

- **PersonaState**: Tracks the patient's cognitive and emotional state
  - Short-term and long-term memory storage
  - Confusion level progression
  - Mood state and intensity
  - Behavioral patterns (repetition, time orientation)
  - Topic tracking

- **ChatMessage**: Represents conversation messages
  - Timestamp tracking
  - Speaker identification (user/patient)
  - Persona state snapshots

- **DementiaSimulationRules**: Implements dementia-specific behaviors
  - **Forgetting Rules**: Simulates memory degradation and forgetting patterns
  - **Mood Rules**: Dynamic mood changes based on conversation context
  - Confusion level progression

- **DementiaSimulationChat**: Main orchestration class
  - `chat_loop()`: Processes user input and generates patient responses
  - Returns both response and current persona state
  - Maintains complete conversation history

### Usage Example

```python
from chat import DementiaSimulationChat

# Initialize chat system
chat = DementiaSimulationChat()

# Process user input
response, persona_state = chat.chat_loop("Hello, how are you today?")

print(f"Patient: {response}")
print(f"Mood: {persona_state['current_mood']}")
print(f"Confusion: {persona_state['confusion_level']}")

# Get conversation history
history = chat.get_conversation_history()

# Reset for new conversation
chat.reset_conversation()
```

## 🎭 Dementia Personas

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

## 🛠️ Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test files
poetry run pytest tests/unit/test_persona.py
poetry run pytest tests/test_chat.py

# Run chat orchestration tests specifically
python -m unittest tests.test_chat -v
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/

# Sort imports
poetry run isort src/ tests/

# Lint code with ruff (recommended)
ruff check src/ tests/

# Or use flake8
poetry run flake8 src/ tests/

# Type checking
poetry run mypy src/
```

### Adding New Personas

1. Create persona in `data/personas/`
2. Update `persona/models.py` if needed
3. Add to knowledge base in `data/knowledge_base/`
4. Test with unit tests

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