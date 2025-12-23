from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.follow import Follow


async def follow_user(db: AsyncSession, follower_id: int, following_id: int) -> None:
    if follower_id == following_id:
        return

    q = select(Follow).where(
        Follow.follower_id == follower_id,
        Follow.following_id == following_id,
    )
    res = await db.execute(q)
    if res.scalar_one_or_none():
        return

    db.add(Follow(follower_id=follower_id, following_id=following_id))
    await db.commit()


async def unfollow_user(db: AsyncSession, follower_id: int, following_id: int) -> None:
    q = delete(Follow).where(
        Follow.follower_id == follower_id,
        Follow.following_id == following_id,
    )
    await db.execute(q)
    await db.commit()
