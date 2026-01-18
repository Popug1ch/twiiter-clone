from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from typing import List
from fastapi import HTTPException

from app.models.tweet import Tweet
from app.models.tweet_media import TweetMedia
from app.models.like import Like
from app.models.media import Media
from app.models.user import User
from app.models.follow import Follow


async def create_tweet(
    db: AsyncSession,
    author_id: int,
    content: str,
    media_ids: List[int] | None = None,
) -> int:
    """Создает твит с проверкой медиа."""
    tweet = Tweet(content=content, author_id=author_id)
    db.add(tweet)
    await db.flush()  # Получаем tweet.id

    # Проверяем существование медиа
    if media_ids:
        existing_media = await db.execute(
            select(Media.id).where(Media.id.in_(media_ids))
        )
        existing_ids = {row[0] for row in existing_media.fetchall()}
        invalid_ids = set(media_ids) - existing_ids

        if invalid_ids:
            await db.rollback()
            raise HTTPException(
                status_code=400, detail=f"Media not found: {list(invalid_ids)}"
            )

        # Создаем связи TweetMedia
        for media_id in media_ids:
            tweet_media = TweetMedia(tweet_id=tweet.id, media_id=media_id)
            db.add(tweet_media)

    await db.commit()
    await db.refresh(tweet)
    return tweet.id


async def delete_tweet(db: AsyncSession, author_id: int, tweet_id: int) -> bool:
    """Удаляет твит автора."""
    stmt = delete(Tweet).where(Tweet.id == tweet_id, Tweet.author_id == author_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def like_tweet(db: AsyncSession, user_id: int, tweet_id: int) -> None:
    """Лайкает твит (если еще не лайкан)."""
    # Проверяем существующий лайк
    stmt = select(Like).where(Like.user_id == user_id, Like.tweet_id == tweet_id)
    result = await db.execute(stmt)

    if result.scalar_one_or_none():
        return  # Уже лайкнуто

    # Создаем новый лайк
    like = Like(user_id=user_id, tweet_id=tweet_id)
    db.add(like)
    await db.commit()


async def unlike_tweet(db: AsyncSession, user_id: int, tweet_id: int) -> None:
    """Убирает лайк с твита."""
    stmt = delete(Like).where(Like.user_id == user_id, Like.tweet_id == tweet_id)
    await db.execute(stmt)
    await db.commit()


async def get_feed_for_user(db: AsyncSession, user_id: int) -> List[dict]:
    """
    Возвращает ленту: свои твиты + твиты подписок,
    отсортированную по популярности.
    """
    # Получаем ID подписок + себя
    following_stmt = select(Follow.followed_id).where(Follow.follower_id == user_id)
    following_result = await db.execute(following_stmt)
    following_ids = [row[0] for row in following_result.fetchall()]

    # ← КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: добавляем свои твиты
    author_ids = [user_id] + following_ids

    if not author_ids:
        return []

    # Загружаем твиты с связями
    tweets_stmt = (
        select(Tweet)
        .where(Tweet.author_id.in_(author_ids))  # ← ИЗМЕНЕНО
        .options(
            joinedload(Tweet.author),
            joinedload(Tweet.tweet_medias).joinedload(TweetMedia.media),
            joinedload(Tweet.likes).joinedload(Like.user),
        )
        .order_by(Tweet.created_at.desc())
    )

    result = await db.execute(tweets_stmt)
    tweets = result.scalars().unique().all()

    # Сортируем по популярности (лайкам)
    tweets_sorted = sorted(tweets, key=lambda t: len(t.likes), reverse=True)

    # Формируем ответ
    feed = []
    for tweet in tweets_sorted:
        attachments = [tm.media.filepath for tm in tweet.tweet_medias]
        likes = [
            {"user_id": like.user.id, "name": like.user.name} for like in tweet.likes
        ]

        feed.append(
            {
                "id": tweet.id,
                "content": tweet.content,
                "attachments": attachments,
                "author": {"id": tweet.author.id, "name": tweet.author.name},
                "likes": likes,
            }
        )

    return feed
