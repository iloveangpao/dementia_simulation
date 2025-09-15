"""
Example usage of the Retriever class for dementia simulation.

This script demonstrates how to use the Retriever class to search for 
relevant information from a knowledge base about dementia.
"""

import sys
import os

# Add src to path to import the retriever
sys.path.append('src')

from retriever import Retriever


def main():
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


if __name__ == "__main__":
    main()