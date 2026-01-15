import pytest

def test_health(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    print("HEALTH OK")

def test_root(test_client):  # ← client → test_client
    response = test_client.get("/")
    assert response.status_code == 200
    print("ROOT SPA OK")

def test_api_404(test_client):
    response = test_client.get("/api/nonexistent")
    assert response.status_code == 404 
    print("API 404 OK")

