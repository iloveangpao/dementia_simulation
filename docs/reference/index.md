# API Reference

Complete technical reference for the Dementia Simulation platform, including API endpoints and module documentation.

## Quick Links

- **[API Server](api/server.md)** - FastAPI endpoints reference
- **[Runtime Endpoints](api/runtime.md)** - OpenAPI docs and testing

## Module Reference

Auto-generated API documentation from Python docstrings:

### Core Modules

- **[Persona](modules/persona.md)** - Patient persona simulation
- **[RAG](modules/rag.md)** - Retrieval-Augmented Generation pipeline
- **[Retriever](modules/retriever.md)** - Document search and indexing
- **[Evaluator](modules/evaluator.md)** - Feedback evaluation system
- **[Utils](modules/utils.md)** - Utility functions and helpers

### API & Interface

- **[API Server](modules/cli.md)** - FastAPI server implementation
- **[CLI](modules/cli.md)** - Command-line interface

## Using This Reference

### For Developers

If you're building on top of the platform:

1. Start with **[API Server](api/server.md)** for REST endpoints
2. Check **[Module docs](modules/persona.md)** for Python API
3. Review examples in each module page

### For Contributors

If you're contributing to the codebase:

1. Follow existing docstring patterns (Google style)
2. Update module docs when adding features
3. Add examples to docstrings
4. Keep documentation in sync with code

## Docstring Style

We use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """Short description of the function.
    
    Longer description that provides more context and explains
    the behavior in detail.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        ValueError: If param1 is empty
        
    Example:
        ```python
        result = example_function("test", 42)
        if result:
            print("Success!")
        ```
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    return len(param1) > param2
```

## API Versioning

Current API version: **v1.0**

Version format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

## Getting Help

- **[Tutorials](../tutorials/index.md)** - Learn the basics
- **[How-to Guides](../how-to/index.md)** - Solve specific problems
- **[Explanation](../explanation/index.md)** - Understand concepts
- **[GitHub Issues](https://github.com/iloveangpao/dementia_simulation/issues)** - Report bugs or request features
