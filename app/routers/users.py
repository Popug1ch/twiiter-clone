from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.crud.user import get_user_profile, get_me_profile
from app.schemas.user import ProfileResponse, ProfileUser, User as UserSchema
from app.crud.follow import follow_user, unfollow_user
from app.models.user import User as UserModel

router = APIRouter()


def success(data: dict | None = None) -> dict:
    base = {"result": True}
    if data:
        base.update(data)
    return base


def build_profile_user(profile: UserModel) -> ProfileUser:
    return ProfileUser(
        id=profile.id,
        name=profile.name,
        followers=[
            UserSchema(id=f.follower.id, name=f.follower.name)
            for f in profile.followers
        ],
        following=[
            UserSchema(id=f.followed.id, name=f.followed.name)
            for f in profile.following
        ],
    )


@router.get("/users/me", response_model=ProfileResponse)
async def get_me(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_me_profile(current_user.id, db)
    user_schema = build_profile_user(profile)
    return ProfileResponse(result=True, user=user_schema)


@router.get("/users/{user_id}", response_model=ProfileResponse)
async def get_user_profile_route(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    profile = await get_user_profile(user_id, db)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    user_schema = build_profile_user(profile)
    return ProfileResponse(result=True, user=user_schema)


@router.post("/users/{user_id}/follow")
async def follow_user_endpoint(
    user_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user_id == current_user.id:
        error = {
            "result": False,
            "error_type": "validation_error",
            "error_message": "Cannot follow yourself",
        }
        raise HTTPException(status_code=400, detail=error)

    await follow_user(db, follower_id=current_user.id, following_id=user_id)
    return {"result": True}


@router.delete("/users/{user_id}/follow")
async def unfollow_user_endpoint(
    user_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await unfollow_user(db, follower_id=current_user.id, following_id=user_id)
    return {"result": True}
