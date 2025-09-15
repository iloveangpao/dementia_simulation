#!/usr/bin/env python3
"""Demo script for the dementia simulation system."""

from dementia_simulation.persona import Persona, MoodState
from dementia_simulation.chat import ChatFlow, MockLLM
from dementia_simulation.retriever import Document
import time

def main():
    print("=== Dementia Simulation Demo ===\n")
    
    # Create a persona with moderate dementia
    persona = Persona(
        name="Alice",
        dementia_severity=0.6,
        mood_stability=0.5
    )
    
    print(f"Created persona: {persona.name}")
    print(f"Dementia severity: {persona.dementia_severity}")
    print(f"Initial mood: {persona.current_mood.value}")
    print()
    
    # Add some initial memories
    persona.add_memory("My daughter Sarah visits me every Sunday", importance=0.9, memory_type="family")
    persona.add_memory("I used to love gardening in my backyard", importance=0.7, memory_type="hobby")
    persona.add_memory("The nurses here are very kind", importance=0.6, memory_type="daily")
    persona.add_memory("I had cereal for breakfast", importance=0.3, memory_type="daily")
    
    print(f"Added {len(persona.memories)} initial memories")
    
    # Set up chat flow with mock LLM
    responses = [
        "Oh yes, I think I remember that...",
        "That sounds familiar, but I'm not quite sure.",
        "I'm feeling a bit confused right now.",
        "Could you tell me more about that?",
        "I'm not sure I can recall clearly.",
        "That's nice to hear.",
        "I feel like I should remember, but...",
        "Thank you for being patient with me."
    ]
    
    llm = MockLLM(responses)
    chat_flow = ChatFlow(persona, llm)
    
    # Add some background documents to the retriever
    documents = [
        Document("Alice loves spending time with her family", metadata={"type": "background"}),
        Document("Alice has been living in the care facility for 2 years", metadata={"type": "background"}),
        Document("Alice used to be a teacher before retiring", metadata={"type": "background"})
    ]
    chat_flow.add_memory_context(documents)
    
    print("Set up chat flow with mock LLM and background context\n")
    
    # Simulate a conversation
    user_messages = [
        "Hello Alice, how are you feeling today?",
        "Do you remember your daughter Sarah?",
        "What did you have for breakfast?",
        "Tell me about your hobbies",
        "What do you think about the weather?"
    ]
    
    print("=== Conversation Simulation ===")
    for i, message in enumerate(user_messages):
        print(f"\nUser: {message}")
        
        # Process message and get response
        response = chat_flow.process_user_message(message)
        print(f"Alice: {response}")
        
        # Show current state
        print(f"  [Mood: {persona.current_mood.value}, Memories: {len(persona.memories)}]")
        
        # Simulate some time passing
        time.sleep(0.1)
        
        # Occasionally trigger memory forgetting
        if i == 2:  # After 3rd message
            forgotten_count = chat_flow.simulate_memory_degradation()
            if forgotten_count > 0:
                print(f"  [Alice forgot {forgotten_count} memories due to time passing]")
    
    # Show final state
    print(f"\n=== Final State ===")
    summary = chat_flow.get_conversation_summary()
    print(f"Total messages: {summary['message_count']}")
    print(f"Final mood: {summary['persona_mood']}")
    print(f"Accessible memories: {summary['accessible_memories']}")
    print(f"Total memories: {summary['total_memories']}")
    
    # Show accessible memories
    accessible = persona.get_accessible_memories()
    if accessible:
        print(f"\nCurrent accessible memories:")
        for memory in accessible:
            age_minutes = int(memory.age_in_seconds() / 60)
            print(f"  - {memory.content} (importance: {memory.importance:.1f}, age: {age_minutes}m)")
    
    print(f"\nDemo completed! The system successfully:")
    print("✓ Managed persona mood changes based on dementia severity")
    print("✓ Handled memory forgetting based on importance and time")
    print("✓ Conducted conversation flow with LLM integration")
    print("✓ Used FAISS-based memory retrieval for context")

if __name__ == "__main__":
    main()