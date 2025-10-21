# CLI Module

Command-line interface for the Dementia Simulation platform.

## Overview

The `cli` module provides the `dementia-sim` command with subcommands for:

- Environment setup
- Interactive chat
- Server management
- Persona listing
- Session analysis

## Commands

### setup

Initialize environment and configuration:

```bash
dementia-sim setup
```

Creates:
- Data directories
- `.env` configuration file
- Log directories

### chat

Start interactive chat session:

```bash
dementia-sim chat
```

Features:
- Persona selection menu
- Turn-by-turn conversation
- Real-time feedback
- Session saving

### server

Start FastAPI backend server:

```bash
dementia-sim server
```

Options:
```bash
dementia-sim server --host 0.0.0.0 --port 8000
```

### streamlit

Launch Streamlit web interface:

```bash
dementia-sim streamlit
```

Opens browser to `http://localhost:8501`

### personas

List available personas:

```bash
dementia-sim personas
```

Output:
```
Available personas:
  - mild: Mild Stage (early cognitive changes)
  - moderate: Moderate Stage (noticeable decline)
  - severe: Severe Stage (significant impairment)
```

### analyze

Analyze saved conversation session:

```bash
dementia-sim analyze data/sessions/session_123.json
```

Provides:
- Conversation statistics
- Feedback scores
- Mood progression
- Recommendations

## Module Reference

The CLI module is located in `src/dementia_simulation/cli/`.

**Main Command**: `dementia-sim`

**Subcommands**:

- `setup` - Initialize environment
- `chat` - Start interactive chat
- `server` - Start API server
- `streamlit` - Launch web UI
- `personas` - List personas
- `analyze` - Analyze sessions

**Implementation**:

The CLI is built with Click framework, providing:
- Command routing
- Argument parsing
- Help text generation
- Progress indicators

For full module documentation, see the source code in `cli/main.py` with inline docstrings.

## Related

- **[Quickstart Tutorial](../../tutorials/quickstart.md)** - Get started
- **[Run Locally](../../tutorials/run-local.md)** - Detailed setup
- **[API Server](../api/server.md)** - REST API documentation
