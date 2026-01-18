from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.user import User
from app.models.follow import Follow


async def get_user_by_api_key(api_key: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.api_key == api_key))
    return result.scalar_one_or_none()


async def get_user_profile(user_id: int, db: AsyncSession) -> User | None:
    stmt = (
        select(User)
        .options(
            joinedload(User.followers).joinedload(Follow.follower),
            joinedload(User.following).joinedload(Follow.followed),
        )
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_me_profile(user_id: int, db: AsyncSession) -> User | None:
    return await get_user_profile(user_id, db)
