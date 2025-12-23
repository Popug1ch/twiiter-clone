from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with AsyncSessionLocal() as session:
        yield session


# ВАЖНО: импортируем модели, чтобы SQLAlchemy видел классы при конфигурации мапперов
import app.models.user  # noqa
import app.models.tweet  # noqa
import app.models.media  # noqa
import app.models.tweet_media  # noqa
import app.models.like  # noqa
import app.models.follow  # noqa
