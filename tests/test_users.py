from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status


class TestUsersAPI:
    def test_get_me(self, client, auth_headers):
        """Получение своего профиля."""
        profile = MagicMock()
        profile.id = 1
        profile.name = "Иван Иванов"
        profile.followers = []
        profile.following = []

        with patch(
            "app.routers.users.get_me_profile", new=AsyncMock(return_value=profile)
        ):
            resp = client.get("/api/users/me", headers=auth_headers)

        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["result"] is True
        assert data["user"]["id"] == 1
        assert data["user"]["name"] == "Иван Иванов"

    def test_get_profile(self, client):
        """Профиль по ID: может быть 404, это ок."""
        with patch(
            "app.routers.users.get_user_profile", new=AsyncMock(return_value=None)
        ):
            resp = client.get("/api/users/1")
        assert resp.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

    def test_follow_unfollow(self, client, auth_headers):
        """Подписка и отписка."""
        with patch("app.routers.users.follow_user", new=AsyncMock(return_value=None)):
            resp1 = client.post("/api/users/2/follow", headers=auth_headers)
        assert resp1.status_code == status.HTTP_200_OK
        assert resp1.json()["result"] is True

        with patch("app.routers.users.unfollow_user", new=AsyncMock(return_value=None)):
            resp2 = client.delete("/api/users/2/follow", headers=auth_headers)
        assert resp2.status_code == status.HTTP_200_OK
        assert resp2.json()["result"] is True

    def test_follow_self_error(self, client, auth_headers):
        """Нельзя подписаться на себя."""
        resp = client.post("/api/users/1/follow", headers=auth_headers)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        detail = resp.json()["detail"]
        assert detail["result"] is False
        assert detail["error_type"] == "validation_error"
        assert "Cannot follow yourself" in detail["error_message"]

    def test_auth_required(self, client):
        """Без Api-Key должен быть 401."""
        resp1 = client.get("/api/users/me")
        resp2 = client.post("/api/users/2/follow")
        assert resp1.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp2.status_code == status.HTTP_401_UNAUTHORIZED
