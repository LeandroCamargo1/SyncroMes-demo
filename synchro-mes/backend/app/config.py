"""
Synchro MES — Configuração central (pydantic-settings)
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./synchro_mes.db"

    # ── JWT / Auth ────────────────────────────────────────────
    secret_key: str = "synchro-mes-demo-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # ── CORS ──────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ── App info ──────────────────────────────────────────────
    app_title: str = "Synchro MES"
    app_version: str = "2.0.0"
    debug: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
