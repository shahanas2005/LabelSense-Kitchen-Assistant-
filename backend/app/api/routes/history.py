from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import AnalysisHistory
from app.schemas import HistoryItem, HistoryResponse

router = APIRouter()


@router.get("/history", response_model=HistoryResponse)
def get_history(user_id: int | None = Query(default=None), limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    query = db.query(AnalysisHistory).order_by(AnalysisHistory.created_at.desc())
    if user_id is not None:
        query = query.filter(AnalysisHistory.user_id == user_id)
    rows = query.limit(limit).all()
    items = [
        HistoryItem(
            id=row.id,
            user_id=row.user_id,
            image_path=row.image_path,
            expiry_status=row.expiry_status,
            expiry_date=row.expiry_date,
            ingredients=json.loads(row.ingredients_json or "[]"),
            warnings=json.loads(row.warnings_json or "[]"),
            confidence=row.confidence,
            speech_text=row.speech_text,
            created_at=row.created_at,
        )
        for row in rows
    ]
    return HistoryResponse(items=items)
