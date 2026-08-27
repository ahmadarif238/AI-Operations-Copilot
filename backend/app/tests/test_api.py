from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}

def test_ask_endpoint_mock():
    # Test /ask with mock response (since we haven't set up full RAG in test env)
    response = client.post(
        "/api/v1/ask",
        json={"query": "test query", "user_id": "00000000-0000-0000-0000-000000000000"}
    )
    # Should return 200 with the mocked answer from endpoints.py
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "answer" in data
    # Robust check: can be "Processed by Ops Copilot" (fallback) or "I don't have information..." (Retreival Agent)
    assert any(x in data["answer"] for x in ["Processed by Ops Copilot", "I don't have information", "mocked"])

def test_log_ingestion_accepted():
    response = client.post(
        "/api/v1/log",
        json={
            "type": "INFO", 
            "message": "Test log", 
            "meta": {"env": "test"}
        }
    )
    # Expect 202 Accepted
    assert response.status_code == 202
    data = response.json()
    assert data["status"] in ["accepted", "accepted_db_only"]
    assert "job_id" in data
