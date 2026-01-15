import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_tweet_lifecycle():
    """Тест полного цикла: create -> like -> feed."""
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine("sqlite+aiosqlite:///./integration.db")
    Session = sessionmaker(engine, class_=AsyncSession)

    async with Session() as db:
        from app.crud.tweet import create_tweet, like_tweet, get_feed_for_user
        from app.core.seed import create_test_users
        await create_test_users()

        # 1. Создаем твит
        tweet_id = await create_tweet(db, 1, "Integration test!")
        assert tweet_id > 0

        # 2. Лайкаем
        await like_tweet(db, 2, tweet_id)

        # 3. Проверяем в ленте
        feed = await get_feed_for_user(db, 1)
        assert len(feed) > 0
        assert any(t["id"] == tweet_id for t in feed)
