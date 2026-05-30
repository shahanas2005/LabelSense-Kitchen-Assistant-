from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import AnalysisHistory, Profile, User
from app.schemas import ProfileRequest
from app.services.expiry import compute_expiry, detect_expiry, extract_label_metadata
from app.services.ingredients import extract_ingredients
from app.services import rules
from app.services.ocr import extract_text_from_image, save_uploaded_image
from app.services.tts import build_speech_text, create_silent_wav, generate_audio_file

settings = get_settings()

HIGH_RISK_KEYWORDS = {
    "sugar": "High Sugar Warning",
    "glucose": "High Sugar Warning",
    "fructose": "High Sugar Warning",
    "sodium benzoate": "Preservative Warning",
    "potassium sorbate": "Preservative Warning",
    "palm oil": "Processed Oil Warning",
    "artificial color": "Artificial Additive Warning",
    "artificial colour": "Artificial Additive Warning",
    "artificial flavor": "Artificial Additive Warning",
    "artificial flavour": "Artificial Additive Warning",
}

ALLERGY_KEYWORDS = {
    "nuts": "Allergy Warning: Nuts",
    "peanuts": "Allergy Warning: Nuts",
    "almonds": "Allergy Warning: Nuts",
    "milk": "Allergy Warning: Lactose",
    "lactose": "Allergy Warning: Lactose",
    "wheat": "Allergy Warning: Gluten",
    "gluten": "Allergy Warning: Gluten",
}


def ensure_user_profile(db: Session, request: ProfileRequest) -> Profile:
    user = None
    if request.user_id:
        user = db.query(User).filter(User.id == request.user_id).first()
    if not user and request.email:
        user = db.query(User).filter(User.email == request.email).first()
    if not user:
        user = User(email=request.email, display_name=request.display_name)
        db.add(user)
        db.flush()
    else:
        if request.display_name:
            user.display_name = request.display_name

    profile = user.profile
    if not profile:
        profile = Profile(user_id=user.id)
        db.add(profile)

    # Persist structured profile fields
    profile.age_group = request.age_group
    # Store lists as comma-separated strings for simplicity
    profile.conditions = ",".join(sorted({item.strip().lower() for item in request.conditions if item.strip()}))
    profile.allergies = ",".join(sorted({item.strip().lower() for item in request.allergies if item.strip()}))
    profile.diet = ",".join(sorted({item.strip().lower() for item in request.diet if item.strip()}))
    profile.language = request.language
    profile.notes = request.notes
    db.commit()
    db.refresh(user)
    return user.profile


def _collect_warnings(ingredients: list[str], raw_text: str, profile: Profile | None) -> list[dict]:
    """Analyze ingredients and user profile to produce structured prioritized warnings.

    Returns a list of dicts with keys: warning, severity, reason, ingredient, rule
    """
    signals = rules.analyze_ingredients(ingredients, raw_text)
    structured = rules.apply_user_profile(profile, signals)
    return structured


def analyze_image(db: Session, image: Image.Image, filename: str, user_id: int | None = None) -> dict:
    user_profile = None
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        user_profile = user.profile if user else None

    image_path = save_uploaded_image(image, settings.uploads_dir / filename)
    ocr_result = extract_text_from_image(image)
    raw_text = ocr_result.text
    ocr_confidence = ocr_result.confidence
    label_metadata = extract_label_metadata(raw_text, lines=ocr_result.lines, near_expiry_days=settings.max_near_expiry_days)
    expiry_result = label_metadata.expiry
    ingredients = extract_ingredients(raw_text)
    warnings = _collect_warnings(ingredients, raw_text, user_profile)
    speech_text = build_speech_text(
        expiry_result.status,
        ingredients,
        warnings,
        language=(user_profile.language if user_profile else settings.default_language),
        label_details=label_metadata.detected_fields or [],
    )

    audio_file = generate_audio_file(speech_text, settings.audio_dir / f"analysis_{Path(filename).stem}")
    if audio_file is None:
        audio_file = create_silent_wav(settings.audio_dir / f"analysis_{Path(filename).stem}.wav")

    confidence = round(min(0.99, max(0.2, 0.45 + 0.4 * ocr_confidence + (0.1 if ingredients else 0.0) + (0.05 if expiry_result.expiry_date else 0.0) + (0.05 if label_metadata.detected_fields else 0.0))), 2)
    if expiry_result.source == "not_detected":
        confidence = round(min(confidence, 0.35), 2)
    history = AnalysisHistory(
        user_id=user_id,
        image_path=image_path,
        raw_text=raw_text,
        expiry_status=expiry_result.status,
        expiry_date=expiry_result.expiry_date,
        ingredients_json=json.dumps(ingredients),
        warnings_json=json.dumps(warnings),
        confidence=confidence,
        speech_text=speech_text,
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    return {
        "analysis_id": history.id,
        "expiry_status": expiry_result.status,
        "expiry_date": expiry_result.expiry_date,
        "ingredients": ingredients,
        "warnings": warnings,
        "confidence": confidence,
        "expiry_source": expiry_result.source,
        "expiry_bbox": expiry_result.bbox,
        "expiry_message": expiry_result.message,
        "manufacturing_date": label_metadata.manufacturing_date.value if label_metadata.manufacturing_date else None,
        "manufacturing_source": label_metadata.manufacturing_date.source if label_metadata.manufacturing_date else None,
        "net_weight": label_metadata.net_weight.value if label_metadata.net_weight else None,
        "net_weight_source": label_metadata.net_weight.source if label_metadata.net_weight else None,
        "label_details": label_metadata.detected_fields or [],
        "speech_text": speech_text,
        "raw_text": raw_text,
        "audio_url": f"/api/audio/{Path(audio_file).name}" if audio_file else None,
    }
