from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.analysis import router as analysis_router
from app.api.routes.history import router as history_router
from app.api.routes.profile import router as profile_router
from app.core.config import get_settings
from app.db.database import Base, engine
from app.db import models  # noqa: F401

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix=settings.api_v1_prefix)
app.include_router(profile_router, prefix=settings.api_v1_prefix)
app.include_router(history_router, prefix=settings.api_v1_prefix)
app.mount("/static", StaticFiles(directory=settings.uploads_dir), name="static")


@app.get("/")
def root():
    return JSONResponse({"message": "LabelSense API is running"})


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})
