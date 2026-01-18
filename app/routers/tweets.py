from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.tweet import TweetCreate, TweetsFeedResponse
from app.crud import tweet as tweet_crud

router = APIRouter()


def success(data: dict | None = None) -> dict:
    base = {"result": True}
    if data:
        base.update(data)
    return base


def error(error_type: str, error_message: str, status_code: int = 400):
    raise HTTPException(
        status_code=status_code,
        detail={"result": False, "error_type": error_type, "error_message": error_message},
    )


@router.post("/tweets")
async def create_tweet_endpoint(
    payload: TweetCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not payload.tweet_data.strip():
        error("validation_error", "tweet_data cannot be empty", 422)

    tweet_id = await tweet_crud.create_tweet(
        db,
        author_id=current_user.id,
        content=payload.tweet_data,
        media_ids=payload.tweet_media_ids or [],
    )
    return success({"tweet_id": tweet_id})


@router.delete("/tweets/{tweet_id}")
async def delete_tweet_endpoint(
    tweet_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await tweet_crud.delete_tweet(db, current_user.id, tweet_id)
    if not ok:
        error("not_found_or_forbidden", "Tweet not found or not owned", 404)
    return success({})


@router.post("/tweets/{tweet_id}/likes")
async def like_tweet_endpoint(
    tweet_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tweet_crud.like_tweet(db, current_user.id, tweet_id)
    return success({})


@router.delete("/tweets/{tweet_id}/likes")
async def unlike_tweet_endpoint(
    tweet_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tweet_crud.unlike_tweet(db, current_user.id, tweet_id)
    return success({})


@router.get("/tweets", response_model=TweetsFeedResponse)
async def get_feed_endpoint(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed = await tweet_crud.get_feed_for_user(db, current_user.id)
    return {"result": True, "tweets": feed}
