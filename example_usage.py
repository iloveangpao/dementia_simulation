import sys
import os

# Add src to path to import the retriever
sys.path.append('src')

from retriever import Retriever


def demo_retriever():
    """Demonstrate the retriever functionality."""
    
    print("Dementia Information Retrieval System")
    print("=" * 40)
    
    # Initialize the retriever
    retriever = Retriever(embeddings_dir="embeddings")
    
    # Try to load the index
    if not retriever.load_index():
        print("Error: Could not load the FAISS index.")
        print("Please run 'python build_index.py' first to create the index.")
        print("Or run 'python test_retriever.py' to test with mock data.")
        return
    
    # Display index information
    print("\nIndex Information:")
    print("-" * 20)
    info = retriever.get_index_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # Interactive query loop
    print("\nYou can now ask questions about dementia.")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            query = input("Enter your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            print(f"\nSearching for: '{query}'")
            print("-" * 40)
            
            # Retrieve relevant documents
            results = retriever.retrieve(query, top_k=3)
            
            if results:
                for i, (document, score) in enumerate(results, 1):
                    print(f"\nResult {i} (Score: {score:.4f}):")
                    print(f"{document}")
                    print("-" * 40)
            else:
                print("No relevant documents found.")
            
            print()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error during search: {e}")
    
    print("\nThank you for using the Dementia Information Retrieval System!")

from persona import PatientPersona, DementiaStage, MoodState


def demo_patient_persona():
    """Demonstrate PatientPersona usage."""
    print("PatientPersona Usage Example")
    print("=" * 30)
    
    # Create a patient with mild dementia
    patient = PatientPersona(
        name="Mary Johnson",
        dementia_stage=DementiaStage.MILD,
        initial_mood=MoodState.CALM
    )
    
    print(f"Created patient: {patient}")
    print(f"Initial status: {patient.get_status()}")
    
    # Add some personal information to memory
    print("\nAdding personal memories...")
    patient.add_memory_key("daughter_name", "Sarah")
    patient.add_memory_key("favorite_song", "Moon River")
    patient.add_memory_key("home_address", "123 Oak Street")
    patient.add_memory_key("wedding_anniversary", "June 15th")
    
    # Add some recent activities
    print("Adding recent activities...")
    patient.add_recent_memory("Had breakfast with oatmeal")
    patient.add_recent_memory("Nurse checked blood pressure")
    patient.add_recent_memory("Watched morning news")
    patient.add_recent_memory("Called daughter on phone")
    
    # Simulate daily interactions
    print("\nSimulating daily interactions:")
    print("-" * 35)
    
    for day in range(1, 4):
        print(f"\nDay {day}:")
        
        # Check if patient remembers key information
        daughter = patient.get_memory_key("daughter_name")
        song = patient.get_memory_key("favorite_song")
        address = patient.get_memory_key("home_address")
        
        print(f"  Remembers daughter's name: {daughter or 'Forgotten'}")
        print(f"  Remembers favorite song: {song or 'Forgotten'}")
        print(f"  Remembers home address: {address or 'Forgotten'}")
        
        # Update mood
        new_mood = patient.update_mood()
        print(f"  Current mood: {new_mood.value}")
        
        # Check recent memories and forget some
        print(f"  Recent memories before forgetting: {len(patient.recent_memories)}")
        forgotten = patient.forget_recent()
        if forgotten:
            print(f"  Forgot: {forgotten}")
        print(f"  Recent memories after forgetting: {len(patient.recent_memories)}")
        
        # Add new daily activity
        patient.add_recent_memory(f"Day {day} activity: Had lunch")
    
    print(f"\nFinal patient status:")
    final_status = patient.get_status()
    for key, value in final_status.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()