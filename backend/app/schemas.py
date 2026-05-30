from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProfileRequest(BaseModel):
    user_id: int | None = None
    email: EmailStr | None = None
    display_name: str | None = None
    # New structured profile fields
    age_group: Literal["elderly", "adult"] | None = None
    conditions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    diet: list[str] = Field(default_factory=list)
    language: Literal["en", "ur"] = "en"
    notes: str = ""


class ProfileResponse(ProfileRequest):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalyzeResponse(BaseModel):
    analysis_id: int
    expiry_status: str
    expiry_date: str | None
    ingredients: list[str]
    # Structured, prioritized warnings
    warnings: list[dict]
    confidence: float
    expiry_source: str | None = None
    expiry_bbox: list[list[float]] | None = None
    expiry_message: str | None = None
    manufacturing_date: str | None = None
    manufacturing_source: str | None = None
    net_weight: str | None = None
    net_weight_source: str | None = None
    label_details: list[dict] = Field(default_factory=list)
    speech_text: str
    raw_text: str
    audio_url: str | None = None


class HistoryItem(BaseModel):
    id: int
    user_id: int | None
    image_path: str
    expiry_status: str
    expiry_date: str | None
    ingredients: list[str]
    warnings: list[str]
    confidence: float
    speech_text: str
    created_at: datetime


class HistoryResponse(BaseModel):
    items: list[HistoryItem]


class ApiMessage(BaseModel):
    message: str
    data: dict[str, Any] | None = None
