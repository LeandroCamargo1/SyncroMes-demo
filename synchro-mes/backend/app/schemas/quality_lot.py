"""
Schemas: Quality Lots (Triagem/Quarentena)
"""
from pydantic import BaseModel, Field
from datetime import datetime


class QualityLotCreate(BaseModel):
    machine_code: str
    product_code: str
    order_number: str | None = None
    quantity: int = Field(gt=0)
    weight_kg: float | None = None
    reason: str
    operator_name: str | None = None
    shift: str | None = None
    notes: str | None = None


class QualityLotUpdate(BaseModel):
    status: str | None = None
    approved_qty: int | None = None
    rejected_qty: int | None = None
    inspector: str | None = None
    conclusion_notes: str | None = None
    returned_to_production: bool | None = None


class QualityLotRead(BaseModel):
    id: int
    lot_number: str
    machine_code: str
    product_code: str
    order_number: str | None = None
    quantity: int
    weight_kg: float | None = None
    reason: str
    status: str
    approved_qty: int
    rejected_qty: int
    returned_to_production: bool
    operator_name: str | None = None
    inspector: str | None = None
    shift: str | None = None
    notes: str | None = None
    conclusion_notes: str | None = None
    created_at: datetime | None = None
    concluded_at: datetime | None = None

    model_config = {"from_attributes": True}
