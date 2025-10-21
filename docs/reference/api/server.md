# API Server

Detailed FastAPI server implementation and endpoint documentation.

## Server Module

The FastAPI server implementation is located in `src/dementia_simulation/api/server.py`.

For detailed API documentation, see:
- [Runtime Endpoints](runtime.md) - Interactive docs at `/docs` and `/redoc`
- [API Reference](index.md) - Complete endpoint listing

## Configuration

Server configuration via environment variables:

```bash
# Server
API_HOST=localhost
API_PORT=8000
WORKERS=4

# CORS
CORS_ORIGINS=["http://localhost:8501", "http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# Authentication (optional)
ENABLE_API_KEYS=false
API_KEY=secret_key_here
```

## Running the Server

### Development Mode

```bash
# Using CLI
dementia-sim server

# Or directly with uvicorn
uvicorn dementia_simulation.api.server:app --reload
```

### Production Mode

```bash
# With gunicorn
gunicorn dementia_simulation.api.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# With uvicorn (optimized)
uvicorn dementia_simulation.api.server:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --no-access-log
```

## Middleware

### CORS Middleware

Handles cross-origin requests:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting Middleware

Prevents abuse:

```python
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
```

### Logging Middleware

Records all requests:

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "duration_ms": duration * 1000,
            "status_code": response.status_code
        }
    )
    return response
```

## Error Handling

Custom exception handlers:

```python
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

## Health Checks

Multiple health check endpoints:

```python
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@app.get("/health/ready")
async def readiness_check():
    """Readiness check (includes dependencies)"""
    # Check database connection
    # Check model availability
    # Check index loaded
    return {"status": "ready"}

@app.get("/health/live")
async def liveness_check():
    """Liveness check (minimal)"""
    return {"status": "alive"}
```

## Monitoring

### Metrics Endpoint

Prometheus-compatible metrics:

```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Performance Monitoring

```python
@app.middleware("http")
async def monitor_performance(request: Request, call_next):
    with request_duration.time():
        request_count.inc()
        response = await call_next(request)
    return response
```

## Testing

### Unit Tests

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    response = client.post(
        "/api/chat",
        json={
            "message": "Hello",
            "persona_id": "mild"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["persona_mood"]
```

### Integration Tests

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chat_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # List personas
        response = await ac.get("/api/personas")
        assert response.status_code == 200
        
        # Chat with persona
        response = await ac.post(
            "/api/chat",
            json={"message": "Hello", "persona_id": "mild"}
        )
        assert response.status_code == 200
```

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "dementia_simulation.api.server:app", \
     "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dementia-sim-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dementia-sim-api
  template:
    metadata:
      labels:
        app: dementia-sim-api
    spec:
      containers:
      - name: api
        image: dementia-sim:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_PORT
          value: "8000"
```

## Next Steps

- **[Runtime Endpoints](runtime.md)** - Interactive testing
- **[API Reference](index.md)** - Complete endpoint list
- **[Module Reference](../modules/persona.md)** - Python API

## Related Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [Gunicorn](https://gunicorn.org/)
