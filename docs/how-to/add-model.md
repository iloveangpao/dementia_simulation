# Add Model

Configure and use different language models for response generation in the Dementia Simulation platform.

## Overview

The platform supports multiple LLM backends:

- **Local Models** (HuggingFace) - Privacy-focused, offline capable
- **OpenAI Models** (GPT-3.5/4) - High quality, requires API key
- **Custom Models** - Bring your own model

## Default Model

Out of the box, the system uses:

```bash
DEFAULT_MODEL=microsoft/DialoGPT-medium
```

This model:
- ✅ Works offline after download
- ✅ No API key required
- ✅ Reasonable quality for conversation
- ⚠️ ~350MB model size

## Switching Models

### Method 1: Environment Variable

Edit `.env` file:

```bash
# Use a different HuggingFace model
DEFAULT_MODEL=facebook/blenderbot-400M-distill

# Or OpenAI
DEFAULT_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=sk-your-key-here
```

Restart the application:

```bash
dementia-sim server
```

### Method 2: Runtime Configuration

In Python code:

```python
from dementia_simulation.rag import DementiaRAGPipeline

# Initialize with specific model
pipeline = DementiaRAGPipeline(
    model_name="gpt-3.5-turbo",
    openai_api_key="sk-your-key-here"
)
```

### Method 3: API Request

When calling the API:

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "persona_id": "mild",
    "model_override": "gpt-4"
  }'
```

## Supported Models

### HuggingFace Models (Free, Local)

#### Conversational Models

**DialoGPT (Recommended for offline)**

```bash
# Small (~125MB) - Fast, lower quality
DEFAULT_MODEL=microsoft/DialoGPT-small

# Medium (~350MB) - Balanced (default)
DEFAULT_MODEL=microsoft/DialoGPT-medium

# Large (~775MB) - Best quality, slower
DEFAULT_MODEL=microsoft/DialoGPT-large
```

**BlenderBot**

```bash
# Distilled (~400MB) - Good balance
DEFAULT_MODEL=facebook/blenderbot-400M-distill

# Full size (~2.7GB) - Higher quality
DEFAULT_MODEL=facebook/blenderbot-1B-distill
```

#### General Purpose Models

**GPT-2**

```bash
# Small
DEFAULT_MODEL=gpt2

# Medium
DEFAULT_MODEL=gpt2-medium

# Large
DEFAULT_MODEL=gpt2-large
```

### OpenAI Models (Paid, Cloud)

**GPT-3.5 Turbo** (Recommended for production)

```bash
DEFAULT_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=sk-...
```

Benefits:
- Excellent quality
- Fast inference
- Cost-effective ($0.001/1K tokens)

**GPT-4**

```bash
DEFAULT_MODEL=gpt-4
OPENAI_API_KEY=sk-...
```

Benefits:
- Best quality
- Advanced reasoning
- Higher cost ($0.03/1K tokens)

**GPT-4 Turbo**

```bash
DEFAULT_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-...
```

### Local LLaMA Models

Using Ollama for local LLaMA:

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama2

# Configure
DEFAULT_MODEL=llama2
MODEL_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
```

Python integration:

```python
from dementia_simulation.rag import DementiaRAGPipeline

pipeline = DementiaRAGPipeline(
    model_name="llama2",
    model_provider="ollama",
    ollama_host="http://localhost:11434"
)
```

## Model Configuration

### Performance Tuning

Adjust generation parameters in `.env`:

```bash
# Temperature (0.0-2.0) - Higher = more creative
MODEL_TEMPERATURE=0.7

# Max tokens per response
MODEL_MAX_TOKENS=150

# Top-p sampling (0.0-1.0)
MODEL_TOP_P=0.9

# Frequency penalty (-2.0 to 2.0)
MODEL_FREQUENCY_PENALTY=0.0

# Presence penalty (-2.0 to 2.0)
MODEL_PRESENCE_PENALTY=0.0
```

### Memory Optimization

For systems with limited RAM:

```bash
# Use smaller model
DEFAULT_MODEL=microsoft/DialoGPT-small

# Enable 8-bit quantization
MODEL_LOAD_IN_8BIT=true

# Limit batch size
MODEL_BATCH_SIZE=1
```

### GPU Acceleration

Enable GPU for faster inference:

```bash
# Install CUDA-enabled PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Verify GPU available
python -c "import torch; print(torch.cuda.is_available())"
```

Configure device:

```bash
# In .env
MODEL_DEVICE=cuda  # or 'cpu' for CPU-only

# Specific GPU
MODEL_DEVICE=cuda:0  # First GPU
MODEL_DEVICE=cuda:1  # Second GPU
```

## Custom Model Integration

### Local Custom Model

For your own trained model:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from dementia_simulation.rag import DementiaRAGPipeline

# Load your model
model_path = "/path/to/your/model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# Use in pipeline
pipeline = DementiaRAGPipeline(
    model_name=model_path,
    custom_model=model,
    custom_tokenizer=tokenizer
)
```

### Custom API Endpoint

For external model APIs:

```python
import requests
from dementia_simulation.rag import DementiaRAGPipeline

class CustomModelProvider:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
    
    def generate(self, prompt, **kwargs):
        response = requests.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"prompt": prompt, **kwargs}
        )
        return response.json()["text"]

# Use custom provider
provider = CustomModelProvider(
    api_url="https://your-api.com/generate",
    api_key="your-key"
)

pipeline = DementiaRAGPipeline(custom_provider=provider)
```

## Model Selection Guidelines

### By Use Case

**Development/Testing**
- Use: `microsoft/DialoGPT-small`
- Why: Fast, small, no API costs

**Production (Budget)**
- Use: `gpt-3.5-turbo`
- Why: Best quality/cost ratio

**Production (Quality)**
- Use: `gpt-4`
- Why: Best overall quality

**Offline/Privacy**
- Use: `microsoft/DialoGPT-large`
- Why: No internet required

**Research**
- Use: `facebook/blenderbot-1B-distill`
- Why: Better conversation quality than DialoGPT

### By System Resources

**Low RAM (<8GB)**
```bash
DEFAULT_MODEL=microsoft/DialoGPT-small
MODEL_LOAD_IN_8BIT=true
```

**Moderate RAM (8-16GB)**
```bash
DEFAULT_MODEL=microsoft/DialoGPT-medium
```

**High RAM (>16GB) + GPU**
```bash
DEFAULT_MODEL=facebook/blenderbot-1B-distill
MODEL_DEVICE=cuda
```

**Cloud/API Only**
```bash
DEFAULT_MODEL=gpt-3.5-turbo
```

## Testing Models

### Benchmark Script

Test different models:

```python
import time
from dementia_simulation.rag import DementiaRAGPipeline

models = [
    "microsoft/DialoGPT-small",
    "microsoft/DialoGPT-medium",
    "gpt-3.5-turbo"
]

test_prompt = "I'm feeling confused about where I am."

for model_name in models:
    pipeline = DementiaRAGPipeline(model_name=model_name)
    
    start = time.time()
    response = pipeline.generate_response(
        patient_message="",
        caregiver_message=test_prompt,
        persona_stage="mild"
    )
    duration = time.time() - start
    
    print(f"\nModel: {model_name}")
    print(f"Time: {duration:.2f}s")
    print(f"Response: {response['response'][:100]}...")
    print(f"Quality: {response.get('confidence_score', 'N/A')}")
```

### Quality Evaluation

Compare model outputs:

```bash
# Create test script
cat > test_models.py << 'EOF'
from dementia_simulation.evaluator import CaregiverFeedbackEvaluator

evaluator = CaregiverFeedbackEvaluator()

responses = {
    "DialoGPT-small": "That's okay. Tell me more.",
    "DialoGPT-medium": "I understand this must be confusing. You're safe here with me.",
    "GPT-3.5": "It's completely normal to feel that way. Let's talk about what's making you feel confused, and we can work through it together."
}

for model, response in responses.items():
    result = evaluator.analyze_feedback(response)
    print(f"{model}: {result['scores']['overall_score']:.2f}")
EOF

python test_models.py
```

## Troubleshooting

### Model Download Fails

**Problem**: Timeout or network error

**Solution**:
```bash
# Pre-download model
python -c "from transformers import AutoModel; AutoModel.from_pretrained('microsoft/DialoGPT-medium')"

# Check cache
ls ~/.cache/huggingface/hub/
```

### Out of Memory

**Problem**: CUDA out of memory or system RAM exceeded

**Solutions**:

1. Use smaller model
2. Enable 8-bit loading:
   ```bash
   MODEL_LOAD_IN_8BIT=true
   ```
3. Use CPU:
   ```bash
   MODEL_DEVICE=cpu
   ```

### OpenAI API Errors

**Problem**: "Invalid API key" or rate limits

**Solutions**:

1. Verify API key:
   ```bash
   echo $OPENAI_API_KEY
   ```

2. Check quotas at [platform.openai.com](https://platform.openai.com/)

3. Add retry logic:
   ```bash
   MODEL_MAX_RETRIES=3
   MODEL_RETRY_DELAY=2
   ```

### Slow Generation

**Problem**: Responses take too long

**Solutions**:

1. Use GPU:
   ```bash
   MODEL_DEVICE=cuda
   ```

2. Reduce max tokens:
   ```bash
   MODEL_MAX_TOKENS=100
   ```

3. Use faster model:
   ```bash
   DEFAULT_MODEL=microsoft/DialoGPT-small
   ```

## Next Steps

- **[Architecture](../explanation/architecture.md)** - Understand model integration
- **[API Reference](../reference/modules/rag.md)** - RAG pipeline documentation
- **[Enable FAISS](enable-faiss.md)** - Improve retrieval

## Need Help?

- 📖 [RAG Pipeline Explanation](../explanation/architecture.md)
- 🐛 [Report Issues](https://github.com/iloveangpao/dementia_simulation/issues)
- 💬 [Ask Questions](https://github.com/iloveangpao/dementia_simulation/discussions)
