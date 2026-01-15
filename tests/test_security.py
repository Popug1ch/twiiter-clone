import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@patch('app.core.security.get_user_by_api_key')
def test_api_key_passes(mock_get_user, client):
    mock_get_user.return_value = type('User', (), {'id': 1})()

    resp = client.get("/health", headers={"Api-Key": "user1"})
    assert resp.status_code == 200


def test_no_api_key(client):
    resp = client.get("/health")
    assert resp.status_code == 401
