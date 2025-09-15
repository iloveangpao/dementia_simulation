# Dementia Simulation

A CLI-based dementia patient simulation tool for caregiver training.

## Features

- Interactive REPL interface for caregiver-patient conversations
- Different dementia stages (mild, moderate, severe) with appropriate response patterns
- Multiple patient personas with customizable names and stages
- Automatic conversation logging to `logs/` directory
- Simple commands for persona management and session control

## Usage

Run the simulation:

```bash
python -m frontend.cli
```

### Commands

- Type your message to interact with the patient
- `/quit` - Exit the simulation
- `/persona <name> <stage>` - Change patient persona (stages: mild, moderate, severe)

### Example

```
Current Patient: Alice Johnson (Stage: mild)
----------------------------------------
Caregiver: Hello, how are you today?
Patient: I'm sorry, what did you say?

Current Patient: Alice Johnson (Stage: mild)
----------------------------------------
Caregiver: /persona Bob Wilson severe
Persona changed to: Bob Wilson (Stage: severe)

Current Patient: Bob Wilson (Stage: severe)
----------------------------------------
Caregiver: How are you feeling?
Patient: *stares blankly*
```

## Logs

All conversations are automatically logged to the `logs/` directory with timestamps. Each session creates a new log file with the format `conversation_YYYYMMDD_HHMMSS.log`.

## Structure

- `frontend/cli.py` - Main REPL interface
- `backend/patient_simulation.py` - Patient simulation logic
- `logs/` - Conversation transcripts