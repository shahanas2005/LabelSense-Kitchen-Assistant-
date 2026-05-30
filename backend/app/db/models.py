from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    history = relationship("AnalysisHistory", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    is_diabetic: Mapped[bool] = mapped_column(default=False)
    age_group: Mapped[str | None] = mapped_column(String(20), default=None)
    conditions: Mapped[str] = mapped_column(Text, default="")
    diet: Mapped[str] = mapped_column(Text, default="")
    allergies: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String(20), default="en")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    image_path: Mapped[str] = mapped_column(String(500))
    raw_text: Mapped[str] = mapped_column(Text, default="")
    expiry_status: Mapped[str] = mapped_column(String(32))
    expiry_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ingredients_json: Mapped[str] = mapped_column(Text, default="[]")
    warnings_json: Mapped[str] = mapped_column(Text, default="[]")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    speech_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="history")
