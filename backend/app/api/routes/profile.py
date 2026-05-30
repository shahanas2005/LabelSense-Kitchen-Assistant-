from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Profile, User
from app.schemas import ProfileRequest, ProfileResponse
from app.services.analyzer import ensure_user_profile

router = APIRouter()


@router.post("/profile", response_model=ProfileResponse)
def save_profile(request: ProfileRequest, db: Session = Depends(get_db)):
    profile = ensure_user_profile(db, request)
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        email=profile.user.email if profile.user else None,
        display_name=profile.user.display_name if profile.user else None,
        age_group=profile.age_group,
        conditions=[item for item in profile.conditions.split(",") if item],
        allergies=[item for item in profile.allergies.split(",") if item],
        diet=[item for item in profile.diet.split(",") if item],
        language=profile.language,
        notes=profile.notes,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
