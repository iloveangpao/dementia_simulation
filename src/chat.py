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
        # Check for mood triggers in recent conversation
        recent_text = " ".join(conversation_context).lower()
        
        # Detect stressful keywords
        stress_keywords = ["hospital", "doctor", "medicine", "wrong", "no", "stop"]
        stress_count = sum(1 for keyword in stress_keywords if keyword in recent_text)
        
        # Detect calming keywords
        calming_keywords = ["love", "family", "home", "remember", "care", "yes"]
        calming_count = sum(1 for keyword in calming_keywords if keyword in recent_text)
        
        # Update mood based on conversation tone
        if stress_count > calming_count and stress_count > 0:
            # Increase likelihood of negative moods
            if random.random() < 0.6:
                moods = ["agitated", "confused", "anxious"]
                persona.current_mood = random.choice(moods)
                persona.mood_intensity = min(1.0, persona.mood_intensity + 0.2)
        elif calming_count > stress_count and calming_count > 0:
            # Increase likelihood of positive moods
            if random.random() < 0.5:
                moods = ["content", "happy", "calm"]
                persona.current_mood = random.choice(moods)
                persona.mood_intensity = max(0.3, persona.mood_intensity - 0.1)
        else:
            # Neutral mood fluctuation
            if random.random() < 0.3:
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
            "Do you know my family? Are they coming to visit?",
            "I used to do this with my mother...",
            "Where is everyone? They said they'd be here."
        ],
        "anxious": [
            "Something doesn't feel right...",
            "I'm worried about something, but I can't remember what.",
            "Are you sure this is the right place?",
            "I feel like I should be somewhere else."
        ],
        "content": [
            "This is nice. Thank you for being here.",
            "I appreciate your patience with me.",
            "It's a lovely day, isn't it?",
            "You're very kind to help me."
        ]
    }
    
    # Select response category based on persona state
    if persona_state.confusion_level > 0.7:
        category = "high_confusion"
    elif persona_state.repetition_tendency > 0.5:
        category = "repetitive"
    elif "family" in persona_state.preferred_topics and random.random() < 0.4:
        category = "family_focused"
    elif persona_state.current_mood in ["anxious", "agitated"]:
        category = "anxious"
    elif persona_state.current_mood in ["content", "happy", "calm"]:
        category = "content"
    else:
        category = random.choice(["high_confusion", "repetitive", "family_focused"])
    
    # Generate context-aware response
    response = random.choice(response_templates[category])
    
    # Add repetition if tendency is high
    if persona_state.repetition_tendency > 0.6 and random.random() < 0.5:
        response += " " + response.split('.')[0] + "."
    
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
        
        # Store patient response in history with persona state snapshot
        patient_message = ChatMessage(
            timestamp=datetime.now(),
            speaker="patient",
            content=patient_response,
            persona_state_snapshot=self.persona_state.to_dict()
        )
        self.chat_history.append(patient_message)
        
        # Return response and current persona state
        return patient_response, self.persona_state.to_dict()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the complete conversation history."""
        return [msg.to_dict() for msg in self.chat_history]
    
    def reset_conversation(self):
        """Reset the conversation and persona state."""
        self.chat_history = []
        self.persona_state = PersonaState()


# Example usage and testing function
def run_demo_conversation():
    """Run a demonstration conversation to test the system."""
    chat = DementiaSimulationChat()
    
    print("=" * 60)
    print("Dementia Simulation Chat Demo")
    print("=" * 60)
    print()
    
    # Sample conversation
    user_inputs = [
        "Hello, how are you feeling today?",
        "Would you like to have some lunch?",
        "Your family called and said they'll visit soon.",
        "Do you remember what we had for breakfast?",
        "Let's take a walk in the garden."
    ]
    
    for user_input in user_inputs:
        print(f"User: {user_input}")
        response, persona_state = chat.chat_loop(user_input)
        print(f"Patient: {response}")
        print(f"[Mood: {persona_state['current_mood']}, Confusion: {persona_state['confusion_level']:.2f}]")
        print()
    
    print("=" * 60)
    print("Conversation Summary")
    print("=" * 60)
    print(f"Total messages: {len(chat.get_conversation_history())}")
    print(f"Final mood: {chat.persona_state.current_mood}")
    print(f"Final confusion level: {chat.persona_state.confusion_level:.2f}")
    print(f"Short-term memory items: {len(chat.persona_state.short_term_memory)}")
    print(f"Forgotten topics: {len(chat.persona_state.forgotten_topics)}")


if __name__ == "__main__":
    run_demo_conversation()
