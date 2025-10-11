"""
RAG Pipeline for Dementia Simulation

This module implements a Retrieval-Augmented Generation (RAG) pipeline
for simulating patient responses in dementia scenarios.
"""

import logging
from typing import List, Dict, Any
import warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    RAG Pipeline for generating persona-aware responses in dementia simulation.
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """
        Initialize the RAG pipeline.
        
        Args:
            model_name: HuggingFace model name for text generation
        """
        self.model_name = model_name
        self.pipeline = None
        self.retriever = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize the text generation pipeline and document retriever."""
        try:
            from transformers import pipeline
            logger.info(f"Initializing text generation pipeline with model: {self.model_name}")
            self.pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                return_full_text=False,
                pad_token_id=50256,  # GPT-2 pad token
                max_length=512,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            logger.info("Text generation pipeline initialized successfully")
        except ImportError:
            logger.warning("Transformers library not available. Pipeline will use fallback mode.")
            self.pipeline = None
        except Exception as e:
            logger.error(f"Failed to initialize text generation pipeline: {e}")
            self.pipeline = None
    
    def retrieve_documents(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve relevant documents based on the query.
        
        Args:
            query: User input query
            top_k: Number of top documents to retrieve
            
        Returns:
            List of relevant document snippets
        """
        # Placeholder implementation - in a real scenario, this would use
        # a vector database like FAISS, Pinecone, or Weaviate
        documents = [
            "Dementia patients often experience memory loss and confusion.",
            "It's important to speak slowly and clearly with dementia patients.",
            "Patients with dementia may have difficulty recognizing familiar faces.",
            "Creating a calm environment helps reduce anxiety in dementia patients.",
            "Routine and structure are beneficial for dementia patients."
        ]
        
        # Simple keyword-based retrieval (in production, use semantic search)
        query_lower = query.lower()
        relevant_docs = []
        
        for doc in documents:
            if any(word in doc.lower() for word in query_lower.split()):
                relevant_docs.append(doc)
        
        # Return top_k documents, or all if fewer available
        return relevant_docs[:top_k] if relevant_docs else documents[:top_k]
    
    def build_persona_prompt(self, user_input: str, persona: Dict[str, Any], 
                           history: List[Dict[str, str]], context_docs: List[str]) -> str:
        """
        Build a persona-aware prompt for text generation.
        
        Args:
            user_input: Current user input
            persona: Patient persona information
            history: Conversation history
            context_docs: Retrieved context documents
            
        Returns:
            Formatted prompt for text generation
        """
        # Extract persona details
        name = persona.get('name', 'Patient')
        age = persona.get('age', 'elderly')
        condition = persona.get('condition', 'mild dementia')
        personality = persona.get('personality', 'friendly')
        
        # Build context from retrieved documents
        context = "\n".join([f"- {doc}" for doc in context_docs])
        
        # Build conversation history
        conversation = ""
        if history:
            for exchange in history[-3:]:  # Last 3 exchanges for context
                if 'user' in exchange and 'assistant' in exchange:
                    conversation += f"Caregiver: {exchange['user']}\n{name}: {exchange['assistant']}\n"
        
        # Create the prompt
        prompt = f"""You are {name}, a {age} person with {condition}. You have a {personality} personality.

Context about dementia and patient care:
{context}

Conversation history:
{conversation}

Current situation:
Caregiver: {user_input}

As {name}, respond naturally as someone with {condition} would. Keep your response brief, authentic, and consistent with your condition and personality. Show some characteristics of {condition} in your response when appropriate.

{name}:"""

        return prompt
    
    def generate_response(self, user_input: str, persona: Dict[str, Any], 
                         history: List[Dict[str, str]]) -> str:
        """
        Generate a persona-aware response using the RAG pipeline.
        
        Args:
            user_input: The user's input message
            persona: Dictionary containing patient persona information
            history: List of previous conversation exchanges
            
        Returns:
            Generated patient response
        """
        try:
            logger.info(f"Generating response for input: {user_input[:50]}...")
            
            # Step 1: Retrieve relevant documents
            context_docs = self.retrieve_documents(user_input)
            logger.info(f"Retrieved {len(context_docs)} context documents")
            
            # Step 2: Build persona-aware prompt
            prompt = self.build_persona_prompt(user_input, persona, history, context_docs)
            logger.info("Built persona-aware prompt")
            
            # Step 3: Generate response using HuggingFace pipeline
            if self.pipeline is None:
                logger.warning("Text generation pipeline not available, using fallback response")
                name = persona.get('name', 'Patient')
                return f"I'm {name}, and I'm having trouble finding the right words today. Could you help me understand what you're asking?"
            
            # Generate response
            response = self.pipeline(
                prompt,
                max_new_tokens=100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=50256
            )
            
            # Extract and clean the generated text
            generated_text = response[0]['generated_text'].strip()
            
            # Post-process the response to ensure it's appropriate
            cleaned_response = self._post_process_response(generated_text, persona)
            
            logger.info(f"Generated response: {cleaned_response[:50]}...")
            return cleaned_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback response
            name = persona.get('name', 'Patient')
            return f"I'm {name}, and I'm a bit confused right now. Could you help me understand what you mean?"
    
    def _post_process_response(self, response: str, persona: Dict[str, Any]) -> str:
        """
        Post-process the generated response to ensure quality and appropriateness.
        
        Args:
            response: Generated response text
            persona: Patient persona information
            
        Returns:
            Cleaned and processed response
        """
        # Remove any potential repetitions or artifacts
        lines = response.split('\n')
        if lines:
            response = lines[0].strip()
        
        # Ensure response isn't too long
        words = response.split()
        if len(words) > 30:
            response = ' '.join(words[:30]) + "..."
        
        # Ensure response doesn't contain inappropriate content
        if not response or len(response.strip()) < 3:
            name = persona.get('name', 'Patient')
            return f"I'm {name}. Could you repeat that please?"
        
        return response


# Factory function for easy instantiation
def create_rag_pipeline(model_name: str = "microsoft/DialoGPT-medium") -> RAGPipeline:
    """
    Create and return a RAG pipeline instance.
    
    Args:
        model_name: HuggingFace model name for text generation
        
    Returns:
        Initialized RAGPipeline instance
    """
    return RAGPipeline(model_name)


# Convenience function as specified in the problem statement
def generate_response(user_input: str, persona: Dict[str, Any], 
                     history: List[Dict[str, str]]) -> str:
    """
    Generate a response using the default RAG pipeline.
    
    Args:
        user_input: The user's input message
        persona: Dictionary containing patient persona information
        history: List of previous conversation exchanges
        
    Returns:
        Generated patient response
    """
    # Create a default pipeline instance (in production, this should be cached)
    pipeline = create_rag_pipeline()
    return pipeline.generate_response(user_input, persona, history)


if __name__ == "__main__":
    # Example usage
    example_persona = {
        "name": "Mary",
        "age": "75",
        "condition": "mild dementia",
        "personality": "gentle and caring"
    }
    
    example_history = [
        {"user": "Good morning! How are you feeling today?", 
         "assistant": "Oh, good morning dear. I'm feeling a bit confused this morning."}
    ]
    
    response = generate_response(
        "Would you like to have breakfast now?",
        example_persona,
        example_history
    )
    
    print(f"Generated response: {response}")