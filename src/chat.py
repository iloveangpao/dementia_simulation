"""
Dementia Simulation Chat System

This module implements a chat loop that simulates conversations with a patient
experiencing dementia. It includes persona management, memory/forgetting patterns,
mood changes, and integrates with a RAG pipeline for generating responses.
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random
import json


@dataclass
class PersonaState:
    """Represents the current state of the simulated patient's persona."""
    
    # Memory and cognitive state
    short_term_memory: List[str] = field(default_factory=list)
    long_term_memory: List[str] = field(default_factory=list)
    forgotten_topics: List[str] = field(default_factory=list)
    confusion_level: float = 0.0  # 0.0 to 1.0
    
    # Emotional/mood state
    current_mood: str = "neutral"  # neutral, happy, sad, agitated, confused, etc.
    mood_intensity: float = 0.5  # 0.0 to 1.0
    
    # Behavioral patterns
    repetition_tendency: float = 0.3  # How likely to repeat things
    time_orientation: float = 0.8  # How well oriented to current time (0.0 to 1.0)
    
    # Conversation patterns
    last_topics: List[str] = field(default_factory=list)
    preferred_topics: List[str] = field(default_factory=lambda: ["family", "past", "home"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert persona state to dictionary for serialization."""
        return {
            "short_term_memory": self.short_term_memory,
            "long_term_memory": self.long_term_memory,
            "forgotten_topics": self.forgotten_topics,
            "confusion_level": self.confusion_level,
            "current_mood": self.current_mood,
            "mood_intensity": self.mood_intensity,
            "repetition_tendency": self.repetition_tendency,
            "time_orientation": self.time_orientation,
            "last_topics": self.last_topics,
            "preferred_topics": self.preferred_topics
        }


@dataclass
class ChatMessage:
    """Represents a single message in the chat history."""
    timestamp: datetime
    speaker: str  # "user" or "patient" 
    content: str
    persona_state_snapshot: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "speaker": self.speaker,
            "content": self.content,
            "persona_state_snapshot": self.persona_state_snapshot
        }


class DementiaSimulationRules:
    """Implements the forgetting and mood rules for dementia simulation."""
    
    @staticmethod
    def apply_forgetting_rules(persona: PersonaState, new_input: str) -> PersonaState:
        """Apply memory degradation and forgetting patterns."""
        # Simulate short-term memory limitations
        if len(persona.short_term_memory) > 3:
            # Sometimes forget earlier items in short-term memory
            if random.random() < 0.3:
                forgotten_item = persona.short_term_memory.pop(0)
                if forgotten_item not in persona.forgotten_topics:
                    persona.forgotten_topics.append(forgotten_item)
        
        # Add new input to short-term memory
        persona.short_term_memory.append(new_input)
        
        # Sometimes transfer to long-term memory (but not always)
        if len(persona.short_term_memory) > 2 and random.random() < 0.4:
            item_to_transfer = persona.short_term_memory.pop(0)
            if item_to_transfer not in persona.long_term_memory:
                persona.long_term_memory.append(item_to_transfer)
        
        # Gradually increase confusion based on conversation length
        persona.confusion_level = min(1.0, persona.confusion_level + random.uniform(0.0, 0.1))
        
        return persona
    
    @staticmethod
    def apply_mood_rules(persona: PersonaState, conversation_context: List[str]) -> PersonaState:
        """Apply mood changes based on conversation context and persona state."""
        mood_triggers = {
            "family": ("happy", 0.7),
            "past": ("nostalgic", 0.6), 
            "confusion": ("agitated", 0.8),
            "lost": ("sad", 0.6),
            "home": ("comfortable", 0.5)
        }
        
        # Analyze recent conversation for mood triggers
        recent_context = " ".join(conversation_context[-3:]).lower()
        
        for trigger, (mood, intensity) in mood_triggers.items():
            if trigger in recent_context:
                persona.current_mood = mood
                persona.mood_intensity = intensity
                break
        else:
            # Default mood drift
            if random.random() < 0.2:
                moods = ["neutral", "confused", "content", "restless"]
                persona.current_mood = random.choice(moods)
                persona.mood_intensity = random.uniform(0.3, 0.7)
        
        return persona


def rag_pipeline(query: str, context: List[str], persona_state: PersonaState) -> str:
    """
    Mock RAG (Retrieval-Augmented Generation) pipeline for generating dementia-simulated responses.
    
    In a real implementation, this would integrate with a language model and knowledge base.
    For now, this provides rule-based responses that simulate dementia patterns.
    """
    
    # Simulate response patterns based on persona state
    response_templates = {
        "high_confusion": [
            "I'm not sure what you mean... where am I?",
            "That sounds familiar, but I can't quite remember...",
            "Is it time for lunch? I thought we just had breakfast.",
            "Who are you again? You seem nice."
        ],
        "repetitive": [
            "I need to go home. When can I go home?",
            "Have you seen my mother? She should be here by now.",
            "I think I left something important somewhere...",
            "This place looks different than I remember."
        ],
        "family_focused": [
            "That reminds me of my children when they were young.",
            "My husband used to say something like that.",
            "We had such wonderful times together as a family.",
            "I wonder how everyone is doing at home."
        ],
        "time_confused": [
            "Is it morning already? Time goes so fast.",
            "I remember when things were different...",
            "What year is it again?",
            "Everything feels like it happened yesterday."
        ]
    }
    
    # Choose response category based on persona state
    if persona_state.confusion_level > 0.7:
        category = "high_confusion"
    elif persona_state.repetition_tendency > 0.6 and random.random() < 0.5:
        category = "repetitive"
    elif any(topic in query.lower() for topic in ["family", "children", "mother", "father"]):
        category = "family_focused"
    elif persona_state.time_orientation < 0.5:
        category = "time_confused"
    else:
        # Generate more contextual response
        if "home" in query.lower():
            return "I'd like to go home now. This isn't my home, is it?"
        elif "remember" in query.lower():
            return "I try to remember, but sometimes things get mixed up in my mind."
        else:
            category = "high_confusion"
    
    # Add mood influence to response
    response = random.choice(response_templates[category])
    
    if persona_state.current_mood == "agitated":
        response = "I don't understand! " + response
    elif persona_state.current_mood == "sad":
        response = response + " It makes me feel sad."
    elif persona_state.current_mood == "happy":
        response = response + " But that's nice to think about."
    
    return response


class DementiaSimulationChat:
    """Main chat system for dementia simulation."""
    
    def __init__(self):
        self.persona_state = PersonaState()
        self.chat_history: List[ChatMessage] = []
        self.rules = DementiaSimulationRules()
    
    def chat_loop(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """
        Main chat loop that processes user input and returns patient response with persona state.
        
        Args:
            user_input: The message from the user/caregiver
            
        Returns:
            Tuple of (patient_response, persona_state_dict)
        """
        # Store user message in history
        user_message = ChatMessage(
            timestamp=datetime.now(),
            speaker="user",
            content=user_input
        )
        self.chat_history.append(user_message)
        
        # Apply forgetting rules based on new input
        self.persona_state = self.rules.apply_forgetting_rules(self.persona_state, user_input)
        
        # Extract conversation context for mood analysis
        recent_messages = [msg.content for msg in self.chat_history[-5:]]
        
        # Apply mood rules
        self.persona_state = self.rules.apply_mood_rules(self.persona_state, recent_messages)
        
        # Generate response using RAG pipeline
        patient_response = rag_pipeline(
            query=user_input,
            context=recent_messages,
            persona_state=self.persona_state
        )
        
        # Store patient response in history with current persona state
        patient_message = ChatMessage(
            timestamp=datetime.now(),
            speaker="patient",
            content=patient_response,
            persona_state_snapshot=self.persona_state.to_dict()
        )
        self.chat_history.append(patient_message)
        
        # Update last topics for future reference
        self.persona_state.last_topics = recent_messages[-3:] if len(recent_messages) >= 3 else recent_messages
        
        return patient_response, self.persona_state.to_dict()
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Return the full chat history as a list of dictionaries."""
        return [msg.to_dict() for msg in self.chat_history]
    
    def reset_conversation(self):
        """Reset the conversation and persona state."""
        self.persona_state = PersonaState()
        self.chat_history = []
    
    def save_conversation(self, filepath: str):
        """Save the conversation to a JSON file."""
        conversation_data = {
            "chat_history": self.get_chat_history(),
            "final_persona_state": self.persona_state.to_dict(),
            "saved_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(conversation_data, f, indent=2)
    
    def load_conversation(self, filepath: str):
        """Load a conversation from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Reconstruct chat history
        self.chat_history = []
        for msg_data in data["chat_history"]:
            message = ChatMessage(
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                speaker=msg_data["speaker"],
                content=msg_data["content"],
                persona_state_snapshot=msg_data.get("persona_state_snapshot")
            )
            self.chat_history.append(message)
        
        # Reconstruct persona state
        persona_data = data["final_persona_state"]
        self.persona_state = PersonaState(**persona_data)


# Example usage and testing function
def run_demo_conversation():
    """Run a demonstration conversation to test the system."""
    chat = DementiaSimulationChat()
    
    print("=== Dementia Simulation Chat Demo ===")
    print("Patient is ready to chat. Type 'quit' to exit.\n")
    
    sample_inputs = [
        "Hello, how are you feeling today?",
        "Do you remember what you had for breakfast?",
        "Tell me about your family.",
        "What year is it?",
        "Would you like to go home?"
    ]
    
    for i, user_input in enumerate(sample_inputs):
        print(f"User: {user_input}")
        response, persona_state = chat.chat_loop(user_input)
        print(f"Patient: {response}")
        print(f"[Persona - Mood: {persona_state['current_mood']}, Confusion: {persona_state['confusion_level']:.2f}]")
        print()
    
    return chat


if __name__ == "__main__":
    # Run demo if script is executed directly
    demo_chat = run_demo_conversation()
    print(f"Demo completed. Total messages: {len(demo_chat.get_chat_history())}")