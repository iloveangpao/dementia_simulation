# RAG Module

Retrieval-Augmented Generation pipeline for context-aware response generation.

## Overview

The `rag` module provides:

- Document retrieval integration
- Prompt construction
- LLM response generation
- Safety filtering
- Citation support

## Quick Example

```python
from dementia_simulation.rag import DementiaRAGPipeline

# Initialize pipeline
pipeline = DementiaRAGPipeline(
    knowledge_base_path="data/knowledge_base",
    model_name="microsoft/DialoGPT-medium",
    disable_faiss=False
)

# Generate response
response = pipeline.generate_response(
    patient_message="I keep forgetting things",
    caregiver_message="Tell me more about that",
    persona_stage="mild"
)

print(f"Response: {response['response']}")
print(f"Retrieved docs: {response['retrieved_docs_count']}")
print(f"Confidence: {response['confidence_score']:.2f}")
```

## Module Reference

The RAG module is located in `src/dementia_simulation/rag/`.

**Key Classes**:

- `DementiaRAGPipeline` - Main RAG pipeline orchestrator
- `PromptBuilder` - Constructs prompts with context
- `ResponseGenerator` - LLM response generation
- `SafetyFilter` - Output safety validation

**Key Methods**:

- `generate_response()` - Generate contextual response
- `retrieve_documents()` - Get relevant context
- `build_prompt()` - Construct prompt with context
- `apply_stage_filters()` - Apply persona stage constraints

For full module documentation, see the source code with inline docstrings.

## Related

- **[Architecture](../../explanation/architecture.md)** - RAG pipeline design
- **[Add Model](../../how-to/add-model.md)** - Configure LLM
- **[Add Citations](../../how-to/add-citations.md)** - Enable source tracking
