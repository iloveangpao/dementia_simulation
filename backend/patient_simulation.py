"""
Backend module for dementia patient simulation.
Handles persona management and patient response generation.
"""

from typing import Dict, Any
from datetime import datetime
import random


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
                "confusion_level": 0.3
            },
            "moderate": {
                "patterns": [
                    "I don't remember that.",
                    "Who are you again?",
                    "What day is it today?",
                    "I feel confused...",
                    "Where am I?",
                    "I want to go home.",
                ],
                "confusion_level": 0.6
            },
            "severe": {
                "patterns": [
                    "...",
                    "*looks confused*",
                    "*stares blankly*",
                    "I... I don't...",
                    "*mumbles incoherently*",
                    "*appears agitated*",
                ],
                "confusion_level": 0.9
            }
        }
    
    def get_response(self, caregiver_input: str) -> str:
        """
        Generate a patient response based on the caregiver input and dementia stage.
        
        Args:
            caregiver_input: Input from the caregiver
            
        Returns:
            Patient response string
        """
        # Store the interaction
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "caregiver_input": caregiver_input,
            "stage": self.stage
        })
        
        # Get response patterns for current stage
        stage_data = self.stage_responses.get(self.stage, self.stage_responses["mild"])
        patterns = stage_data["patterns"]
        
        # Simple response generation - could be enhanced with more sophisticated logic
        response = random.choice(patterns)
        
        # Add the response to history
        self.conversation_history[-1]["patient_response"] = response
        
        return response
    
    def get_persona_info(self) -> Dict[str, Any]:
        """Get current persona information."""
        return {
            "name": self.persona_name,
            "stage": self.stage,
            "confusion_level": self.stage_responses[self.stage]["confusion_level"]
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