from fastapi import HTTPException, Security, Depends, Request
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.user import get_user_by_api_key
from app.models.user import User

api_key_header = APIKeyHeader(name="Api-Key", auto_error=False)


async def get_current_user(
    request: Request,
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> User:
    # пробуем оба варианта заголовка
    if not api_key:
        api_key = request.headers.get("api-key") or request.headers.get("Api-Key")

    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    user = await get_user_by_api_key(api_key, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user
