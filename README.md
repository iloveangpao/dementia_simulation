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

5. **Preprocess documents (optional):**
```bash
# Add PDF or CSV files to data/uploads/
# Then run preprocessing to chunk documents
python run_preprocessing.py

# Or use the Jupyter notebook
jupyter notebook notebooks/preprocess_docs.ipynb
```

6. **Build the FAISS index:**
```bash
# Build index from preprocessed documents (auto-detect source)
python build_index.py

# Build from specific source
python build_index.py --source processed    # Use preprocessed documents
python build_index.py --source knowledge_base
python build_index.py --source default

# Specify custom directories
python build_index.py --output-dir embeddings --kb-dir data/knowledge_base
```

### Usage

#### 🖥️ Command Line Interface

**Simple REPL Interface** (for basic training):
```bash
# Start the simple REPL loop
python frontend/cli/main.py

# Features:
# - Interactive caregiver-patient conversation
# - Change personas with /persona <name> <stage>
# - Exit with /quit
# - All conversations logged in logs/ directory
```

**Advanced CLI** (with full RAG pipeline):
```bash
# Start an interactive conversation
poetry run dementia-sim chat

# List available personas
poetry run dementia-sim personas

# Analyze a saved conversation
poetry run dementia-sim analyze data/sessions/conversation_margaret_20240101_120000.json
```

#### 🌐 Web Interface

Start the Streamlit web app:
```bash
poetry run dementia-sim streamlit
# Opens http://localhost:8501
```

Or run directly:
```bash
cd frontend
streamlit run streamlit_app.py
```

**Features:**
- **Two-Panel Layout**: Chat interface on left, monitoring panel on right
- **Chat Interface**: Real-time conversation with AI-powered dementia personas
- **Mood Tracking**: Visual display of patient's current emotional state
- **Performance Monitoring**: Real-time empathy scores and feedback
- **Session Stats**: Track conversation duration, message count, and progress
- **Stage-Specific Tips**: Contextual guidance based on dementia stage
- **Progress Charts**: Visualize improvement over multiple evaluations

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

The system includes two complementary evaluators for assessing caregiver communication:

### CaregiverFeedbackEvaluator (Basic)
Rule-based pattern matching for quick assessment:
- **Reassurance Detection**: Identifies supportive phrases ("okay", "I understand", "take your time")
- **Confrontation Detection**: Identifies problematic language ("no, that's wrong", "you're confused")
- **JSON Score Output**: Returns structured scores, detected patterns, and recommendations
- **Optional LLM Support**: Framework for secondary analysis
- **Use Case**: Real-time feedback during interactions

See [Feedback Evaluator Documentation](docs/feedback_evaluator.md) for details.

### EmpathyEvaluator (Advanced)
Comprehensive multi-dimensional assessment:
- **Validation**: Acknowledging feelings without correction
- **Emotional Support**: Providing comfort and reassurance  
- **Respect & Dignity**: Maintaining the person's dignity
- **Patience**: Handling repetition and confusion gracefully
- **Communication Clarity**: Using clear, simple language
- **Non-confrontational**: Avoiding arguments and corrections
- **Conversation Flow**: Consistency, adaptability, and engagement metrics
- **Use Case**: Post-conversation analysis and training assessment

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

# Run specific test files
poetry run pytest tests/unit/test_persona.py
poetry run pytest tests/test_chat.py

# Run chat orchestration tests specifically
python -m unittest tests.test_chat -v
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

### Preprocessing Documents

To add custom documents (PDFs, CSVs) to the knowledge base:

1. **Place files in the upload directory:**
```bash
# Add your PDF or CSV files
cp your_document.pdf data/uploads/
cp your_data.csv data/uploads/
```

2. **Run preprocessing:**
```bash
# Using the Python script
python run_preprocessing.py

# Or using the Jupyter notebook
jupyter notebook notebooks/preprocess_docs.ipynb
```

The preprocessing pipeline:
- Extracts text from PDFs and CSVs
- Cleans and normalizes the text
- Chunks text into overlapping passages (512 tokens with 50 token overlap)
- Saves processed chunks to `data/processed/`

**Output files:**
- `data/processed/text_chunks.json`: Processed chunks with metadata
- `data/processed/text_chunks.csv`: CSV version for easy viewing
- `data/processed/document_metadata.json`: Document-level metadata

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

The FastAPI server provides comprehensive REST endpoints for chat and evaluation functionality. Full interactive documentation is available at `/docs` when the server is running.

### Chat Endpoint

**POST** `/chat` - Interact with a dementia persona

Accepts flexible schemas for compatibility:
- `message` or `text` - The user's message (required)
- `persona_id` - Specific persona to chat with (optional)
- `session_id` - Session identifier for tracking (optional)

```bash
# Using 'message' field
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How are you feeling today?",
    "persona_id": "persona_1",
    "session_id": "my_session"
  }'

# Using 'text' field (alternative)
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "session_id": "my_session"
  }'
```

**Response:**
```json
{
  "response": "I'm feeling a bit confused...",
  "reply": "I'm feeling a bit confused...",
  "persona_mood": "confused",
  "mood": "confused",
  "confidence_score": 0.85,
  "processing_time": 1.2,
  "model_used": "microsoft/DialoGPT-medium",
  "retrieved_docs": 3,
  "session_id": "my_session"
}
```

### Evaluation Endpoint

**POST** `/evaluate` - Evaluate caregiver empathy and communication

Accepts flexible input formats:
- `transcript` - Simple text transcript to evaluate (recommended for quick evaluation)
- `conversation_history` + `caregiver_responses` - Detailed conversation data

```bash
# Using transcript (simple)
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "I understand how you feel. Let me help you with that."
  }'

# Using detailed conversation history
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_history": [
      {"speaker": "caregiver", "message": "How are you feeling?"},
      {"speaker": "patient", "message": "Confused...", "mood": "confused"}
    ],
    "caregiver_responses": ["How are you feeling?", "I understand..."]
  }'
```

**Response:**
```json
{
  "overall_empathy_score": 0.75,
  "overall_score": 0.75,
  "detailed_scores": {
    "validation": 0.8,
    "emotional_support": 0.7,
    "patience": 0.85,
    "communication_clarity": 0.75,
    "non_confrontational": 0.9
  },
  "flags": {
    "low_validation": false,
    "low_patience": false,
    "needs_improvement": false
  },
  "feedback": ["Good validation of feelings"],
  "strengths": ["Excellent patience"],
  "improvements": ["Could improve emotional support"]
}
```

### Other Endpoints

- **GET** `/health` - Health check
- **GET** `/personas` - List all available personas
- **GET** `/personas/{persona_id}` - Get specific persona details
- **GET** `/sessions/{session_id}` - Get session conversation history
- **DELETE** `/sessions/{session_id}` - Delete a session
- **GET** `/stats` - Get system statistics

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