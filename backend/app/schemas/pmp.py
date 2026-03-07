"""
Schemas: PMP (Moído/Borra/Sucata)
"""
from pydantic import BaseModel, Field
from datetime import datetime


class PmpEntryCreate(BaseModel):
    type: str  # moido, borra, sucata
    machine_code: str | None = None
    product_code: str | None = None
    material: str | None = None
    weight_kg: float = Field(gt=0)
    operator_name: str | None = None
    shift: str | None = None
    destination: str | None = None
    notes: str | None = None


class PmpEntryRead(BaseModel):
    id: int
    type: str
    machine_code: str | None = None
    product_code: str | None = None
    material: str | None = None
    weight_kg: float
    operator_name: str | None = None
    shift: str | None = None
    destination: str | None = None
    notes: str | None = None
    timestamp: datetime | None = None

    model_config = {"from_attributes": True}
