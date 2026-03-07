"""
Schemas: ISA-95 Equipment Hierarchy — Site, Area, WorkCenter
"""
from pydantic import BaseModel


# ── Site ──────────────────────────────────────────────────────

class SiteCreate(BaseModel):
    code: str
    name: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    timezone: str = "America/Sao_Paulo"


class SiteRead(BaseModel):
    id: int
    code: str
    name: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    timezone: str
    is_active: bool

    model_config = {"from_attributes": True}


# ── Area ──────────────────────────────────────────────────────

class AreaCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    site_code: str


class AreaRead(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    site_code: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


# ── WorkCenter ────────────────────────────────────────────────

class WorkCenterCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    area_code: str
    capacity: int = 1


class WorkCenterRead(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    area_code: str | None = None
    site_code: str | None = None
    capacity: int
    is_active: bool

    model_config = {"from_attributes": True}
