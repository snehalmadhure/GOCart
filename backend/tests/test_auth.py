from fastapi.testclient import TestClient

from app.main import app


def test_protected_routes_reject_missing_or_invalid_tokens(monkeypatch):
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-supabase-jwt-secret")
    with TestClient(app) as client:
        assert client.get("/api/v1/pantry").status_code == 401
        assert client.get("/api/v1/pantry", headers={"Authorization": "Bearer invalid"}).status_code == 401
