#!/usr/bin/env python3
"""
Example usage of the RAG Pipeline for dementia simulation

This script demonstrates how to use the generate_response function
with different personas and conversation scenarios.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.rag_pipeline import generate_response, create_rag_pipeline


def demo_basic_usage():
    """Demonstrate basic usage of the generate_response function"""
    print("=== Basic Usage Demo ===\n")
    
    # Define a patient persona
    persona = {
        "name": "Margaret",
        "age": "78",
        "condition": "moderate dementia",
        "personality": "formerly outgoing teacher, now sometimes confused but still kind"
    }
    
    # Start with empty history
    history = []
    
    # Simulate a conversation
    conversations = [
        "Good morning Margaret! How are you feeling today?",
        "I brought you some tea. Would you like to drink it?",
        "Do you remember what you had for breakfast?",
        "Your daughter called and said she'll visit later today."
    ]
    
    for user_input in conversations:
        print(f"Caregiver: {user_input}")
        
        # Generate response
        response = generate_response(user_input, persona, history)
        print(f"Margaret: {response}")
        print()
        
        # Add to history
        history.append({
            "user": user_input,
            "assistant": response
        })


def demo_different_personas():
    """Demonstrate usage with different patient personas"""
    print("=== Different Personas Demo ===\n")
    
    personas = [
        {
            "name": "Robert",
            "age": "82",
            "condition": "early-stage dementia",
            "personality": "retired engineer, detail-oriented but becoming forgetful"
        },
        {
            "name": "Emma",
            "age": "74",
            "condition": "severe dementia",
            "personality": "former nurse, caring but often disoriented"
        }
    ]
    
    user_input = "Can you tell me about your family?"
    
    for persona in personas:
        print(f"Persona: {persona['name']} ({persona['condition']})")
        print(f"Caregiver: {user_input}")
        
        response = generate_response(user_input, persona, [])
        print(f"{persona['name']}: {response}")
        print()


def demo_conversation_history():
    """Demonstrate how conversation history affects responses"""
    print("=== Conversation History Demo ===\n")
    
    persona = {
        "name": "William",
        "age": "80",
        "condition": "mild dementia",
        "personality": "former musician, still loves music but forgets recent events"
    }
    
    # Build up conversation history
    history = [
        {
            "user": "Do you remember playing piano?",
            "assistant": "Oh yes, I loved playing piano. I played for many years."
        },
        {
            "user": "What was your favorite piece to play?",
            "assistant": "I think... Chopin was always my favorite. The nocturnes were beautiful."
        }
    ]
    
    print("Previous conversation:")
    for exchange in history:
        print(f"Caregiver: {exchange['user']}")
        print(f"William: {exchange['assistant']}")
        print()
    
    print("Current interaction:")
    user_input = "Would you like to listen to some Chopin now?"
    print(f"Caregiver: {user_input}")
    
    response = generate_response(user_input, persona, history)
    print(f"William: {response}")


def demo_error_handling():
    """Demonstrate error handling with invalid inputs"""
    print("\n=== Error Handling Demo ===\n")
    
    persona = {
        "name": "Dorothy",
        "age": "76",
        "condition": "dementia",
        "personality": "gentle"
    }
    
    # Test with minimal persona
    minimal_persona = {"name": "John"}
    
    response = generate_response("How are you?", minimal_persona, [])
    print(f"Response with minimal persona: {response}")
    
    # Test with empty input
    response = generate_response("", persona, [])
    print(f"Response with empty input: {response}")


if __name__ == "__main__":
    print("Dementia Simulation RAG Pipeline Demo")
    print("=" * 50)
    print()
    
    try:
        demo_basic_usage()
        demo_different_personas()
        demo_conversation_history()
        demo_error_handling()
        
        print("\nDemo completed successfully!")
        print("Note: Actual model responses will vary and require proper model installation.")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        print("This is expected if transformers library is not installed.")
        print("Install with: pip install -r requirements.txt")