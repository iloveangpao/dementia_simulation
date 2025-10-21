# Run Locally

Complete guide to setting up the Dementia Simulation platform for local development and testing.

## Prerequisites

- **Python 3.10 or higher**
- **Git**
- **4GB RAM minimum** (8GB recommended)
- **500MB-1GB disk space** for models and data
- Internet connection for initial model downloads

## Installation Methods

Choose your preferred installation method:

=== "Poetry (Recommended)"

    Poetry manages dependencies and virtual environments:
    
    ```bash
    # Install Poetry
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Clone and install
    git clone https://github.com/iloveangpao/dementia_simulation.git
    cd dementia_simulation
    
    # Install dependencies
    poetry install --with dev
    
    # Activate virtual environment
    poetry shell
    ```

=== "pip + venv"

    Using Python's built-in virtual environment:
    
    ```bash
    # Clone repository
    git clone https://github.com/iloveangpao/dementia_simulation.git
    cd dementia_simulation
    
    # Create virtual environment
    python -m venv venv
    
    # Activate virtual environment
    # On Linux/Mac:
    source venv/bin/activate
    # On Windows:
    venv\Scripts\activate
    
    # Install dependencies
    pip install -r requirements.txt
    pip install -r requirements-dev.txt  # For development
    ```

=== "pip (Global)"

    Install directly to your system Python:
    
    ```bash
    git clone https://github.com/iloveangpao/dementia_simulation.git
    cd dementia_simulation
    pip install -r requirements.txt
    ```
    
    !!! warning "Not Recommended for Development"
        Global installation can cause dependency conflicts. Use virtual environment for development.

## Environment Setup

### 1. Initialize Directories

Create necessary directories and configuration:

```bash
dementia-sim setup
```

This creates:

```
dementia_simulation/
├── data/
│   ├── uploads/          # Place PDF/text documents here
│   ├── processed/        # Preprocessed documents
│   ├── knowledge_base/   # Final knowledge base files
│   ├── personas/         # Persona definitions
│   └── sessions/         # Saved conversation sessions
├── embeddings/           # Cached embeddings
└── logs/                 # Application logs
```

### 2. Configure Environment Variables

Edit `.env` file:

```bash
# API Keys (optional - for advanced models)
OPENAI_API_KEY=sk-...                    # OpenAI GPT models
HUGGINGFACE_TOKEN=hf_...                 # HuggingFace models

# Model Configuration
DEFAULT_MODEL=microsoft/DialoGPT-medium  # Conversational model
EMBEDDING_MODEL=all-MiniLM-L6-v2        # For document embeddings

# API Server
API_HOST=localhost
API_PORT=8000

# Logging
LOG_LEVEL=INFO                           # DEBUG, INFO, WARNING, ERROR
```

!!! tip "Offline Mode"
    Default models work offline after initial download. API keys are only needed for GPT-3.5/4 or commercial models.

## Running the Application

### Streamlit Web Interface

Launch the interactive web UI:

```bash
dementia-sim streamlit
```

Features:
- Visual persona selection
- Chat interface with history
- Real-time feedback evaluation
- Session management
- Mood tracking visualization

Access at: [http://localhost:8501](http://localhost:8501)

### CLI Chat Interface

Terminal-based chat:

```bash
dementia-sim chat
```

Interactive features:
- Persona selection menu
- Turn-by-turn conversation
- Immediate feedback scores
- Session saving

### API Server

Start the FastAPI backend:

```bash
dementia-sim server
```

Or with custom options:

```bash
uvicorn dementia_simulation.api.server:app --reload --host 0.0.0.0 --port 8000
```

Available endpoints:
- **Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### All Components Together

Run everything simultaneously:

```bash
# Terminal 1: API Server
dementia-sim server

# Terminal 2: Streamlit UI
dementia-sim streamlit

# Terminal 3: Watch logs
tail -f logs/dementia_sim.log
```

## Adding Documents to Knowledge Base

### 1. Add Source Documents

Place documents in the uploads directory:

```bash
cp /path/to/your/documents/*.pdf data/uploads/
cp /path/to/your/documents/*.txt data/uploads/
```

Supported formats:
- PDF (`.pdf`)
- Plain text (`.txt`)
- CSV (`.csv`)
- Markdown (`.md`)

### 2. Preprocess Documents

Clean and chunk documents:

```bash
python run_preprocessing.py
```

This:
- Extracts text from PDFs
- Cleans and normalizes text
- Splits into semantic chunks
- Saves to `data/processed/`

### 3. Build Search Index

Choose indexing method:

=== "FAISS (Semantic Search)"

    Better quality, requires internet for initial model download:
    
    ```bash
    python build_index.py
    ```
    
    Creates:
    - `data/index/faiss.index` - Vector index
    - `data/index/chunks.json` - Chunk metadata
    - `data/index/model_name.txt` - Embedding model info

=== "TF-IDF (Offline)"

    Faster, works completely offline:
    
    ```bash
    python build_index_tfidf.py
    ```
    
    Creates:
    - `data/index/tfidf_index.pkl` - TF-IDF index
    - `data/index/chunks.json` - Chunk metadata

### 4. Test Search

Verify the index works:

```bash
python search.py "memory loss symptoms"
```

Expected output:
```
Search results for: 'memory loss symptoms'
==================================================
1. Score: 0.892
   Source: dementia_care_guide.pdf
   Text: Memory loss is one of the most common early signs...

2. Score: 0.847
   Source: alzheimers_handbook.pdf
   Text: Short-term memory issues typically appear first...
```

## Development Workflow

### Running Tests

```bash
# All tests
pytest

# Specific test modules
pytest tests/unit/test_persona.py
pytest tests/unit/test_rag_pipeline.py
pytest tests/redteam/test_safety.py

# With coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
poetry run ruff format .

# Lint
poetry run ruff check .

# Type checking
poetry run mypy src --ignore-missing-imports
```

### Pre-commit Hooks

Install pre-commit hooks for automatic checks:

```bash
pre-commit install
pre-commit run --all-files
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:

```bash
# Install in editable mode
pip install -e .

# Or add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### FAISS Index Not Found

Build the index first:

```bash
python build_index.py
# Or for offline
python build_index_tfidf.py
```

### Out of Memory

Reduce batch size in code or use smaller models:

```bash
# In .env
DEFAULT_MODEL=microsoft/DialoGPT-small
```

### Port Already in Use

Kill existing process or use different port:

```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
dementia-sim server --port 8001
```

### Models Not Downloading

Models are cached in:
- **Linux/Mac**: `~/.cache/huggingface/`
- **Windows**: `%USERPROFILE%\.cache\huggingface\`

Manual download:

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

## Performance Optimization

### Use GPU (if available)

PyTorch automatically detects CUDA:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

### Reduce Model Size

Edit `.env`:

```bash
DEFAULT_MODEL=microsoft/DialoGPT-small  # Faster, less memory
EMBEDDING_MODEL=all-MiniLM-L6-v2        # Already optimal
```

### Enable Caching

Response caching is automatic. Clear cache if needed:

```bash
rm -rf embeddings/cache/
```

## Next Steps

- **[Build Index Tutorial](build-index.md)** - Detailed indexing guide
- **[Add Dataset How-to](../how-to/add-dataset.md)** - Integrate new data sources
- **[Architecture](../explanation/architecture.md)** - Understand the system
- **[API Reference](../reference/api/server.md)** - Explore endpoints

## Getting Help

- 📖 [How-to Guides](../how-to/index.md)
- 🐛 [GitHub Issues](https://github.com/iloveangpao/dementia_simulation/issues)
- 💬 [Discussions](https://github.com/iloveangpao/dementia_simulation/discussions)
