from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "LabelSense"
    api_v1_prefix: str = "/api"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    database_url: str = f"sqlite:///{(DATA_DIR / 'labelsense.db').as_posix()}"
    uploads_dir: Path = DATA_DIR / "uploads"
    audio_dir: Path = DATA_DIR / "audio"
    max_near_expiry_days: int = 30
    default_language: str = "en"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def ensure_paths(self) -> None:
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_paths()
    return settings
