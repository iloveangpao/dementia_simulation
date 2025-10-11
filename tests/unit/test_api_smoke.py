from fastapi.testclient import TestClient
from src.dementia_simulation.api.server import app


def test_chat_and_evaluate_smoke():
    client = TestClient(app)
    r = client.post("/chat", json={"session_id": "s1", "text": "hello"})
    assert r.status_code == 200
    assert "reply" in r.json() and "mood" in r.json()

    e = client.post("/evaluate", json={"transcript": "I understand. It's okay."})
    assert e.status_code == 200
    body = e.json()
    assert "overall_score" in body and "flags" in body
