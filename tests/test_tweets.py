from unittest.mock import AsyncMock, patch

from fastapi import status


class TestTweetsAPI:
    def test_create_tweet(self, client, auth_headers, sample_tweet_data):
        """Создание твита."""
        with patch(
            "app.routers.tweets.tweet_crud.create_tweet",
            new=AsyncMock(return_value=123),
        ):
            resp = client.post(
                "/api/tweets", headers=auth_headers, json=sample_tweet_data
            )

        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["result"] is True
        assert data["tweet_id"] == 123

    def test_empty_tweet_error(self, client, auth_headers):
        """Пустой контент не допускается."""
        resp = client.post("/api/tweets", headers=auth_headers, json={"tweet_data": ""})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        detail = resp.json()["detail"]
        assert detail["result"] is False
        assert detail["error_type"] == "validation_error"

    def test_delete_tweet(self, client, auth_headers):
        """Успешное удаление твита."""
        with patch(
            "app.routers.tweets.tweet_crud.delete_tweet",
            new=AsyncMock(return_value=True),
        ):
            resp = client.delete("/api/tweets/123", headers=auth_headers)

        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["result"] is True

    def test_delete_not_found(self, client, auth_headers):
        """Удаление несуществующего твита."""
        with patch(
            "app.routers.tweets.tweet_crud.delete_tweet",
            new=AsyncMock(return_value=False),
        ):
            resp = client.delete("/api/tweets/999", headers=auth_headers)

        assert resp.status_code == status.HTTP_404_NOT_FOUND
        detail = resp.json()["detail"]
        assert detail["result"] is False
        assert detail["error_type"] == "not_found_or_forbidden"

    def test_like_unlike(self, client, auth_headers):
        """Лайк / снятие лайка."""
        with patch(
            "app.routers.tweets.tweet_crud.like_tweet", new=AsyncMock(return_value=None)
        ):
            resp1 = client.post("/api/tweets/123/likes", headers=auth_headers)
        assert resp1.status_code == status.HTTP_200_OK
        assert resp1.json()["result"] is True

        with patch(
            "app.routers.tweets.tweet_crud.unlike_tweet",
            new=AsyncMock(return_value=None),
        ):
            resp2 = client.delete("/api/tweets/123/likes", headers=auth_headers)
        assert resp2.status_code == status.HTTP_200_OK
        assert resp2.json()["result"] is True

    def test_feed(self, client, auth_headers, sample_feed_data):
        """Лента твитов."""
        with patch(
            "app.routers.tweets.tweet_crud.get_feed_for_user",
            new=AsyncMock(return_value=sample_feed_data),
        ):
            resp = client.get("/api/tweets", headers=auth_headers)

        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["result"] is True
        assert len(data["tweets"]) == len(sample_feed_data)
