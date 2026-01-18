"""
Общие фикстуры для всех тестов.
"""
import asyncio
from typing import Generator
from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi import HTTPException, Request, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, api_key_header  # используем оригинальный api_key_header
from app.models.user import User
from app.routers import users, tweets, medias
from tests.test_app import test_app


@pytest.fixture
def mock_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.id = 1
    user.name = "Иван Иванов"
    user.api_key = "user1"
    user.followers = []
    user.following = []
    return user


@pytest.fixture
def mock_db_session() -> AsyncMock:
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.add_all = MagicMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def _ensure_routers_registered() -> None:
    """Подключаем роутеры к test_app один раз."""
    if getattr(test_app.state, "routers_registered", False):
        return
    test_app.include_router(users.router, prefix="/api", tags=["users"])
    test_app.include_router(tweets.router, prefix="/api", tags=["tweets"])
    test_app.include_router(medias.router, prefix="/api", tags=["medias"])
    test_app.state.routers_registered = True


@pytest.fixture
def client(mock_db_session: AsyncMock, mock_user: MagicMock) -> TestClient:
    _ensure_routers_registered()

    async def override_get_current_user(
        request: Request,
        api_key: str = Depends(api_key_header),  # точная сигнатура из security.py
        db: AsyncSession = Depends(get_db),
        mock_user=mock_user  # передаём мок-юзер
    ) -> User:
        if api_key == "user1":
            return mock_user
        raise HTTPException(status_code=401, detail="API key required")

    test_app.dependency_overrides[get_db] = lambda: mock_db_session
    test_app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    return {"Api-Key": "user1"}


@pytest.fixture
def invalid_auth_headers() -> dict:
    return {"Api-Key": "invalid_key"}


@pytest.fixture
def sample_tweet_data() -> dict:
    return {"tweet_data": "Тестовый твит"}


@pytest.fixture
def sample_tweet_with_media() -> dict:
    return {"tweet_data": "Твит с медиа", "tweet_media_ids": [1]}


@pytest.fixture
def sample_feed_data() -> list:
    return [
        {
            "id": 1,
            "content": "Первый твит",
            "attachments": [],
            "author": {"id": 1, "name": "Иван Иванов"},
            "likes": [],
        }
    ]
