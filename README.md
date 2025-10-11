# Dementia Simulation

A comprehensive platform for dementia patient simulation to help caregivers practice empathetic communication. The system includes interactive chat interfaces, persona management, memory simulation, and caregiver feedback evaluation.

## Features

- **Interactive Chat**: CLI, Streamlit web interface, and API endpoints for caregiver-patient conversations
- **Patient Personas**: Multiple personas with different dementia stages (mild, moderate, severe)
- **Memory Simulation**: Realistic memory degradation and forgetting patterns based on dementia stage
- **Mood Tracking**: Dynamic mood states (calm, agitated, withdrawn) that change during interactions
- **Caregiver Evaluation**: Automated feedback on communication quality, empathy, and technique
- **Document Retrieval**: FAISS-based knowledge base for contextually relevant responses
- **Conversation Logging**: Automatic session recording for review and analysis

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/iloveangpao/dementia_simulation.git
cd dementia_simulation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the environment:
```bash
dementia-sim setup
```

This will create necessary directories and a `.env` configuration file.

### Running the Application

**Option 1: Streamlit Web Interface (Recommended)**
```bash
dementia-sim streamlit
```
Access at: http://localhost:8501

**Option 2: CLI Chat Interface**
```bash
dementia-sim chat
```

**Option 3: API Server**
```bash
dementia-sim server
```
API docs at: http://localhost:8000/docs

## CLI Commands

The `dementia-sim` command provides several subcommands:

- `dementia-sim setup` - Initialize the environment and create configuration files
- `dementia-sim chat` - Start an interactive chat session
- `dementia-sim personas` - List all available patient personas
- `dementia-sim server` - Start the FastAPI backend server
- `dementia-sim streamlit` - Launch the Streamlit web interface
- `dementia-sim analyze <session_file>` - Analyze a saved conversation session

## Project Structure

```
dementia_simulation/
├── src/
│   ├── dementia_simulation/
│   │   ├── api/              # FastAPI server endpoints
│   │   ├── cli/              # CLI interface and commands
│   │   ├── evaluator/        # Caregiver feedback evaluation
│   │   ├── persona/          # Patient persona management
│   │   ├── rag/              # RAG pipeline for response generation
│   │   ├── retriever/        # Document retrieval with FAISS
│   │   └── utils/            # Utility functions
│   ├── chat.py               # Chat system implementation
│   ├── evaluator.py          # Evaluator implementation
│   ├── persona.py            # Persona class
│   ├── rag_pipeline.py       # RAG pipeline
│   └── retriever.py          # Document retriever
├── frontend/
│   ├── streamlit_app.py      # Streamlit web interface
│   ├── app.py                # Alternative Streamlit app
│   └── cli.py                # CLI interface
├── data/
│   ├── uploads/              # Document uploads
│   ├── processed/            # Processed documents
│   ├── knowledge_base/       # Knowledge base files
│   ├── personas/             # Persona definitions
│   └── sessions/             # Saved conversation sessions
├── tests/                    # Test suite
├── notebooks/                # Jupyter notebooks
└── README.md                 # This file
```

## API Endpoints

The FastAPI server provides the following endpoints:

### POST /api/chat
Send a message to the dementia patient simulation.

**Request:**
```json
{
  "text": "Hello, how are you feeling today?",
  "persona_id": "persona_1"
}
```

**Response:**
```json
{
  "patient_reply": "Who are you? I don't recognize you...",
  "persona_mood": "confused",
  "mood_state": "agitated"
}
```

### POST /api/evaluate
Evaluate caregiver performance based on conversation.

**Request:**
```json
{
  "transcript": "I spoke to the patient with calm and gentle words.",
  "caregiver_responses": ["That's okay", "I understand how you feel"]
}
```

**Response:**
```json
{
  "overall_score": 8.5,
  "empathy_score": 9.0,
  "communication_score": 8.0,
  "patience_score": 9.0,
  "feedback": ["Excellent use of reassurance"],
  "improvement_suggestions": ["Continue using supportive language"]
}
```

### GET /api/personas
List all available patient personas.

### POST /api/mood
Update patient mood score.

Visit http://localhost:8000/docs for interactive API documentation.

## Core Components

### Patient Personas
The system simulates different patient personas with varying dementia stages. Each persona includes:
- Name, age, and background information
- Dementia stage (mild, moderate, severe)
- Memory capacity and retention parameters
- Mood state and behavioral patterns
- Personality characteristics

See [PERSONA_README.md](PERSONA_README.md) for detailed persona API documentation.

### Chat System
The chat system orchestrates conversations between caregivers and simulated patients:
- Stores complete conversation history
- Applies forgetting rules based on dementia stage
- Updates mood states dynamically
- Generates contextually appropriate responses
- Supports conversation persistence

### RAG Pipeline
The Retrieval-Augmented Generation pipeline:
- Retrieves relevant dementia care information from the knowledge base
- Constructs persona-aware prompts with conversation context
- Generates patient responses using AI models or rule-based fallbacks
- Ensures responses match the patient's cognitive state and mood

### Caregiver Evaluation
The evaluator analyzes caregiver responses for:
- **Reassurance**: Use of supportive and comforting language
- **Confrontation**: Presence of corrective or confrontational language
- **Overall Quality**: Combined score emphasizing positive communication
- **Feedback**: Specific suggestions for improvement

See [README_evaluator.md](README_evaluator.md) for detailed evaluation API documentation.

## Usage Examples

### Python API Usage

```python
from src.dementia_simulation.persona import PatientPersona, DementiaStage, MoodState

# Create a patient persona
patient = PatientPersona(
    name="Mary Johnson",
    dementia_stage=DementiaStage.MODERATE,
    initial_mood=MoodState.CALM
)

# Simulate a conversation
from src.chat import DementiaSimulationChat

chat = DementiaSimulationChat()
response, state = chat.chat_loop("Hello, how are you feeling today?")
print(f"Patient: {response}")
print(f"Mood: {state['current_mood']}, Confusion: {state['confusion_level']}")
```

### Evaluating Caregiver Responses

```python
from src.evaluator import CaregiverFeedbackEvaluator

evaluator = CaregiverFeedbackEvaluator()
result = evaluator.analyze_feedback("Okay, I understand how you feel.")

print(f"Reassurance Score: {result['scores']['reassurance_score']}")
print(f"Overall Score: {result['scores']['overall_score']}")
print(f"Feedback Type: {result['analysis']['feedback_type']}")
```

## Document Knowledge Base

### Adding Documents

1. Place PDF or text files in `data/uploads/` directory
2. Run preprocessing:
```bash
python run_preprocessing.py
```

3. Build the search index:
```bash
# For offline use (TF-IDF)
python build_index_tfidf.py

# For better semantic search (requires internet)
python build_index.py
```

4. Search documents:
```bash
python search.py "memory loss symptoms"
```

## Configuration

Edit `.env` file to configure:
```bash
OPENAI_API_KEY=your_key_here          # Optional, for OpenAI models
HUGGINGFACE_TOKEN=your_token_here     # Optional, for HuggingFace models
DEFAULT_MODEL=microsoft/DialoGPT-medium
EMBEDDING_MODEL=all-MiniLM-L6-v2
API_HOST=localhost
API_PORT=8000
LOG_LEVEL=INFO
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run specific test modules
python test_persona.py          # Test persona functionality
python test_evaluator.py        # Test caregiver evaluation
python test_retriever.py        # Test document retrieval
python validate_requirements.py # Validate requirements compliance
python test_edge_cases.py       # Edge case testing

# Run unit tests
python -m unittest tests.test_chat -v
python -m unittest tests.test_rag_pipeline -v
```

## Example Scripts

The repository includes several example scripts:

- `example.py` - Automated conversation demonstration
- `example_usage.py` - Interactive examples with multiple personas
- `demo.py` - Complete system demonstration with memory and mood tracking

Run any example:
```bash
python example.py
python example.py interactive  # Interactive mode
```

## Dependencies

Core dependencies:
- **fastapi** - REST API server
- **streamlit** - Web interface
- **click** - CLI framework
- **faiss-cpu** - Vector similarity search
- **sentence-transformers** - Document embeddings
- **transformers** - Language models
- **torch** - Deep learning framework
- **pydantic** - Data validation
- **numpy** - Numerical operations
- **pandas** - Data processing
- **scikit-learn** - Machine learning utilities

See `requirements.txt` and `pyproject.toml` for complete dependency lists.

## Troubleshooting

**Issue: Models not downloading**
- Ensure internet connection for first-time model downloads
- Models are cached locally after first use

**Issue: FAISS index not found**
- Run `python build_index.py` to create the search index
- Or use `python build_index_tfidf.py` for offline operation

**Issue: CLI command not found**
- Install in development mode: `pip install -e .`
- Or use Poetry: `poetry install`

**Issue: Out of memory**
- Reduce batch size in configuration
- Use smaller models (e.g., DialoGPT-small)
- Use TF-IDF indexing instead of sentence transformers

## Best Practices for Dementia Care

The simulation is based on evidence-based dementia care principles:

1. **Use simple, clear language** - Avoid complex sentences and jargon
2. **Be patient with repetition** - Understand that repetition is common
3. **Avoid arguments or confrontation** - Never correct the patient aggressively
4. **Focus on emotions, not facts** - Validate feelings rather than correcting memories
5. **Provide reassurance and comfort** - Use supportive language consistently
6. **Maintain dignity and respect** - Treat the person with respect at all times

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Add tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Follow code style guidelines (black, isort, flake8)
6. Submit a pull request

## License

This project is developed for educational and research purposes in dementia care simulation and caregiver training.

## Acknowledgments

This simulation system is designed to help caregivers develop empathetic communication skills for working with dementia patients. It is not a substitute for professional medical training or advice.

## Additional Documentation

- [PERSONA_README.md](PERSONA_README.md) - Detailed persona system documentation
- [README_evaluator.md](README_evaluator.md) - Caregiver evaluation system documentation

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/iloveangpao/dementia_simulation).
