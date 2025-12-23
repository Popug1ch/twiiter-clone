from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.media import Media

async def create_media(db: AsyncSession, filename: str, filepath: str) -> int:
    media = Media(filename=filename, filepath=filepath)
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media.id

async def get_media_by_id(db: AsyncSession, media_id: int) -> Media | None:
    res = await db.execute(select(Media).where(Media.id == media_id))
    return res.scalar_one_or_none()
