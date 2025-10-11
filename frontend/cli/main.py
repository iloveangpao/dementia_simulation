#!/usr/bin/env python3
"""
CLI REPL interface for dementia patient simulation.
Provides interactive caregiver-patient conversation simulation.
"""

import os
import sys
from datetime import datetime

# Add the project root to the path so we can import backend modules
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from backend.patient_simulation import (  # noqa: E402
    get_patient_response,
    get_persona_info,
    set_patient_persona,
)


class TranscriptLogger:
    """Handles logging of conversation transcripts."""

    def __init__(self, logs_dir: str = "logs"):
        """
        Initialize the transcript logger.

        Args:
            logs_dir: Directory to store log files
        """
        self.logs_dir = logs_dir
        self.ensure_logs_dir()
        self.current_session_file = None
        self.start_new_session()

    def ensure_logs_dir(self):
        """Ensure the logs directory exists."""
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    def start_new_session(self):
        """Start a new conversation session with a new log file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.log"
        self.current_session_file = os.path.join(self.logs_dir, filename)

        # Write session header
        with open(self.current_session_file, "w") as f:
            f.write("Dementia Simulation Conversation Log\n")
            f.write(f"Session started: {datetime.now().isoformat()}\n")
            f.write("=" * 50 + "\n\n")

    def log_interaction(
        self,
        persona_name: str,
        stage: str,
        caregiver_input: str,
        patient_response: str,
    ):
        """
        Log a caregiver-patient interaction.

        Args:
            persona_name: Patient persona name
            stage: Dementia stage
            caregiver_input: What the caregiver said
            patient_response: How the patient responded
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.current_session_file, "a") as f:
            f.write(f"[{timestamp}] Persona: {persona_name} (Stage: {stage})\n")
            f.write(f"Caregiver: {caregiver_input}\n")
            f.write(f"Patient: {patient_response}\n")
            f.write("-" * 30 + "\n\n")

    def log_session_end(self):
        """Log the end of a conversation session."""
        with open(self.current_session_file, "a") as f:
            f.write(f"Session ended: {datetime.now().isoformat()}\n")


class DementiaSimulationREPL:
    """Main REPL interface for dementia simulation."""

    def __init__(self):
        """Initialize the REPL interface."""
        self.logger = TranscriptLogger()
        self.running = True

    def display_welcome(self):
        """Display welcome message and instructions."""
        print("=" * 60)
        print("    Dementia Patient Simulation - Caregiver Training")
        print("=" * 60)
        print()
        print("Instructions:")
        print("- Type your message to interact with the patient")
        print("- Type '/quit' to exit the simulation")
        print("- Type '/persona <name> <stage>' to change patient persona")
        print("  (stages: mild, moderate, severe)")
        print("- All conversations are logged in the logs/ directory")
        print()
        print("=" * 60)
        print()

    def display_persona_info(self):
        """Display current persona information."""
        persona_info = get_persona_info()
        print(
            f"Current Patient: {persona_info['name']} (Stage: {persona_info['stage']})"
        )
        print("-" * 40)

    def handle_command(self, user_input: str) -> bool:
        """
        Handle special commands.

        Args:
            user_input: User input string

        Returns:
            True if command was handled, False otherwise
        """
        if user_input.startswith("/quit"):
            print("\nEnding simulation...")
            self.running = False
            return True

        if user_input.startswith("/persona"):
            parts = user_input.split()
            if len(parts) >= 3:
                # Extract name and stage
                stage = parts[-1].lower()
                name = " ".join(parts[1:-1])

                if stage in ["mild", "moderate", "severe"]:
                    set_patient_persona(name, stage)
                    print(f"\nPersona changed to: {name} ({stage})")
                    print()
                else:
                    print("\nInvalid stage. Please use: mild, moderate, or severe")
                    print()
            else:
                print("\nUsage: /persona <name> <stage>")
                print("Example: /persona John Smith mild")
            return True

        return False

    def run(self):
        """Main REPL loop."""
        self.display_welcome()

        try:
            while self.running:
                # Display current persona info
                self.display_persona_info()

                # Get caregiver input
                try:
                    caregiver_input = input("Caregiver: ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\n\nExiting simulation...")
                    break

                # Skip empty input
                if not caregiver_input:
                    continue

                # Handle special commands
                if self.handle_command(caregiver_input):
                    continue

                # Get patient response from backend
                try:
                    patient_response = get_patient_response(caregiver_input)

                    # Display patient response
                    print(f"Patient: {patient_response}")
                    print()

                    # Log the interaction
                    persona_info = get_persona_info()
                    self.logger.log_interaction(
                        persona_info["name"],
                        persona_info["stage"],
                        caregiver_input,
                        patient_response,
                    )

                except Exception as e:
                    print(f"Error getting response: {e}")
                    print()

        finally:
            # Log session end
            self.logger.log_session_end()
            print(f"Conversation log saved to: {self.logger.current_session_file}")


def main():
    """Main entry point for the CLI application."""
    repl = DementiaSimulationREPL()
    repl.run()


if __name__ == "__main__":
    main()
