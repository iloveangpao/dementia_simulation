#!/usr/bin/env python3
"""
Example usage of the dementia simulation chat system.

This script demonstrates how to use the chat loop and shows the key features:
- Chat history storage
- Persona state evolution 
- Forgetting and mood rules
- RAG pipeline integration
"""

import sys
import os
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.chat import DementiaSimulationChat


def interactive_chat_demo():
    """Run an interactive chat session with the dementia simulation."""
    chat = DementiaSimulationChat()
    
    print("=== Dementia Simulation Interactive Chat ===")
    print("You are chatting with a simulated patient experiencing dementia.")
    print("Type 'quit' to exit, 'history' to see chat history, 'state' to see persona state.")
    print("Type 'reset' to start a new conversation.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'history':
                print("\n--- Chat History ---")
                history = chat.get_chat_history()
                for msg in history:
                    speaker = msg['speaker'].title()
                    content = msg['content']
                    timestamp = msg['timestamp']
                    print(f"[{timestamp}] {speaker}: {content}")
                print("--- End History ---\n")
                continue
            elif user_input.lower() == 'state':
                print("\n--- Current Persona State ---")
                state = chat.persona_state.to_dict()
                for key, value in state.items():
                    print(f"{key}: {value}")
                print("--- End State ---\n")
                continue
            elif user_input.lower() == 'reset':
                chat.reset_conversation()
                print("Conversation reset. Starting fresh.\n")
                continue
            elif not user_input:
                continue
            
            # Process the user input through the chat loop
            patient_response, persona_state = chat.chat_loop(user_input)
            
            # Display the response with persona information
            mood = persona_state['current_mood']
            confusion = persona_state['confusion_level']
            print(f"Patient: {patient_response}")
            print(f"[Mood: {mood}, Confusion: {confusion:.2f}]\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


def automated_demo():
    """Run an automated demonstration showing various features."""
    print("=== Automated Demonstration ===\n")
    
    chat = DementiaSimulationChat()
    
    # Test scenarios that demonstrate different aspects
    test_scenarios = [
        {
            "name": "Initial Contact",
            "inputs": [
                "Hello, how are you today?",
                "What's your name?",
            ]
        },
        {
            "name": "Memory Testing",
            "inputs": [
                "Do you remember what you had for breakfast?",
                "What did you do yesterday?",
                "Can you tell me about your childhood?",
            ]
        },
        {
            "name": "Family Discussion",
            "inputs": [
                "Tell me about your family.",
                "Do you have children?",
                "Where do your children live now?",
            ]
        },
        {
            "name": "Time Orientation",
            "inputs": [
                "What year is it?",
                "What season is it now?",
                "Do you know what time it is?",
            ]
        },
        {
            "name": "Home and Comfort",
            "inputs": [
                "Where is your home?",
                "Would you like to go home?",
                "Are you comfortable here?",
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"=== {scenario['name']} ===")
        
        for user_input in scenario['inputs']:
            print(f"Caregiver: {user_input}")
            
            patient_response, persona_state = chat.chat_loop(user_input)
            
            print(f"Patient: {patient_response}")
            print(f"[State - Mood: {persona_state['current_mood']}, "
                  f"Confusion: {persona_state['confusion_level']:.2f}, "
                  f"Short-term memory items: {len(persona_state['short_term_memory'])}]")
            print()
        
        print()
    
    # Show final conversation summary
    print("=== Conversation Summary ===")
    history = chat.get_chat_history()
    print(f"Total messages exchanged: {len(history)}")
    print(f"Final confusion level: {chat.persona_state.confusion_level:.2f}")
    print(f"Final mood: {chat.persona_state.current_mood}")
    print(f"Topics in short-term memory: {chat.persona_state.short_term_memory}")
    print(f"Forgotten topics: {chat.persona_state.forgotten_topics}")
    
    return chat


def save_conversation_example(chat):
    """Demonstrate saving and loading conversations."""
    print("\n=== Save/Load Demonstration ===")
    
    # Save the conversation
    save_path = "/tmp/demo_conversation.json"
    chat.save_conversation(save_path)
    print(f"Conversation saved to {save_path}")
    
    # Create a new chat instance and load the conversation
    new_chat = DementiaSimulationChat()
    new_chat.load_conversation(save_path)
    print("Conversation loaded into new chat instance")
    
    # Verify the loaded data
    print(f"Loaded chat has {len(new_chat.get_chat_history())} messages")
    print(f"Loaded persona state: mood={new_chat.persona_state.current_mood}, "
          f"confusion={new_chat.persona_state.confusion_level:.2f}")


def main():
    """Main function to run the examples."""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_chat_demo()
    else:
        # Run automated demo by default
        demo_chat = automated_demo()
        save_conversation_example(demo_chat)
        
        print("\n" + "="*50)
        print("Demo complete! Run with 'interactive' argument for interactive mode:")
        print("python example.py interactive")


if __name__ == "__main__":
    main()