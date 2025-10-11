"""
Backend module for dementia patient simulation.
Handles persona management and patient response generation.
"""

import random
from datetime import datetime
from typing import Any, Dict


class DementiaPatient:
    """Simulates a dementia patient with different stages and personas."""

    def __init__(self, persona_name: str = "Default Patient", stage: str = "mild"):
        """
        Initialize a dementia patient simulation.

        Args:
            persona_name: Name of the patient persona
            stage: Dementia stage (mild, moderate, severe)
        """
        self.persona_name = persona_name
        self.stage = stage
        self.conversation_history = []

        # Define response patterns for different stages
        self.stage_responses = {
            "mild": {
                "patterns": [
                    "I'm sorry, what did you say?",
                    "Could you repeat that? I didn't quite catch it.",
                    "That sounds familiar, but I'm not sure...",
                    "I think I understand, but let me think about it.",
                    "Yes, I remember something like that.",
                ],
                "confusion_level": 0.3,
            },
            "moderate": {
                "patterns": [
                    "I don't remember that.",
                    "Who are you again?",
                    "Where am I?",
                    "I want to go home.",
                    "Have you seen my mother?",
                    "What day is it?",
                ],
                "confusion_level": 0.6,
            },
            "severe": {
                "patterns": [
                    "What? I don't understand.",
                    "Who... who are you?",
                    "Where is this place?",
                    "I'm scared.",
                    "Help me.",
                    "I want my mother.",
                ],
                "confusion_level": 0.9,
            },
        }

    def get_response(self, caregiver_input: str) -> str:
        """
        Generate a patient response based on input and dementia stage.

        Args:
            caregiver_input: Input from the caregiver

        Returns:
            Patient response string
        """
        # Store the conversation
        self.conversation_history.append(
            {"timestamp": datetime.now(), "input": caregiver_input}
        )

        # Get stage-specific patterns
        stage_data = self.stage_responses.get(self.stage, self.stage_responses["mild"])
        patterns = stage_data["patterns"]
        confusion_level = stage_data["confusion_level"]

        # Simple response logic - select a random pattern based on confusion level
        if random.random() < confusion_level:
            # More confused response
            response = random.choice(patterns)
        else:
            # More coherent response
            response = self._generate_coherent_response(caregiver_input)

        return response

    def _generate_coherent_response(self, caregiver_input: str) -> str:
        """
        Generate a more coherent response based on input.

        Args:
            caregiver_input: Input from the caregiver

        Returns:
            A more contextual response
        """
        # Simple keyword-based responses
        input_lower = caregiver_input.lower()

        if any(word in input_lower for word in ["hello", "hi", "good morning"]):
            return "Hello there. It's nice to see you."
        elif any(word in input_lower for word in ["how are you", "feeling"]):
            return "I'm doing alright, thank you for asking."
        elif "name" in input_lower:
            return f"My name is {self.persona_name}."
        elif any(word in input_lower for word in ["eat", "food", "hungry"]):
            return "I think I had something earlier, but I'm not sure what it was."
        elif any(word in input_lower for word in ["family", "children"]):
            return "Yes, I have family... I think they're coming to visit soon."
        elif any(word in input_lower for word in ["home", "house"]):
            return "This place is nice, but sometimes I miss my own home."
        else:
            # Default responses based on stage
            stage_data = self.stage_responses[self.stage]
            return random.choice(stage_data["patterns"])

    def get_persona_info(self) -> Dict[str, Any]:
        """Get current persona information."""
        return {
            "name": self.persona_name,
            "stage": self.stage,
            "confusion_level": self.stage_responses[self.stage]["confusion_level"],
        }


# Global patient instance - in a real application, this might be managed differently
current_patient = DementiaPatient("Alice Johnson", "mild")


def get_patient_response(caregiver_input: str) -> str:
    """
    Main interface function for getting patient responses.

    Args:
        caregiver_input: Input from the caregiver

    Returns:
        Patient response
    """
    return current_patient.get_response(caregiver_input)


def get_persona_info() -> Dict[str, Any]:
    """Get current patient persona information."""
    return current_patient.get_persona_info()


def set_patient_persona(name: str, stage: str):
    """
    Set a new patient persona.

    Args:
        name: Patient name
        stage: Dementia stage (mild, moderate, severe)
    """
    global current_patient
    current_patient = DementiaPatient(name, stage)
