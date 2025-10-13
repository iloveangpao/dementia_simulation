# Utils Module

Utility functions and helper classes.

## Overview

The `utils` module provides common utilities used throughout the platform:

- Configuration management
- File I/O helpers
- Text processing utilities
- Logging setup
- Validation functions

## Quick Example

```python
from dementia_simulation.utils import (
    load_config,
    save_session,
    clean_text,
    setup_logging
)

# Load configuration
config = load_config("config.yaml")

# Setup logging
logger = setup_logging(level="INFO")

# Clean text
cleaned = clean_text(raw_text)

# Save session
save_session(session_data, "data/sessions/session_123.json")
```

## Module Reference

The utils module is located in `src/dementia_simulation/utils/`.

**Key Functions**:

- `load_config()` - Load YAML configuration
- `save_config()` - Save configuration to file
- `setup_logging()` - Configure logging system
- `clean_text()` - Text preprocessing
- `save_session()` - Persist conversation session
- `load_session()` - Load saved session

**Configuration Utilities**:

- Environment variable loading
- Path management
- File I/O helpers

For full module documentation, see the source code with inline docstrings.

## Related

- **[Architecture](../../explanation/architecture.md)** - System overview
- **[Run Locally](../../tutorials/run-local.md)** - Setup guide
