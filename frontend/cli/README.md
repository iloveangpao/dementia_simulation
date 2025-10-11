# CLI REPL Frontend

A simple, interactive REPL (Read-Eval-Print Loop) interface for the dementia patient simulation caregiver training system.

## Features

- **Interactive Conversation**: Real-time caregiver-patient dialogue simulation
- **Multiple Personas**: Switch between different patient personas with varying dementia stages
- **Transcript Logging**: All conversations are automatically logged to `logs/` directory with timestamps
- **Easy Exit**: Type `/quit` to gracefully exit the simulation
- **Stage-Specific Responses**: Patient responses vary based on dementia stage (mild, moderate, severe)

## Usage

### Starting the CLI

```bash
cd dementia_simulation
python frontend/cli/main.py
```

### Commands

- **Regular message**: Just type your message and press Enter to interact with the patient
- `/quit` - Exit the simulation
- `/persona <name> <stage>` - Change the patient persona
  - Example: `/persona John Smith moderate`
  - Valid stages: `mild`, `moderate`, `severe`

### Example Session

```
============================================================
    Dementia Patient Simulation - Caregiver Training
============================================================

Instructions:
- Type your message to interact with the patient
- Type '/quit' to exit the simulation
- Type '/persona <name> <stage>' to change patient persona
  (stages: mild, moderate, severe)
- All conversations are logged in the logs/ directory

============================================================

Current Patient: Alice Johnson (Stage: mild)
----------------------------------------
Caregiver: Hello, how are you feeling today?
Patient: Hello there. It's nice to see you.

Current Patient: Alice Johnson (Stage: mild)
----------------------------------------
Caregiver: /persona Robert Wilson severe

Persona changed to: Robert Wilson (severe)

Current Patient: Robert Wilson (Stage: severe)
----------------------------------------
Caregiver: Where are we?
Patient: Where is this place?

Current Patient: Robert Wilson (Stage: severe)
----------------------------------------
Caregiver: /quit

Ending simulation...
Conversation log saved to: logs/conversation_20241011_143022.log
```

## Architecture

### Components

1. **TranscriptLogger**: Handles conversation logging
   - Creates timestamped log files in `logs/` directory
   - Records all interactions with persona info and stages
   - Logs session start/end times

2. **DementiaSimulationREPL**: Main REPL loop
   - Displays welcome message and instructions
   - Shows current persona information
   - Handles user input and commands
   - Integrates with backend patient simulation

3. **Backend Integration**: Uses `backend/patient_simulation.py`
   - `get_patient_response()`: Get patient's response to caregiver input
   - `get_persona_info()`: Get current persona details
   - `set_patient_persona()`: Change patient persona

### Log Format

Log files are created in `logs/` with the format:
```
conversation_YYYYMMDD_HHMMSS.log
```

Example log content:
```
Dementia Simulation Conversation Log
Session started: 2025-10-11T14:58:15.253133
==================================================

[2025-10-11 14:58:31] Persona: Alice Johnson (Stage: mild)
Caregiver: Hello, how are you feeling today?
Patient: Hello there. It's nice to see you.
------------------------------

Session ended: 2025-10-11T14:59:42.123792
```

## Testing

Run the test suite:
```bash
pytest tests/unit/test_cli_repl.py -v
pytest tests/unit/test_patient_simulation.py -v
```

## Development

### Code Quality

The codebase follows strict code quality standards:
- **Linting**: Ruff for Python linting
- **Formatting**: Ruff for code formatting
- **Testing**: Pytest with 100% test coverage for new code

To check code quality:
```bash
# Check formatting
ruff format --check frontend/cli/

# Check linting
ruff check frontend/cli/

# Run tests
pytest tests/unit/test_cli_repl.py -v
```

## Future Enhancements

Possible improvements:
- Integration with the advanced RAG pipeline for more sophisticated responses
- Empathy evaluation feedback during conversations
- Session replay functionality
- Export logs in different formats (JSON, CSV)
- Color-coded output for better readability
- Auto-save sessions at intervals
