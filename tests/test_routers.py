import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@patch('app.crud.tweet.create_tweet')
def test_post_tweet(mock_create_tweet, client):
    mock_create_tweet.return_value = 123

    resp = client.post(
        "/api/tweets",
        json={"tweet_data": "Hello!"},
        headers={"Api-Key": "user1"}
    )
    assert resp.status_code == 200
    assert resp.json()["tweet_id"] == 123


@patch('app.crud.user.get_user_profile')
def test_get_user_profile(mock_profile, client):
    mock_user = type('User', (), {'id': 1, 'name': 'Test'})()
    mock_profile.return_value = mock_user

    resp = client.get("/api/users/1", headers={"Api-Key": "user1"})
    assert resp.status_code == 200
    assert resp.json()["result"]


@patch('app.crud.tweet.get_feed_for_user')
def test_get_feed(mock_feed, client):
    mock_feed.return_value = [{"id": 1, "content": "test"}]

    resp = client.get("/api/tweets", headers={"Api-Key": "user1"})
    assert resp.status_code == 200
    assert "tweets" in resp.json()


def test_upload_media_invalid_type(client, mock_upload_file):
    resp = client.post(
        "/api/medias",
        files={"file": ("test.txt", mock_upload_file, "text/plain")},
        headers={"Api-Key": "user1"}
    )
    assert resp.status_code == 400
