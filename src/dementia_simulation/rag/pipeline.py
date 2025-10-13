"""
RAG (Retrieval-Augmented Generation) pipeline for dementia simulation.

This module combines document retrieval with language model generation
to create contextually informed responses for dementia patient simulation.
"""

import asyncio
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger

from ..persona.models import DementiaPersona, DementiaStage, MoodState

# Import local modules
from ..retriever.faiss_retriever import FAISSRetriever

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

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
        temperature: float = 0.7,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
        max_context_tokens: int = 1024,
    ):
        """
        Initialize the RAG pipeline.

        Args:
            retriever: FAISS retriever for knowledge base
            model_name: HuggingFace model name or path
            use_openai: Whether to use OpenAI API instead of local models
            openai_model: OpenAI model to use
            max_context_length: Maximum context length for generation
                (deprecated, use max_context_tokens)
            temperature: Generation temperature (0.0 to 1.0)
            top_p: Nucleus sampling parameter
            repetition_penalty: Penalty for repeated tokens
            max_context_tokens: Maximum number of tokens for context
        """
        self.retriever = retriever or FAISSRetriever()
        self.model_name = model_name
        self.use_openai = use_openai
        self.openai_model = openai_model
        self.max_context_length = max_context_length
        self.temperature = temperature
        self.top_p = top_p
        self.repetition_penalty = repetition_penalty
        self.max_context_tokens = max_context_tokens

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

            # Set pad token if not present (prefer explicit pad, fall back to eos)
            if self.tokenizer.pad_token is None:
                # Some models define pad_token_id but not pad_token string
                if self.tokenizer.pad_token_id is not None:
                    logger.info("Using existing pad_token_id from tokenizer config")
                else:
                    # Fall back to EOS token for padding
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                    logger.info("Set pad_token to eos_token (no explicit pad token)")

            # Handle multiple EOS token IDs (e.g., Llama 3.x)
            # Some models have eos_token_id as a list; we pass it as-is to the pipeline
            if isinstance(self.tokenizer.eos_token_id, list):
                logger.info(
                    f"Model has multiple EOS token IDs: {self.tokenizer.eos_token_id}"
                )

            # Load model with appropriate settings
            model_kwargs = {
                "torch_dtype": torch.float16 if device == "cuda" else torch.float32,
                "low_cpu_mem_usage": True,
            }

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name, **model_kwargs
            )

            # Create text generation pipeline
            # Pass both pad_token_id and eos_token_id explicitly
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1,
                do_sample=True,
                temperature=self.temperature,
                max_new_tokens=150,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,  # Pass full list or single ID
            )

            logger.info(f"Initialized HuggingFace model: {self.model_name}")
            logger.info(
                f"Using pad_token_id={self.tokenizer.pad_token_id}, "
                f"eos_token_id={self.tokenizer.eos_token_id}"
            )

        except Exception as e:
            logger.error(f"Error setting up HuggingFace model: {e}")
            self.model = None
            self.tokenizer = None
            self.generator = None

    def retrieve_context(
        self, query: str, persona: DementiaPersona, k: int = 3
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
        enhanced_query = (
            f"{query} {persona.stage.value} dementia {persona.current_mood.value}"
        )

        # Retrieve documents
        results = self.retriever.search(enhanced_query, k=k, score_threshold=0.1)

        # Filter by relevance to persona's stage
        filtered_results = []
        for doc, _score in results:
            if persona.stage.value in doc.get("severity", [persona.stage.value]):
                filtered_results.append(doc)

        # If no stage-specific results, use general results
        if not filtered_results:
            filtered_results = [doc for doc, _ in results]

        logger.debug(f"Retrieved {len(filtered_results)} relevant documents")
        return filtered_results[:k]

    def _truncate_messages_by_tokens(
        self, messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Truncate messages to fit within max_context_tokens by keeping the last tokens.

        Args:
            messages: List of chat messages

        Returns:
            Truncated list of messages
        """
        if self.tokenizer is None:
            return messages

        # Encode all messages to get total token count
        full_text = ""
        for msg in messages:
            full_text += f"{msg['role']}: {msg['content']}\n"

        tokens = self.tokenizer.encode(full_text, add_special_tokens=True)

        # If within limit, return as is
        if len(tokens) <= self.max_context_tokens:
            return messages

        # Keep system message and truncate conversation history
        system_msgs = [msg for msg in messages if msg["role"] == "system"]
        other_msgs = [msg for msg in messages if msg["role"] != "system"]

        # Try to keep at least the last user message
        if not other_msgs:
            return system_msgs

        # Encode system message
        system_text = ""
        for msg in system_msgs:
            system_text += f"{msg['role']}: {msg['content']}\n"
        system_tokens = self.tokenizer.encode(system_text, add_special_tokens=False)

        # Calculate available tokens for other messages
        available_tokens = self.max_context_tokens - len(system_tokens) - 50  # buffer

        # Start from the end and add messages until we hit the limit
        truncated_other = []
        current_tokens = 0

        for msg in reversed(other_msgs):
            msg_text = f"{msg['role']}: {msg['content']}\n"
            msg_tokens = self.tokenizer.encode(msg_text, add_special_tokens=False)

            if current_tokens + len(msg_tokens) <= available_tokens:
                truncated_other.insert(0, msg)
                current_tokens += len(msg_tokens)
            else:
                break

        return system_msgs + truncated_other

    def build_prompt(
        self,
        user_input: str,
        persona: DementiaPersona,
        context_documents: List[Dict],
        conversation_history: List[Dict] = None,
    ) -> List[Dict[str, str]]:
        """
        Build the complete prompt for generation using chat format.

        Args:
            user_input: User's current input
            persona: Dementia persona
            context_documents: Retrieved context documents
            conversation_history: Recent conversation history

        Returns:
            List of chat messages in format
            [{"role": "system"|"user"|"assistant", "content": str}]
        """
        messages = []

        # System message with persona context and guidance
        system_content = persona.get_context_prompt()
        system_content += (
            "\n\nGuidance: Validate feelings and emotions. "
            "Avoid arguing or correcting. Speak simply and clearly. "
            "Redirect gently when confused."
        )

        # Add relevant knowledge if available
        if context_documents:
            system_content += "\n\nRelevant care information:\n"
            for i, doc in enumerate(
                context_documents[:2], 1
            ):  # Limit to 2 docs to save space
                system_content += f"{i}. {doc['text']}\n"

        messages.append({"role": "system", "content": system_content})

        # Add conversation history (last 3 exchanges)
        if conversation_history and len(conversation_history) > 0:
            for entry in conversation_history[-3:]:
                role = "user" if entry["speaker"] == "caregiver" else "assistant"
                messages.append({"role": role, "content": entry["message"]})

        # Add current user input
        messages.append({"role": "user", "content": user_input})

        return messages

    async def generate_response_openai(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response using OpenAI API.

        Args:
            messages: List of chat messages in format [{"role": str, "content": str}]

        Returns:
            Generated response text
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.openai_model,
                messages=messages,
                max_tokens=150,
                temperature=self.temperature,
                top_p=self.top_p,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return "I'm sorry, I'm feeling a bit confused right now."

    def generate_response_huggingface(
        self, messages: List[Dict[str, str]], retry_count: int = 0
    ) -> str:
        """
        Generate response using HuggingFace model with chat template.

        Args:
            messages: List of chat messages in format [{"role": str, "content": str}]
            retry_count: Current retry attempt (for internal use)

        Returns:
            Generated response text
        """
        try:
            if self.generator is None or self.tokenizer is None:
                return "I'm having trouble thinking right now."

            # Truncate messages by tokens
            truncated_messages = self._truncate_messages_by_tokens(messages)

            # Try to use chat template if available
            try:
                prompt = self.tokenizer.apply_chat_template(
                    truncated_messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
            except Exception as template_error:
                logger.warning(
                    f"Chat template not available, using fallback: {template_error}"
                )
                # Fallback: concatenate messages manually
                prompt = ""
                for msg in truncated_messages:
                    role_label = {
                        "system": "System",
                        "user": "Caregiver",
                        "assistant": "You",
                    }.get(msg["role"], msg["role"].capitalize())
                    prompt += f"{role_label}: {msg['content']}\n"
                prompt += "You: "

            # Generate response with decoding parameters
            # Pass pad_token_id and eos_token_id explicitly to avoid warnings
            outputs = self.generator(
                prompt,
                max_new_tokens=100,
                num_return_sequences=1,
                temperature=self.temperature,
                top_p=self.top_p,
                repetition_penalty=self.repetition_penalty,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                return_full_text=False,
            )

            # Extract generated text
            response = outputs[0]["generated_text"].strip()

            # Clean up response
            if "\n" in response:
                response = response.split("\n")[0]  # Take first line only

            # Min-length guard and retry logic
            is_too_short = len(response) < 40
            is_non_wordy = response.lower() in ["pl", "ok", "yes", "no", "hmm"]

            if (is_too_short or is_non_wordy) and retry_count == 0:
                logger.info(
                    f"Response too short or non-wordy (len={len(response)}), "
                    "retrying with coach tail"
                )
                # Add a coach tail to encourage better response
                coach_message = {
                    "role": "system",
                    "content": (
                        "Remember: Validate feelings and gently redirect. "
                        "Respond with more detail and empathy. "
                        "Speak as the person with dementia would naturally respond."
                    ),
                }
                # Insert coach message before the last user message
                enhanced_messages = truncated_messages[:-1] + [
                    coach_message,
                    truncated_messages[-1],
                ]
                return self.generate_response_huggingface(
                    enhanced_messages, retry_count=1
                )

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
                "I'm having trouble concentrating today.",
            ],
            DementiaStage.MODERATE: [
                "I'm sorry, what did you say?",
                "I don't understand. Who are you?",
                "Where am I? This doesn't look familiar.",
                "I want to go home now.",
            ],
            DementiaStage.SEVERE: [
                "What? I don't... what?",
                "No, no, no...",
                "Help me... I'm scared.",
                "Mama? Is that you?",
            ],
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
        conversation_history: Optional[List[Dict]] = None,
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

        # Build prompt messages
        messages = self.build_prompt(
            user_input, persona, context_docs, conversation_history
        )

        # Generate response
        if self.use_openai and OPENAI_AVAILABLE:
            response_text = await self.generate_response_openai(messages)
            model_used = f"openai-{self.openai_model}"
        elif self.generator is not None:
            response_text = self.generate_response_huggingface(messages)
            model_used = self.model_name
        else:
            response_text = self.generate_mock_response(persona, user_input)
            model_used = "mock"

        # Apply persona-specific modifications
        if persona.should_be_confused() and len(response_text) > 20:
            response_text = "I'm sorry, what were we talking about?"

        if persona.should_repeat():
            response_text += " " + response_text.split(".")[0] + "."

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
            model_used=model_used,
        )

    def get_pipeline_stats(self) -> Dict:
        """Get statistics about the pipeline."""
        stats = {
            "model_name": self.model_name,
            "use_openai": self.use_openai,
            "retriever_stats": self.retriever.get_stats() if self.retriever else {},
            "model_loaded": self.generator is not None or self.use_openai,
        }
        return stats


# Convenience function for backward compatibility and easier access
async def generate_response(
    user_input: str,
    persona: DementiaPersona,
    history: Optional[List[Dict]] = None,
    retriever: Optional[FAISSRetriever] = None,
    model_name: str = "microsoft/DialoGPT-medium",
    use_openai: bool = False,
) -> RAGResponse:
    """
    Generate a persona-aware response using the RAG pipeline.

    This is a convenience function that creates a pipeline instance and generates
    a response. For multiple calls, it's more efficient to create a pipeline
    instance once and reuse it.

    Args:
        user_input: The user's input message
        persona: DementiaPersona object with patient information
        history: List of previous conversation exchanges (optional)
        retriever: Optional FAISSRetriever instance
        model_name: HuggingFace model name for text generation
        use_openai: Whether to use OpenAI API

    Returns:
        RAGResponse object containing the generated response and metadata

    Example:
        >>> from dementia_simulation.persona.models import create_sample_personas
        >>> personas = create_sample_personas()
        >>> persona = personas[0]
        >>> response = await generate_response(
        ...     "How are you feeling today?",
        ...     persona
        ... )
        >>> print(response.response_text)
    """
    pipeline = DementiaRAGPipeline(
        retriever=retriever,
        model_name=model_name,
        use_openai=use_openai,
    )

    return await pipeline.generate_response(
        user_input=user_input,
        persona=persona,
        conversation_history=history,
    )


if __name__ == "__main__":
    # Example usage
    import asyncio

    from ..persona.models import create_sample_personas
    from ..retriever.faiss_retriever import initialize_retriever_with_knowledge_base

    async def test_rag():
        # Initialize components
        retriever = FAISSRetriever()
        initialize_retriever_with_knowledge_base(retriever)

        rag = DementiaRAGPipeline(retriever=retriever)
        personas = create_sample_personas()

        # Test conversation
        persona = personas[1]  # Moderate dementia

        response = await rag.generate_response("How are you feeling today?", persona)

        print(f"Response: {response.response_text}")
        print(f"Mood: {response.persona_mood}")
        print(f"Model: {response.model_used}")
        print(f"Processing time: {response.processing_time:.2f}s")

    # Run test
    asyncio.run(test_rag())
