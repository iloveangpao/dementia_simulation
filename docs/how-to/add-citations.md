# Add Citations

Configure the system to include source references in generated responses, enabling transparency and trust.

## Overview

Citations allow you to:
- Track which documents informed each response
- Provide evidence for claims
- Enable fact-checking
- Build trust with users

## Quick Setup

### Enable Citations

Edit `.env`:

```bash
# Enable citations in responses
ENABLE_CITATIONS=true

# Citation style
CITATION_STYLE=inline  # or 'footer', 'numbered'

# Number of sources to cite
MAX_CITATIONS=3
```

Restart the service:

```bash
dementia-sim server
```

### Test Citations

```python
from dementia_simulation.rag import DementiaRAGPipeline

pipeline = DementiaRAGPipeline(enable_citations=True)

response = pipeline.generate_response(
    patient_message="I keep forgetting things",
    caregiver_message="Tell me more about that",
    persona_stage="mild"
)

print(response['response'])
print("\nSources:")
for source in response.get('sources', []):
    print(f"- {source['file']} (confidence: {source['score']:.2f})")
```

## Citation Styles

### Inline Citations

Sources embedded in the text:

```
Memory loss is common in early dementia [1]. Strategies like 
using calendars can help [2]. Validation therapy is effective [1].

Sources:
[1] dementia_care_guide.pdf
[2] communication_strategies.pdf
```

Configuration:

```bash
CITATION_STYLE=inline
CITATION_FORMAT=[{number}]  # or ({number}) or ^{number}
```

### Footer Citations

All sources listed at the end:

```
Memory loss is common in early dementia. Strategies like using 
calendars and reminders can help maintain independence. 
Validation therapy has shown effectiveness.

---
Sources:
1. dementia_care_guide.pdf - "Memory Loss in Dementia"
2. communication_strategies.pdf - "Supporting Daily Tasks"
3. validation_therapy.pdf - "Therapeutic Approaches"
```

Configuration:

```bash
CITATION_STYLE=footer
SHOW_SOURCE_EXCERPTS=true  # Include text excerpts
```

### Numbered Citations

Traditional academic style:

```
Memory loss is one of the earliest signs of dementia.[1] 
Research shows that memory aids can significantly improve 
daily functioning.[2,3]

References:
[1] Smith et al. (2023). "Early Signs of Dementia." 
    dementia_care_guide.pdf
[2] Johnson, M. "Communication Strategies." 
    communication_strategies.pdf
[3] Brown, A. "Memory Aids Study." clinical_research.pdf
```

Configuration:

```bash
CITATION_STYLE=numbered
CITATION_INCLUDE_AUTHORS=true
CITATION_INCLUDE_YEAR=true
```

## Response Format with Citations

### API Response

```json
{
  "response": "Memory issues are common in early dementia [1]...",
  "citations": [
    {
      "id": 1,
      "source_file": "dementia_care_guide.pdf",
      "chunk_id": "chunk_042",
      "relevance_score": 0.89,
      "text": "Memory loss is one of the most common...",
      "page": 12
    }
  ],
  "retrieved_docs_count": 5,
  "cited_docs_count": 1
}
```

### Streamlit UI

Citations appear as expandable sections:

```
💬 Response: Memory issues are common...

📚 Sources (3):
▸ dementia_care_guide.pdf (Score: 0.89)
  "Memory loss is one of the most common early signs..."
  
▸ communication_strategies.pdf (Score: 0.82)
  "When addressing memory concerns..."
```

## Advanced Configuration

### Filter by Source Type

Only cite certain document types:

```bash
# In .env
CITATION_ALLOWED_TYPES=pdf,txt
CITATION_EXCLUDE_TYPES=csv,json
```

Or in code:

```python
pipeline = DementiaRAGPipeline(
    enable_citations=True,
    citation_filters={'type': ['pdf', 'txt']}
)
```

### Citation Confidence Threshold

Only cite high-confidence sources:

```bash
# In .env
CITATION_MIN_SCORE=0.75  # 0.0 to 1.0
```

Lower threshold = more citations
Higher threshold = only best sources

### Deduplication

Avoid citing the same document multiple times:

```bash
CITATION_DEDUPLICATE=true
CITATION_MAX_PER_SOURCE=1
```

### Include Metadata

Add rich metadata to citations:

```python
# In retriever.py or rag_pipeline.py

def format_citation(chunk, index):
    return {
        'id': index + 1,
        'source_file': chunk['source_file'],
        'relevance_score': chunk['score'],
        'text_excerpt': chunk['text'][:200],
        'page': chunk.get('page', 'N/A'),
        'section': chunk.get('section', 'N/A'),
        'date_added': chunk.get('date_added', 'N/A'),
        'url': chunk.get('url', None)
    }
```

## Use Cases

### Medical/Clinical Settings

Requires evidence-based responses:

```bash
ENABLE_CITATIONS=true
CITATION_STYLE=numbered
CITATION_MIN_SCORE=0.80
CITATION_INCLUDE_EXCERPTS=true
```

### Training/Education

Show learners where information comes from:

```bash
ENABLE_CITATIONS=true
CITATION_STYLE=inline
SHOW_SOURCE_EXCERPTS=true
MAX_CITATIONS=5
```

### Research/Analysis

Comprehensive source tracking:

```bash
ENABLE_CITATIONS=true
CITATION_STYLE=footer
CITATION_INCLUDE_ALL_RETRIEVED=true
LOG_RETRIEVAL_DETAILS=true
```

## Custom Citation Templates

### Define Custom Format

Create `config/citation_template.py`:

```python
def format_citation(citation, style='custom'):
    if style == 'custom':
        return f"""
📄 {citation['source_file']}
   Relevance: {citation['relevance_score']:.0%}
   "{citation['text'][:100]}..."
   Page {citation.get('page', 'N/A')}
"""
    return default_format(citation)
```

### Use in Pipeline

```python
from config.citation_template import format_citation

pipeline = DementiaRAGPipeline(
    enable_citations=True,
    citation_formatter=format_citation
)
```

## Citation Analytics

### Track Citation Usage

```python
# Add to telemetry
def log_citation(citation):
    metrics = {
        'source': citation['source_file'],
        'score': citation['relevance_score'],
        'timestamp': datetime.now()
    }
    # Log to database or file
    logging.info(f"Citation used: {metrics}")
```

### Popular Sources Report

```bash
# Generate report
python scripts/citation_report.py --days 30

# Output:
Top cited sources (last 30 days):
1. dementia_care_guide.pdf - 145 citations
2. communication_strategies.pdf - 98 citations
3. clinical_guidelines.pdf - 67 citations
```

## Testing Citations

### Verify Citation Accuracy

```python
def test_citation_accuracy():
    pipeline = DementiaRAGPipeline(enable_citations=True)
    
    test_cases = [
        "What are memory loss symptoms?",
        "How to handle agitation?",
        "Communication strategies for dementia"
    ]
    
    for query in test_cases:
        response = pipeline.generate_response(
            patient_message="",
            caregiver_message=query,
            persona_stage="mild"
        )
        
        citations = response.get('citations', [])
        print(f"\nQuery: {query}")
        print(f"Citations: {len(citations)}")
        
        for cite in citations:
            print(f"  - {cite['source_file']} ({cite['relevance_score']:.2f})")
            assert cite['relevance_score'] > 0.7, "Low relevance score"
```

### Check Citation Coverage

```python
def check_citation_coverage():
    """Verify important documents are being cited"""
    
    required_sources = [
        'dementia_care_guide.pdf',
        'clinical_guidelines.pdf'
    ]
    
    # Run test queries
    # Check if required sources appear in citations
    # Alert if coverage < 80%
```

## Troubleshooting

### No Citations Generated

**Problem**: Responses have no citations

**Solutions**:

1. Verify enabled:
   ```bash
   grep ENABLE_CITATIONS .env
   ```

2. Check threshold:
   ```bash
   # Lower to see if documents match
   CITATION_MIN_SCORE=0.50
   ```

3. Verify documents indexed:
   ```bash
   python search.py "test query"
   ```

### Too Many Citations

**Problem**: Response cluttered with citations

**Solution**:
```bash
MAX_CITATIONS=2  # Limit to top 2 sources
CITATION_MIN_SCORE=0.85  # Raise threshold
```

### Citations Not Relevant

**Problem**: Cited sources don't match content

**Solutions**:

1. Rebuild index:
   ```bash
   python build_index.py
   ```

2. Check retrieval quality:
   ```bash
   python search.py "exact phrase from response"
   ```

3. Improve embeddings:
   ```bash
   EMBEDDING_MODEL=all-mpnet-base-v2
   ```

## Best Practices

### ✅ Do

- Enable citations for medical/clinical use
- Set reasonable confidence thresholds (0.75+)
- Include source excerpts for verification
- Log citation usage for analytics
- Test citation accuracy regularly

### ❌ Don't

- Over-cite (clutters response)
- Cite low-confidence sources (<0.70)
- Include too much excerpt text
- Forget to filter outdated sources
- Skip citation accuracy testing

## Next Steps

- **[Data Pipeline](../explanation/data-pipeline.md)** - Understanding retrieval
- **[RAG Reference](../reference/modules/rag.md)** - Pipeline API
- **[Enable FAISS](enable-faiss.md)** - Improve retrieval quality

## Need Help?

- 📖 [RAG Pipeline Explanation](../explanation/architecture.md)
- 🐛 [Report Issues](https://github.com/iloveangpao/dementia_simulation/issues)
- 💬 [Ask Questions](https://github.com/iloveangpao/dementia_simulation/discussions)
