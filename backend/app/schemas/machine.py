"""
Schemas: Machine & Mold
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MachineRead(BaseModel):
    id: int
    code: str
    name: str
    type: str
    tonnage: float | None = None
    status: str
    current_product: str | None = None
    current_mold: str | None = None
    current_operator: str | None = None
    cycle_time_seconds: float | None = None
    cavities: int
    efficiency: float
    location: str
    work_center_code: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class MachineUpdate(BaseModel):
    status: str | None = None
    current_product: str | None = None
    current_mold: str | None = None
    current_operator: str | None = None
    cycle_time_seconds: float | None = None
    efficiency: float | None = None


class MoldRead(BaseModel):
    id: int
    code: str
    name: str
    cavities: int
    cycle_time_ideal: float | None = None
    product_code: str | None = None
    status: str
    total_cycles: int
    max_cycles: int | None = None
    weight_grams: float | None = None
    material_type: str | None = None

    model_config = {"from_attributes": True}
