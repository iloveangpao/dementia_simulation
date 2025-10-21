# Dementia Simulation Documentation

Welcome to the comprehensive documentation for the **Dementia Simulation** platform - a tool designed to help caregivers practice empathetic communication with dementia patients through realistic AI-powered simulations.

## 🎯 What is Dementia Simulation?

Dementia Simulation is a comprehensive platform that provides:

- **Patient Persona Simulation**: Realistic patient personas at different dementia stages (mild, moderate, severe)
- **Interactive Chat Interfaces**: Web UI (Streamlit), CLI, and REST API for flexible interaction
- **RAG Pipeline**: Retrieval-Augmented Generation using knowledge base documents with FAISS indexing
- **Feedback Evaluation**: Automated caregiver response evaluation with empathy scoring
- **Safety Guardrails**: Built-in protections against harmful advice and problematic interactions

## 📚 Documentation Structure

This documentation follows the [Diátaxis](https://diataxis.fr/) framework for technical documentation:

### [Tutorials](tutorials/index.md)

**Learning-oriented** - Step-by-step lessons to get you started:

- [Quickstart Guide](tutorials/quickstart.md) - Get up and running in minutes
- [Run Locally](tutorials/run-local.md) - Complete local setup walkthrough
- [Build Index](tutorials/build-index.md) - Create your knowledge base search index

### [How-to Guides](how-to/index.md)

**Problem-oriented** - Practical guides for specific tasks:

- [Add Dataset](how-to/add-dataset.md) - Integrate new document sources
- [Add Model](how-to/add-model.md) - Configure different LLM models
- [Enable FAISS](how-to/enable-faiss.md) - Set up semantic search
- [Add Citations](how-to/add-citations.md) - Include source references in responses

### [Reference](reference/index.md)

**Information-oriented** - Technical descriptions and API documentation:

- [API Documentation](reference/api/index.md) - FastAPI endpoints
- [Module Reference](reference/modules/persona.md) - Auto-generated API docs for all Python modules

### [Explanation](explanation/index.md)

**Understanding-oriented** - Background and design decisions:

- [Architecture](explanation/architecture.md) - System design and component interaction
- [Data Pipeline](explanation/data-pipeline.md) - Document processing and indexing
- [Evaluation & Iteration](explanation/evaluation-iteration.md) - Testing and improvement workflow
- [Safety Guardrails](explanation/safety-guardrails.md) - Safety mechanisms and red-team testing
- [Personas](explanation/personas.md) - Stage parameters and affect modeling

### [Decisions](decisions/index.md)

**Architecture Decision Records** (ADRs) - Why we made key technical choices:

- [ADR-0001: Docs Stack](decisions/ADR-0001-docs-stack.md) - MkDocs + Material + mkdocstrings

## 🚀 Quick Links

- **[Quickstart Tutorial](tutorials/quickstart.md)** - Get started in 5 minutes
- **[API Reference](reference/api/server.md)** - REST API documentation
- **[Architecture Overview](explanation/architecture.md)** - System design
- **[GitHub Repository](https://github.com/iloveangpao/dementia_simulation)** - Source code

## 🔧 Features

### Core Components

- **Patient Personas**: Configurable dementia stage simulation with memory, communication, and behavioral parameters
- **Chat System**: Multi-interface support (Web, CLI, API)
- **RAG Pipeline**: Context-aware response generation using retrieved documents
- **Caregiver Evaluation**: Pattern-based feedback scoring with empathy metrics
- **Document Knowledge Base**: PDF/text ingestion with preprocessing and indexing

### Technology Stack

- **Backend**: FastAPI, Python 3.10+
- **Frontend**: Streamlit
- **ML/AI**: Transformers, Sentence Transformers, FAISS
- **CLI**: Click framework
- **Testing**: Pytest, red-team safety tests

## 📖 Getting Started

If you're new to the project, start here:

1. **[Quickstart Guide](tutorials/quickstart.md)** - Install and run your first simulation
2. **[Architecture Overview](explanation/architecture.md)** - Understand the system design
3. **[API Documentation](reference/api/index.md)** - Explore available endpoints

## 🤝 Contributing

We welcome contributions! See our [GitHub repository](https://github.com/iloveangpao/dementia_simulation) for:

- Issue tracker
- Pull request guidelines
- Development setup
- Code of conduct

## 📄 License

This project is licensed under the MIT License. See the repository for full details.

---

*Built with ❤️ to help caregivers provide better dementia care*
