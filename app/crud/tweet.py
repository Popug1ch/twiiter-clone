from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from typing import List

from app.models.tweet import Tweet
from app.models.tweet_media import TweetMedia
from app.models.like import Like
from app.models.user import User
from app.models.follow import Follow

async def create_tweet(
    db: AsyncSession,
    author_id: int,
    content: str,
    media_ids: List[int] | None,
) -> int:
    tweet = Tweet(content=content, author_id=author_id)
    db.add(tweet)
    await db.flush()
    if media_ids:
        for mid in media_ids:
            db.add(TweetMedia(tweet_id=tweet.id, media_id=mid))
    await db.commit()
    await db.refresh(tweet)
    return tweet.id

async def delete_tweet(db: AsyncSession, author_id: int, tweet_id: int) -> bool:
    q = delete(Tweet).where(Tweet.id == tweet_id, Tweet.author_id == author_id)
    res = await db.execute(q)
    await db.commit()
    return res.rowcount > 0

async def like_tweet(db: AsyncSession, user_id: int, tweet_id: int) -> None:
    stmt = select(Like).where(Like.user_id == user_id, Like.tweet_id == tweet_id)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        return
    like = Like(user_id=user_id, tweet_id=tweet_id)
    db.add(like)
    await db.commit()

async def unlike_tweet(db: AsyncSession, user_id: int, tweet_id: int) -> None:
    stmt = delete(Like).where(Like.user_id == user_id, Like.tweet_id == tweet_id)
    await db.execute(stmt)
    await db.commit()

async def get_feed_for_user(db: AsyncSession, user_id: int):
    following_ids_q = select(Follow.followed_id).where(Follow.follower_id == user_id)
    following_ids_res = await db.execute(following_ids_q)
    following_ids = [row[0] for row in following_ids_res.fetchall()]
    if not following_ids:
        return []
    tweets_q = (
        select(Tweet)
        .where(Tweet.author_id.in_(following_ids))
        .options(
            joinedload(Tweet.author),
            joinedload(Tweet.tweet_medias).joinedload(TweetMedia.media),
            joinedload(Tweet.likes).joinedload(Like.user),
        )
    )
    tweets_res = await db.execute(tweets_q)
    tweets = tweets_res.scalars().unique().all()
    tweets_sorted = sorted(tweets, key=lambda t: len(t.likes), reverse=True)
    feed = []
    for t in tweets_sorted:
        attachments = [tm.media.filepath for tm in t.tweet_medias]
        likes = [{"user_id": lk.user.id, "name": lk.user.name} for lk in t.likes]
        feed.append(
            {
                "id": t.id,
                "content": t.content,
                "attachments": attachments,
                "author": {"id": t.author.id, "name": t.author.name},
                "likes": likes,
            }
        )
    return feed
