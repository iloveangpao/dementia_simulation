"""
RAG (Retrieval-Augmented Generation) pipeline for dementia simulation.

This module combines document retrieval with language model generation
to create contextually informed responses for dementia patient simulation.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import asyncio
from loguru import logger
import os
from datetime import datetime

# Import local modules
from ..retriever.faiss_retriever import FAISSRetriever
from ..persona.models import DementiaPersona, DementiaStage, MoodState

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logger.warning("Transformers not available. Using mock responses.")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class RAGResponse:
    """Response from the RAG pipeline."""
    response_text: str
    retrieved_documents: List[Dict]
    confidence_score: float
    persona_mood: str
    processing_time: float
    model_used: str


class DementiaRAGPipeline:
    """
    RAG pipeline specifically designed for dementia patient simulation.
    """
    
    def __init__(
        self,
        retriever: Optional[FAISSRetriever] = None,
        model_name: str = "microsoft/DialoGPT-medium",
        use_openai: bool = False,
        openai_model: str = "gpt-3.5-turbo",
        max_context_length: int = 2048,
        temperature: float = 0.7
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            retriever: FAISS retriever for knowledge base
            model_name: HuggingFace model name or path
            use_openai: Whether to use OpenAI API instead of local models
            openai_model: OpenAI model to use
            max_context_length: Maximum context length for generation
            temperature: Generation temperature (0.0 to 1.0)
        """
        self.retriever = retriever or FAISSRetriever()
        self.model_name = model_name
        self.use_openai = use_openai
        self.openai_model = openai_model
        self.max_context_length = max_context_length
        self.temperature = temperature
        
        # Initialize language model
        self.tokenizer = None
        self.model = None
        self.generator = None
        
        if self.use_openai and OPENAI_AVAILABLE:
            self._setup_openai()
        elif HF_AVAILABLE:
            self._setup_huggingface()
        else:
            logger.warning("No language models available. Using mock responses.")
    
    def _setup_openai(self):
        """Setup OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            self.use_openai = False
            return
        
        openai.api_key = api_key
        logger.info(f"Initialized OpenAI client with model: {self.openai_model}")
    
    def _setup_huggingface(self):
        """Setup HuggingFace transformers."""
        try:
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Add pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with appropriate settings
            model_kwargs = {
                "torch_dtype": torch.float16 if device == "cuda" else torch.float32,
                "low_cpu_mem_usage": True
            }
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1,
                do_sample=True,
                temperature=self.temperature,
                max_new_tokens=150,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            logger.info(f"Initialized HuggingFace model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error setting up HuggingFace model: {e}")
            self.model = None
            self.tokenizer = None
            self.generator = None
    
    def retrieve_context(
        self,
        query: str,
        persona: DementiaPersona,
        k: int = 3
    ) -> List[Dict]:
        """
        Retrieve relevant context documents for the query.
        
        Args:
            query: User's input/question
            persona: Current dementia persona
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        # Enhance query with persona information
        enhanced_query = f"{query} {persona.stage.value} dementia {persona.current_mood.value}"
        
        # Retrieve documents
        results = self.retriever.search(enhanced_query, k=k, score_threshold=0.1)
        
        # Filter by relevance to persona's stage
        filtered_results = []
        for doc, score in results:
            if persona.stage.value in doc.get('severity', [persona.stage.value]):
                filtered_results.append(doc)
        
        # If no stage-specific results, use general results
        if not filtered_results:
            filtered_results = [doc for doc, _ in results]
        
        logger.debug(f"Retrieved {len(filtered_results)} relevant documents")
        return filtered_results[:k]
    
    def build_prompt(
        self,
        user_input: str,
        persona: DementiaPersona,
        context_documents: List[Dict],
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Build the complete prompt for generation.
        
        Args:
            user_input: User's current input
            persona: Dementia persona
            context_documents: Retrieved context documents
            conversation_history: Recent conversation history
            
        Returns:
            Complete prompt string
        """
        # Start with persona context
        prompt = persona.get_context_prompt()
        
        # Add relevant knowledge if available
        if context_documents:
            prompt += "\n\nRelevant care information:\n"
            for i, doc in enumerate(context_documents[:2], 1):  # Limit to 2 docs to save space
                prompt += f"{i}. {doc['text']}\n"
        
        # Add conversation history
        if conversation_history and len(conversation_history) > 0:
            prompt += "\n\nRecent conversation:\n"
            for entry in conversation_history[-3:]:  # Last 3 exchanges
                speaker = "Caregiver" if entry['speaker'] == 'caregiver' else "You"
                prompt += f"{speaker}: {entry['message']}\n"
        
        # Add current interaction
        prompt += f"\n\nCaregiver: {user_input}\nYou: "
        
        return prompt
    
    async def generate_response_openai(self, prompt: str) -> str:
        """
        Generate response using OpenAI API.
        
        Args:
            prompt: Complete prompt for generation
            
        Returns:
            Generated response text
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are roleplaying as a person with dementia. Follow the persona description carefully."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=self.temperature,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return "I'm sorry, I'm feeling a bit confused right now."
    
    def generate_response_huggingface(self, prompt: str) -> str:
        """
        Generate response using HuggingFace model.
        
        Args:
            prompt: Complete prompt for generation
            
        Returns:
            Generated response text
        """
        try:
            if self.generator is None:
                return "I'm having trouble thinking right now."
            
            # Truncate prompt if too long
            if len(prompt) > self.max_context_length:
                prompt = prompt[-self.max_context_length:]
            
            # Generate response
            outputs = self.generator(
                prompt,
                max_new_tokens=100,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract generated text (remove prompt)
            generated_text = outputs[0]['generated_text']
            response = generated_text[len(prompt):].strip()
            
            # Clean up response
            if '\n' in response:
                response = response.split('\n')[0]  # Take first line only
            
            return response if response else "I'm not sure what to say."
            
        except Exception as e:
            logger.error(f"HuggingFace generation error: {e}")
            return "I'm feeling a bit confused right now."
    
    def generate_mock_response(self, persona: DementiaPersona, user_input: str) -> str:
        """
        Generate a mock response based on persona characteristics.
        
        Args:
            persona: Dementia persona
            user_input: User's input
            
        Returns:
            Mock response based on persona
        """
        responses = {
            DementiaStage.MILD: [
                "I think I remember that, but I'm not entirely sure.",
                "Could you remind me what we were talking about?",
                "That sounds familiar, but my memory isn't what it used to be.",
                "I'm having trouble concentrating today."
            ],
            DementiaStage.MODERATE: [
                "I'm sorry, what did you say?",
                "I don't understand. Who are you?",
                "Where am I? This doesn't look familiar.",
                "I want to go home now."
            ],
            DementiaStage.SEVERE: [
                "What? I don't... what?",
                "No, no, no...",
                "Help me... I'm scared.",
                "Mama? Is that you?"
            ]
        }
        
        # Select response based on mood
        if persona.current_mood == MoodState.AGITATED:
            return "I don't want to talk about this! Leave me alone!"
        elif persona.current_mood == MoodState.ANXIOUS:
            return "I'm worried... something's not right."
        elif persona.current_mood == MoodState.CONFUSED:
            return "I don't understand what's happening."
        
        import random
        return random.choice(responses[persona.stage])
    
    async def generate_response(
        self,
        user_input: str,
        persona: DementiaPersona,
        conversation_history: Optional[List[Dict]] = None
    ) -> RAGResponse:
        """
        Generate a complete response using the RAG pipeline.
        
        Args:
            user_input: User's input message
            persona: Current dementia persona
            conversation_history: Recent conversation history
            
        Returns:
            Complete RAG response with metadata
        """
        start_time = datetime.now()
        
        # Update persona mood based on interaction
        trigger = None
        if "?" in user_input and persona.should_repeat():
            trigger = "question_repeated"
        elif any(word in user_input.lower() for word in ["wrong", "no", "mistake"]):
            trigger = "correction"
        elif any(word in user_input.lower() for word in ["good", "right", "yes"]):
            trigger = "validation"
        
        persona.update_mood(trigger)
        
        # Retrieve relevant context
        context_docs = self.retrieve_context(user_input, persona)
        
        # Build prompt
        prompt = self.build_prompt(user_input, persona, context_docs, conversation_history)
        
        # Generate response
        if self.use_openai and OPENAI_AVAILABLE:
            response_text = await self.generate_response_openai(prompt)
            model_used = f"openai-{self.openai_model}"
        elif self.generator is not None:
            response_text = self.generate_response_huggingface(prompt)
            model_used = self.model_name
        else:
            response_text = self.generate_mock_response(persona, user_input)
            model_used = "mock"
        
        # Apply persona-specific modifications
        if persona.should_be_confused() and len(response_text) > 20:
            response_text = "I'm sorry, what were we talking about?"
        
        if persona.should_repeat():
            response_text += " " + response_text.split('.')[0] + "."
        
        # Calculate processing time and confidence
        processing_time = (datetime.now() - start_time).total_seconds()
        confidence_score = 0.8 if context_docs else 0.5
        
        # Add to persona's conversation history
        persona.add_to_conversation_history(user_input, "caregiver")
        persona.add_to_conversation_history(response_text, "patient")
        
        return RAGResponse(
            response_text=response_text,
            retrieved_documents=context_docs,
            confidence_score=confidence_score,
            persona_mood=persona.current_mood.value,
            processing_time=processing_time,
            model_used=model_used
        )
    
    def get_pipeline_stats(self) -> Dict:
        """Get statistics about the pipeline."""
        stats = {
            "model_name": self.model_name,
            "use_openai": self.use_openai,
            "retriever_stats": self.retriever.get_stats() if self.retriever else {},
            "model_loaded": self.generator is not None or self.use_openai
        }
        return stats


if __name__ == "__main__":
    # Example usage
    import asyncio
    from ..retriever.faiss_retriever import initialize_retriever_with_knowledge_base
    from ..persona.models import create_sample_personas
    
    async def test_rag():
        # Initialize components
        retriever = FAISSRetriever()
        initialize_retriever_with_knowledge_base(retriever)
        
        rag = DementiaRAGPipeline(retriever=retriever)
        personas = create_sample_personas()
        
        # Test conversation
        persona = personas[1]  # Moderate dementia
        
        response = await rag.generate_response(
            "How are you feeling today?",
            persona
        )
        
        print(f"Response: {response.response_text}")
        print(f"Mood: {response.persona_mood}")
        print(f"Model: {response.model_used}")
        print(f"Processing time: {response.processing_time:.2f}s")
    
    # Run test
    asyncio.run(test_rag())