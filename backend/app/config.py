"""
Synchro MES — Configuração central (pydantic-settings)
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./synchro_mes_v2.db"

    # ── JWT / Auth ────────────────────────────────────────────
    secret_key: str = os.environ.get(
        "SECRET_KEY", "CHANGE-ME-IN-PRODUCTION-" + "x" * 32
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # ── Dev mode ──────────────────────────────────────────────
    dev_bypass_auth: bool = True  # set False in production

    # ── CORS ──────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ── App info ──────────────────────────────────────────────
    app_title: str = "Synchro MES"
    app_version: str = "2.1.0"
    debug: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
