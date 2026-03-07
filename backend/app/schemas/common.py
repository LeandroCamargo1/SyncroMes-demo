"""
Schemas: System Log (Histórico/Auditoria)
"""
from pydantic import BaseModel
from datetime import datetime


class SystemLogRead(BaseModel):
    id: int
    action: str
    user_email: str | None = None
    user_name: str | None = None
    details: dict = {}
    module: str | None = None
    timestamp: datetime | None = None

    model_config = {"from_attributes": True}


class ProductRead(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    weight_grams: float | None = None
    material: str | None = None
    color: str | None = None
    cycle_time_ideal: float | None = None
    cavities: int
    category: str | None = None
    client: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class OperatorRead(BaseModel):
    id: int
    registration: str
    name: str
    shift: str | None = None
    sector: str
    role: str
    skills: list = []
    is_active: bool
    phone: str | None = None

    model_config = {"from_attributes": True}
