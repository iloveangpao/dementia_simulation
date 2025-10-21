# How-to Guides

Problem-oriented guides for accomplishing specific tasks with the Dementia Simulation platform.

## 📋 Available Guides

### [Add Dataset](add-dataset.md)

Integrate new document sources into your knowledge base.

**Use when**: You need to add research papers, care guides, or custom documentation

**Topics covered**:
- Supported document formats
- Preprocessing custom data
- Handling special formats (medical records, structured data)
- Updating existing datasets

---

### [Add Model](add-model.md)

Configure and use different language models for conversation generation.

**Use when**: You want to try different LLM backends or optimize for specific use cases

**Topics covered**:
- OpenAI GPT models
- HuggingFace models
- Local models
- Model configuration and selection

---

### [Enable FAISS](enable-faiss.md)

Set up semantic search with FAISS vector indexing.

**Use when**: You need better search quality than keyword-based TF-IDF

**Topics covered**:
- FAISS installation and configuration
- Choosing embedding models
- Index optimization
- GPU acceleration

---

### [Add Citations](add-citations.md)

Include source references in generated responses.

**Use when**: You need to track which documents informed each response

**Topics covered**:
- Enabling citation mode
- Citation formats
- Inline vs. footer citations
- Filtering by source type

---

## 🎯 Quick Tasks

Common tasks with quick solutions:

### Change API Port

```bash
# Method 1: Environment variable
export API_PORT=8001
dementia-sim server

# Method 2: Direct uvicorn
uvicorn dementia_simulation.api.server:app --port 8001
```

### Switch Persona Stage

```python
from dementia_simulation.persona import DementiaPersona

persona = DementiaPersona(stage="severe")  # mild, moderate, or severe
```

### Clear Session History

```bash
rm -rf data/sessions/*
```

### Update Dependencies

```bash
# With Poetry
poetry update

# With pip
pip install --upgrade -r requirements.txt
```

## 🔍 Find a Guide

Use the search bar above or browse by category:

- **Data Management**: [Add Dataset](add-dataset.md)
- **Configuration**: [Add Model](add-model.md), [Enable FAISS](enable-faiss.md)
- **Features**: [Add Citations](add-citations.md)

## 💡 Tips

!!! tip "Prerequisites"
    Most guides assume you've completed the [Quickstart Tutorial](../tutorials/quickstart.md) and have the system running.

!!! note "Testing Changes"
    After making configuration changes, restart the service:
    ```bash
    # Kill and restart server
    dementia-sim server
    ```

## Can't Find What You Need?

- **[Tutorials](../tutorials/index.md)** - Step-by-step learning
- **[Reference](../reference/index.md)** - API documentation
- **[Explanation](../explanation/index.md)** - Understanding concepts
- **[GitHub Issues](https://github.com/iloveangpao/dementia_simulation/issues)** - Report problems or request guides
