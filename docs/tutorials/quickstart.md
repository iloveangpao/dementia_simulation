# Quickstart Guide

Get started with Dementia Simulation in just 10 minutes! This tutorial will walk you through installation, setup, and running your first patient simulation.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.10+** installed ([Download Python](https://www.python.org/downloads/))
- **Git** installed ([Download Git](https://git-scm.com/downloads))
- A terminal/command prompt
- (~500MB disk space for models and dependencies)

## Step 1: Clone the Repository

Open your terminal and run:

```bash
git clone https://github.com/iloveangpao/dementia_simulation.git
cd dementia_simulation
```

## Step 2: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

!!! note "Installation Time"
    First-time installation may take 3-5 minutes as it downloads ML models and dependencies.

## Step 3: Initialize the Environment

Set up necessary directories and configuration:

```bash
dementia-sim setup
```

This creates:

- `data/` directories for documents and sessions
- `.env` configuration file
- `logs/` directory

## Step 4: Configure (Optional)

Edit the `.env` file if you want to customize settings:

```bash
# Optional: Add API keys for better models
OPENAI_API_KEY=your_key_here          # For GPT models
HUGGINGFACE_TOKEN=your_token_here     # For HuggingFace models

# Default configuration (works offline)
DEFAULT_MODEL=microsoft/DialoGPT-medium
EMBEDDING_MODEL=all-MiniLM-L6-v2
API_HOST=localhost
API_PORT=8000
LOG_LEVEL=INFO
```

!!! tip "Running Offline"
    The default configuration works completely offline after initial model downloads. No API keys required!

## Step 5: Start Your First Simulation

Choose your preferred interface:

=== "Streamlit Web UI (Recommended)"

    Launch the interactive web interface:
    
    ```bash
    dementia-sim streamlit
    ```
    
    Open your browser to [http://localhost:8501](http://localhost:8501)
    
    The web interface provides:
    
    - Visual persona selection
    - Interactive chat
    - Feedback evaluation
    - Session history

=== "CLI Chat"

    Start a command-line chat session:
    
    ```bash
    dementia-sim chat
    ```
    
    Follow the prompts to:
    
    1. Select a persona (mild, moderate, or severe stage)
    2. Start chatting with the simulated patient
    3. Receive feedback on your responses

=== "API Server"

    Run the REST API server:
    
    ```bash
    dementia-sim server
    ```
    
    Access the API documentation at:
    
    - Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)
    - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
    - OpenAPI spec: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Step 6: Try a Conversation

Here's an example conversation to try:

**You**: "Good morning! How are you feeling today?"

**Patient** (mild stage): "Good morning... I'm doing okay, I think. Though I'm not sure if we've met before?"

**You**: "That's okay. I'm here to help you today. Would you like to talk about anything?"

**Patient**: "I was thinking about my garden... I used to love gardening. Did I already tell you that?"

!!! tip "Empathetic Communication"
    Notice how the patient shows mild memory issues but maintains conversation. Try validating their feelings and avoiding corrections.

## Step 7: View Feedback (CLI Only)

In CLI mode, after each response, you'll see:

```
Feedback Score: 0.85
Type: Supportive
✓ Good use of reassurance
✓ Patient-centered language
! Consider: More validation of feelings
```

## 🎉 Success!

You've completed the quickstart! You now know how to:

- ✅ Install and set up Dementia Simulation
- ✅ Run different interfaces (Web, CLI, API)
- ✅ Interact with simulated patients
- ✅ Receive feedback on your communication

## What's Next?

Now that you're up and running, explore:

- **[Run Locally](run-local.md)** - Detailed setup for development
- **[Build Index](build-index.md)** - Add your own knowledge base documents
- **[Architecture](../explanation/architecture.md)** - Understand how it works
- **[How-to Guides](../how-to/index.md)** - Solve specific tasks

## Common Issues

### Models Not Downloading

If models fail to download:

1. Check your internet connection
2. Models are cached after first download to:
   - Linux/Mac: `~/.cache/huggingface/`
   - Windows: `%USERPROFILE%\.cache\huggingface\`
3. Try running again - downloads will resume

### Port Already in Use

If you see "Address already in use":

```bash
# For Streamlit
dementia-sim streamlit --server.port 8502

# For API server
uvicorn dementia_simulation.api.server:app --port 8001
```

### Command Not Found

If `dementia-sim` command isn't found:

```bash
# Install in development mode
pip install -e .

# Or use Python module syntax
python -m dementia_simulation.cli.main setup
```

## Need Help?

- 📖 Check the [Run Locally](run-local.md) tutorial for more details
- 🐛 [Report issues](https://github.com/iloveangpao/dementia_simulation/issues) on GitHub
- 💬 Ask questions in GitHub Discussions
