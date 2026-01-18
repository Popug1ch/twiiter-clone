import pytest
from fastapi import status


class TestHealthEndpoints:
    def test_health(self, client):
        assert client.get("/health").status_code == 200

    def test_root(self, client):
        assert client.get("/").json() == {"message": "Test API"}

    def test_favicon(self, client):
        assert client.get("/favicon.ico").status_code == 200

    def test_api_404(self, client):
        assert client.get("/api/nonexistent").status_code == 404

    def test_method_405(self, client):
        assert client.post("/health").status_code == 405

    @pytest.mark.parametrize("origin", ["http://localhost:3000", "https://example.com"])
    def test_cors(self, client, origin):
        resp = client.get("/health", headers={"Origin": origin})
        assert resp.headers["access-control-allow-origin"] == "*"
