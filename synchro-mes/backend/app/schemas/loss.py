"""
Schemas: Loss entries
"""
from pydantic import BaseModel, Field
from datetime import datetime


class LossEntryCreate(BaseModel):
    machine_code: str
    product_code: str
    order_number: str | None = None
    operator_name: str | None = None
    shift: str | None = None
    quantity: int = Field(gt=0)
    weight_kg: float | None = None
    reason: str
    category: str
    material: str | None = None
    is_manual: bool = False
    notes: str | None = None


class LossEntryRead(BaseModel):
    id: int
    machine_code: str
    product_code: str
    order_number: str | None = None
    operator_name: str | None = None
    shift: str | None = None
    quantity: int
    weight_kg: float | None = None
    reason: str
    category: str
    material: str | None = None
    is_manual: bool
    notes: str | None = None
    timestamp: datetime | None = None

    model_config = {"from_attributes": True}
