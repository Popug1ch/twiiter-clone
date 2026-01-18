from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status


class TestIntegration:
    def test_full_flow(self, client, auth_headers, sample_feed_data):
        """Полный сценарий: профиль → follow → твит → лайк → лента."""
        profile = MagicMock()
        profile.id = 1
        profile.name = "Иван Иванов"
        profile.followers = []
        profile.following = []

        with patch("app.routers.users.get_me_profile", new=AsyncMock(return_value=profile)), \
             patch("app.routers.users.follow_user", new=AsyncMock(return_value=None)), \
             patch("app.routers.tweets.tweet_crud.create_tweet", new=AsyncMock(return_value=123)), \
             patch("app.routers.tweets.tweet_crud.like_tweet", new=AsyncMock(return_value=None)), \
             patch("app.routers.tweets.tweet_crud.get_feed_for_user", new=AsyncMock(return_value=sample_feed_data)):

            assert client.get("/api/users/me", headers=auth_headers).status_code == status.HTTP_200_OK
            assert client.post("/api/users/2/follow", headers=auth_headers).status_code == status.HTTP_200_OK
            assert client.post("/api/tweets", headers=auth_headers, json={"tweet_data": "test"}).status_code == status.HTTP_200_OK
            assert client.post("/api/tweets/123/likes", headers=auth_headers).status_code == status.HTTP_200_OK

            feed_resp = client.get("/api/tweets", headers=auth_headers)
            assert feed_resp.status_code == status.HTTP_200_OK
            assert feed_resp.json()["result"] is True
            assert len(feed_resp.json()["tweets"]) > 0

    def test_media_tweet(self, client, auth_headers):
        """Медиа → твит с медиа."""
        with patch("app.routers.medias.create_media", new=AsyncMock(return_value=456)), \
             patch("app.routers.tweets.tweet_crud.create_tweet", new=AsyncMock(return_value=123)):

            files = {"file": ("test.jpg", b"fake", "image/jpeg")}
            media_resp = client.post("/api/medias", headers=auth_headers, files=files)
            assert media_resp.status_code == status.HTTP_200_OK
            assert media_resp.json()["media_id"] == 456

            tweet_resp = client.post(
                "/api/tweets",
                headers=auth_headers,
                json={"tweet_data": "с медиа", "tweet_media_ids": [456]},
            )
            assert tweet_resp.status_code == status.HTTP_200_OK
            assert tweet_resp.json()["tweet_id"] == 123

    def test_errors(self, client):
        """Базовые ошибки."""
        assert client.get("/api/nonexistent").status_code == status.HTTP_404_NOT_FOUND
        assert client.post("/health").status_code == status.HTTP_405_METHOD_NOT_ALLOWED
