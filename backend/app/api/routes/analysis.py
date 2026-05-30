from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import get_db
from app.schemas import AnalyzeResponse
from app.services.analyzer import analyze_image

router = APIRouter()
settings = get_settings()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    image: UploadFile = File(...),
    user_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    try:
        pil_image = Image.open(image.file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid image file") from exc

    filename = f"{uuid.uuid4().hex}_{Path(image.filename or 'upload').name}"
    result = analyze_image(db, pil_image, filename=filename, user_id=user_id)
    return result


@router.get("/audio/{filename}")
def get_audio(filename: str):
    audio_path = settings.audio_dir / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(audio_path, media_type="audio/wav", filename=filename)
