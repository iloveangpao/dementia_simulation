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
│   └── dementia_simulation/   # Core package
│       ├── persona/           # Dementia personas and stages (DementiaPersona)
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

## 🎭 Dementia Personas

The system uses the `DementiaPersona` class which provides realistic simulation of dementia patients with:
- **Dementia Stages**: Mild, Moderate, Severe
- **Mood States**: Calm, Confused, Agitated, Anxious, Depressed, Content, Frustrated
- **Memory Profiles**: Configurable short-term retention, long-term clarity, confusion likelihood
- **Personality Traits**: Baseline mood, volatility, social engagement, cooperation level
- **Scenario Context**: Support for situational context (e.g., "In emergency room after a fall")
- **Symptom Descriptions**: Detailed descriptions of memory, orientation, emotion, and insight symptoms for each stage
- **Methods**: `update_mood()`, `should_remember()`, `should_be_confused()`, `should_repeat()`, `get_symptoms_description()`, `add_to_conversation_history()`, `get_context_prompt()`

Example usage:
```python
from dementia_simulation.persona import DementiaPersona, DementiaStage, create_sample_personas

# Create a custom persona with scenario context
persona = DementiaPersona(
    name="Mr. Tan",
    age=75,
    stage=DementiaStage.MODERATE,
    background={
        "profession": "Retired taxi driver",
        "history": "History of hypertension"
    },
    context="In the emergency room after a fall at home. Daughter is waiting outside."
)

# Get symptom descriptions for this stage
symptoms = persona.get_symptoms_description()
# Returns: {"memory": "...", "orientation": "...", "emotion": "...", "insight": "..."}

# Update mood based on trigger (e.g., validation, correction, unfamiliar_person)
new_mood = persona.update_mood(trigger="validation")

# Check if they should remember something from X minutes ago
remembers = persona.should_remember(minutes_ago=15)

# Check if persona should express confusion or repeat themselves
if persona.should_be_confused():
    # Handle confusion in response
    pass
if persona.should_repeat():
    # Repeat last question
    pass

# Add to conversation history
persona.add_to_conversation_history("How are you feeling?", "caregiver")
persona.add_to_conversation_history("I'm not sure... where am I?", "patient")

# Get context prompt for LLM (includes scenario context, symptoms, mood)
system_prompt = persona.get_context_prompt()

# Or use pre-configured sample personas (loads from data/personas/sample_personas.json)
personas = create_sample_personas()

# Load personas from a custom JSON file with random contexts
from dementia_simulation.persona import load_personas_from_json, get_persona_contexts
custom_personas = load_personas_from_json("path/to/custom_personas.json")

# Load personas with a specific context scenario (useful for controlled simulations)
personas_context_0 = load_personas_from_json(
    "data/personas/sample_personas.json",
    context_index=0  # Uses first context for each persona
)

# Get all available contexts for each persona
contexts = get_persona_contexts("data/personas/sample_personas.json")
for name, context_list in contexts.items():
    print(f"{name} has {len(context_list)} possible scenarios")
```

### Sample Personas

The system includes pre-configured sample personas loaded from `data/personas/sample_personas.json`:

#### Mild Dementia - Margaret Chua (78 years old)
- **Background**: Homemaker, widow, lives with daughter
- **Diagnosis**: Mild Cognitive Impairment progressing to early-stage vascular dementia
- **Medications**: Glucosamine, Furosemide, Tolbutamide, Enalapril, multivitamins
- **Current Concerns**: Forgetting names, difficulty with telephone, confused about dates
- **Possible Scenarios**: At home alone, at polyclinic for check-up, at memory clinic, with daughter on weekend, attempting to cook
- **Communication**: Generally coherent, may need gentle reminders

#### Moderate Dementia - Gopal Ramakrishnan (75 years old) 
- **Background**: Retired police officer, divorced, lives with son
- **Diagnosis**: Moderate-stage Alzheimer's disease
- **Medications**: Memantine, Aricept, Metformin, Citalopram
- **Current Concerns**: Repeats questions, doesn't recognize family, wanders at night
- **Possible Scenarios**: At home asking for son, in emergency after wandering, late night confusion, at day care center, at clinic appointment
- **Communication**: Often confused, may not recognize familiar people, repetitive questions

#### Severe Dementia - Rosmah Wati (87 years old)
- **Background**: Retired teacher, widow, lives with daughter and helper
- **Diagnosis**: Severe Alzheimer's disease with behavioral symptoms
- **Medications**: Risperidone (PRN)
- **Current Concerns**: Very limited communication, needs assistance with all activities
- **Possible Scenarios**: Being fed at home, in bed calling for husband, with visiting family, in emergency after seizure, during sundowning hours
- **Communication**: Very simple words or non-verbal, focuses on emotions over facts

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