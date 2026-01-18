from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.crud.media import create_media

router = APIRouter()

UPLOAD_DIR = "static/media"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/medias")
async def upload_media_endpoint(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type.startswith("image/"):
        error = {
            "result": False,
            "error_type": "validation_error",
            "error_message": "Only image files are allowed",
        }
        raise HTTPException(status_code=400, detail=error)

    contents = await file.read()
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(full_path, "wb") as buffer:
        buffer.write(contents)

    relative_path = f"/static/media/{unique_name}"
    media_id = await create_media(db, filename=unique_name, filepath=relative_path)

    return {"result": True, "media_id": media_id}
