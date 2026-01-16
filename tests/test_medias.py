import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status


class TestMediasAPI:
    def test_upload_image(self, client, auth_headers):
        """Успешная загрузка изображения."""
        with patch("app.routers.medias.create_media", new=AsyncMock(return_value=789)):
            files = {"file": ("test.jpg", b"fake-image", "image/jpeg")}
            resp = client.post("/api/medias", headers=auth_headers, files=files)

        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["result"] is True
        assert data["media_id"] == 789

    def test_non_image_error(self, client, auth_headers):
        """Ошибка при загрузке не-изображения."""
        files = {"file": ("test.txt", b"text", "text/plain")}
        resp = client.post("/api/medias", headers=auth_headers, files=files)

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        detail = resp.json()["detail"]
        assert detail["result"] is False
        assert detail["error_type"] == "validation_error"
        assert "Only image files are allowed" in detail["error_message"]

    @pytest.mark.parametrize("ctype", ["image/jpeg", "image/png", "image/gif"])
    def test_formats(self, client, auth_headers, ctype):
        """Разные форматы изображений."""
        with patch("app.routers.medias.create_media", new=AsyncMock(return_value=1)):
            files = {"file": ("test.img", b"fake", ctype)}
            resp = client.post("/api/medias", headers=auth_headers, files=files)

        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["result"] is True

    def test_no_file(self, client, auth_headers):
        """Нет файла в запросе."""
        resp = client.post("/api/medias", headers=auth_headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
