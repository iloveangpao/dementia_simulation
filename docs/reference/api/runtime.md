# Runtime Endpoints

Interactive API documentation and testing tools available when the server is running.

## Interactive Documentation

### Swagger UI

**URL**: [http://localhost:8000/docs](http://localhost:8000/docs)

Features:
- Interactive API explorer
- Test endpoints directly in browser
- View request/response schemas
- Auto-generated from OpenAPI spec

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-03-swagger-02.png)

### ReDoc

**URL**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Features:
- Clean, three-panel layout
- Searchable documentation
- Code samples in multiple languages
- Responsive design

![ReDoc](https://fastapi.tiangolo.com/img/index/index-04-redoc-02.png)

## OpenAPI Specification

### JSON Spec

**URL**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

Download the OpenAPI 3.0 specification:

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

Use with:
- API client generators (OpenAPI Generator, Swagger Codegen)
- Testing tools (Postman, Insomnia)
- Documentation generators
- Mock servers

## Testing with cURL

### Health Check

```bash
curl http://localhost:8000/health
```

### Chat Request

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How are you feeling today?",
    "persona_id": "mild",
    "session_id": "test_session_123"
  }'
```

### Evaluate Feedback

```bash
curl -X POST http://localhost:8000/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "That'\''s okay. I understand.",
    "context": {
      "persona_stage": "mild"
    }
  }'
```

### List Personas

```bash
curl http://localhost:8000/api/personas
```

## Testing with HTTPie

More human-friendly HTTP client:

```bash
# Install
pip install httpie

# Health check
http GET localhost:8000/health

# Chat
http POST localhost:8000/api/chat \
  message="Hello" \
  persona_id="mild"

# Evaluate
http POST localhost:8000/api/evaluate \
  text="I understand how you feel"
```

## Testing with Postman

### Import OpenAPI Spec

1. Open Postman
2. Click Import
3. Enter URL: `http://localhost:8000/openapi.json`
4. Postman auto-generates collection

### Example Collection

```json
{
  "info": {
    "name": "Dementia Simulation API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Chat",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/chat",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"message\": \"Hello\",\n  \"persona_id\": \"mild\"\n}"
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

## Testing with Python

### requests Library

```python
import requests

base_url = "http://localhost:8000"

# Health check
response = requests.get(f"{base_url}/health")
print(response.json())

# Chat
response = requests.post(
    f"{base_url}/api/chat",
    json={
        "message": "How are you?",
        "persona_id": "mild"
    }
)
print(response.json()['response'])

# Evaluate
response = requests.post(
    f"{base_url}/api/evaluate",
    json={
        "text": "I understand"
    }
)
print(response.json()['scores'])
```

### httpx Library (async)

```python
import asyncio
import httpx

async def test_api():
    async with httpx.AsyncClient() as client:
        # Health check
        response = await client.get("http://localhost:8000/health")
        print(response.json())
        
        # Chat
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={
                "message": "Hello",
                "persona_id": "mild"
            }
        )
        print(response.json())

asyncio.run(test_api())
```

## Load Testing

### Using locust

```python
from locust import HttpUser, task, between

class DementiaSimUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def chat(self):
        self.client.post(
            "/api/chat",
            json={
                "message": "Hello",
                "persona_id": "mild"
            }
        )
    
    @task
    def evaluate(self):
        self.client.post(
            "/api/evaluate",
            json={
                "text": "I understand"
            }
        )
```

Run:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

### Using Apache Bench

```bash
# 1000 requests, 10 concurrent
ab -n 1000 -c 10 \
  -p chat.json \
  -T application/json \
  http://localhost:8000/api/chat
```

## Monitoring Requests

### View Logs

```bash
# Tail application logs
tail -f logs/app.log

# Filter by endpoint
tail -f logs/app.log | grep "/api/chat"

# Filter by session
tail -f logs/app.log | grep "session_id=abc123"
```

### Access Logs

```bash
# Enable access logs
uvicorn dementia_simulation.api.server:app \
  --log-level info \
  --access-log

# View access logs
tail -f logs/access.log
```

## Debugging

### Enable Debug Mode

```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart server
dementia-sim server
```

### Debug Specific Request

```python
import logging
from dementia_simulation.api import server

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Make request with debug
response = client.post(
    "/api/chat",
    json={"message": "test", "persona_id": "mild"}
)
print(response.json())
```

## Next Steps

- **[API Reference](index.md)** - Complete endpoint documentation
- **[Server Implementation](server.md)** - Server details
- **[How-to Guides](../../how-to/index.md)** - Common tasks

## Related Resources

- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Swagger Editor](https://editor.swagger.io/)
- [Postman](https://www.postman.com/)
- [HTTPie](https://httpie.io/)
