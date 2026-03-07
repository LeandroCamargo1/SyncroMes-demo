"""
Schemas: ProductionOrder, Planning, ProductionEntry
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional


# ── Production Order ──────────────────────────────────────────
class ProductionOrderCreate(BaseModel):
    order_number: str
    product_code: str
    product_name: str
    quantity_planned: int = Field(gt=0)
    priority: str = "normal"
    machine_code: str | None = None
    mold_code: str | None = None
    due_date: date | None = None
    client: str | None = None
    notes: str | None = None


class ProductionOrderUpdate(BaseModel):
    quantity_produced: int | None = None
    quantity_good: int | None = None
    quantity_rejected: int | None = None
    status: str | None = None
    machine_code: str | None = None
    operator_name: str | None = None
    notes: str | None = None


class ProductionOrderRead(BaseModel):
    id: int
    order_number: str
    product_code: str
    product_name: str
    quantity_planned: int
    quantity_produced: int
    quantity_good: int
    quantity_rejected: int
    status: str
    priority: str
    machine_code: str | None = None
    mold_code: str | None = None
    operator_name: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    due_date: date | None = None
    client: str | None = None
    notes: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Planning ──────────────────────────────────────────────────
class PlanningCreate(BaseModel):
    machine_code: str
    product_code: str
    product_name: str
    quantity_planned: int = Field(gt=0)
    date: date
    shift: str | None = None
    mold_code: str | None = None
    cycle_time_seconds: float | None = None
    cavities: int = 1
    weight_grams: float | None = None
    material: str | None = None
    color: str | None = None
    operator_name: str | None = None
    sequence: int = 1


class PlanningRead(BaseModel):
    id: int
    machine_code: str
    product_code: str
    product_name: str
    quantity_planned: int
    date: date
    shift: str | None = None
    mold_code: str | None = None
    cycle_time_seconds: float | None = None
    cavities: int
    weight_grams: float | None = None
    material: str | None = None
    color: str | None = None
    sequence: int
    status: str
    operator_name: str | None = None

    model_config = {"from_attributes": True}


# ── Production Entry ──────────────────────────────────────────
class ProductionEntryCreate(BaseModel):
    machine_code: str
    product_code: str
    product_name: str | None = None
    order_number: str | None = None
    operator_name: str | None = None
    shift: str | None = None
    quantity_good: int = Field(ge=0)
    quantity_rejected: int = Field(ge=0, default=0)
    weight_kg: float | None = None
    cycle_time_actual: float | None = None
    notes: str | None = None


class ProductionEntryRead(BaseModel):
    id: int
    machine_code: str
    product_code: str
    product_name: str | None = None
    order_number: str | None = None
    operator_name: str | None = None
    shift: str | None = None
    quantity_good: int
    quantity_rejected: int
    weight_kg: float | None = None
    cycle_time_actual: float | None = None
    timestamp: datetime | None = None

    model_config = {"from_attributes": True}
