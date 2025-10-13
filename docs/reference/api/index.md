# API Reference

FastAPI REST API documentation for the Dementia Simulation platform.

## Base URL

```
http://localhost:8000
```

For production deployments, replace with your actual domain.

## Authentication

Currently optional. Can be enabled with API keys:

```bash
# In .env
ENABLE_API_KEYS=true
API_KEY=your_secret_key_here
```

**Header**:
```
Authorization: Bearer your_secret_key_here
```

## Rate Limiting

Default rate limits:

- **100 requests/minute** per IP
- **1000 requests/hour** per IP
- **20 requests/minute** per session

## API Documentation

### Interactive Documentation

When the server is running, access interactive API docs:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### OpenAPI Specification

Download the OpenAPI JSON spec:

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

Or visit: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Core Endpoints

### Health Check

```http
GET /health
```

Check API server status.

**Response** `200 OK`:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Chat

```http
POST /api/chat
```

Generate a response from the patient persona.

**Request Body**:
```json
{
  "message": "How are you feeling today?",
  "persona_id": "mild",
  "session_id": "optional_session_id"
}
```

**Response** `200 OK`:
```json
{
  "response": "I'm doing okay, I think... though I'm not sure if we've met before?",
  "persona_mood": "neutral",
  "confidence_score": 0.85,
  "processing_time": 1.23,
  "model_used": "microsoft/DialoGPT-medium",
  "retrieved_docs": 3,
  "session_id": "abc123..."
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How are you feeling?",
    "persona_id": "mild"
  }'
```

### Evaluate Feedback

```http
POST /api/evaluate
```

Evaluate caregiver communication quality.

**Request Body**:
```json
{
  "text": "That's okay. I understand how you're feeling.",
  "context": {
    "persona_stage": "mild",
    "patient_message": "I keep forgetting things"
  }
}
```

**Response** `200 OK`:
```json
{
  "scores": {
    "reassurance_score": 0.90,
    "confrontation_score": 0.0,
    "overall_score": 0.90
  },
  "analysis": {
    "feedback_type": "supportive",
    "patterns_detected": {
      "reassurance": ["understand", "okay"],
      "confrontation": []
    }
  },
  "recommendations": [
    "Good use of validation language",
    "Consider adding more specific empathy"
  ]
}
```

### List Personas

```http
GET /api/personas
```

Get available patient personas.

**Response** `200 OK`:
```json
{
  "personas": [
    {
      "id": "mild",
      "name": "Mild Stage",
      "stage": "mild",
      "description": "Early cognitive changes, mostly independent"
    },
    {
      "id": "moderate",
      "name": "Moderate Stage",
      "stage": "moderate",
      "description": "Noticeable decline, requires assistance"
    },
    {
      "id": "severe",
      "name": "Severe Stage",
      "stage": "severe",
      "description": "Significant impairment, needs full-time care"
    }
  ]
}
```

### Update Mood

```http
POST /api/mood
```

Manually update persona mood (for testing).

**Request Body**:
```json
{
  "session_id": "abc123",
  "mood_value": 0.5,
  "trigger": "validation"
}
```

**Response** `200 OK`:
```json
{
  "success": true,
  "new_mood": 0.3,
  "mood_label": "content"
}
```

### System Stats

```http
GET /api/stats
```

Get system statistics.

**Response** `200 OK`:
```json
{
  "total_personas": 3,
  "active_sessions": 5,
  "pipeline_stats": {
    "total_requests": 1234,
    "avg_response_time": 1.45,
    "cache_hit_rate": 0.67
  },
  "uptime": "2024-01-15T10:30:00Z"
}
```

## Error Responses

### 400 Bad Request

Invalid request parameters:

```json
{
  "detail": "Invalid persona_id. Must be one of: mild, moderate, severe"
}
```

### 429 Too Many Requests

Rate limit exceeded:

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### 500 Internal Server Error

Server error:

```json
{
  "detail": "Internal server error",
  "request_id": "req_abc123"
}
```

## WebSocket Support

(Coming soon)

Real-time chat via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "Hello",
    persona_id: "mild"
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log(response.text);
};
```

## Client Libraries

### Python

```python
import requests

class DementiaSimClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def chat(self, message, persona_id="mild", session_id=None):
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "message": message,
                "persona_id": persona_id,
                "session_id": session_id
            }
        )
        return response.json()
    
    def evaluate(self, text, context=None):
        response = requests.post(
            f"{self.base_url}/api/evaluate",
            json={
                "text": text,
                "context": context or {}
            }
        )
        return response.json()

# Usage
client = DementiaSimClient()
result = client.chat("How are you?", persona_id="mild")
print(result['response'])
```

### JavaScript/TypeScript

```typescript
class DementiaSimClient {
  constructor(private baseUrl: string = 'http://localhost:8000') {}
  
  async chat(message: string, personaId: string = 'mild', sessionId?: string) {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        persona_id: personaId,
        session_id: sessionId
      })
    });
    return response.json();
  }
  
  async evaluate(text: string, context?: any) {
    const response = await fetch(`${this.baseUrl}/api/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, context })
    });
    return response.json();
  }
}

// Usage
const client = new DementiaSimClient();
const result = await client.chat('How are you?', 'mild');
console.log(result.response);
```

## Next Steps

- **[Server Implementation](server.md)** - Detailed endpoint documentation
- **[Runtime Endpoints](runtime.md)** - Testing with interactive docs
- **[Module Reference](../modules/persona.md)** - Python API documentation

## Related Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [REST API Best Practices](https://restfulapi.net/)
