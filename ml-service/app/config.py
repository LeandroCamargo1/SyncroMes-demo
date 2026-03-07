"""
Synchro MES — ML Service — Configuração
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

ML_MODELS_DIR = Path(__file__).parent / "ml_models"


class Settings(BaseSettings):
    # ── Database (read-only do banco principal) ───────────────
    database_url: str = "sqlite+aiosqlite:///./synchro_mes.db"

    # ── App ───────────────────────────────────────────────────
    app_title: str = "Synchro MES — ML Service"
    app_version: str = "1.0.0"
    debug: bool = True

    # ── CORS ──────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:8000"

    # ── ML ────────────────────────────────────────────────────
    min_samples_for_training: int = 30
    prediction_horizon_days: int = 7

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
