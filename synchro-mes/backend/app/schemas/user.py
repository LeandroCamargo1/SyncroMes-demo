"""
Schemas: User & Auth
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# ── Auth / Token ──────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserRead"


class TokenData(BaseModel):
    email: str | None = None
    role: str | None = None


# ── User ──────────────────────────────────────────────────────
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=255)
    role: str = Field(default="operador", pattern="^(admin|supervisor|operador|qualidade|pcp)$")
    sector: str = "producao"


class UserCreate(UserBase):
    password: str = Field(min_length=4, max_length=128)


class UserUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    sector: str | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    id: int
    is_active: bool
    avatar_initials: str | None = None
    custom_claims: dict = {}
    created_at: datetime | None = None
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


# ── Login ─────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
