"""
Schemas: Material, BOM, InventoryMovement
"""
from pydantic import BaseModel
from datetime import datetime


# ── Material ──────────────────────────────────────────────────

class MaterialCreate(BaseModel):
    code: str
    name: str
    type: str
    unit: str = "kg"
    density: float | None = None
    supplier: str | None = None
    min_stock: float = 0
    cost_per_unit: float | None = None


class MaterialRead(BaseModel):
    id: int
    code: str
    name: str
    type: str
    unit: str
    density: float | None = None
    supplier: str | None = None
    min_stock: float
    current_stock: float
    cost_per_unit: float | None = None
    is_active: bool
    below_min_stock: bool

    model_config = {"from_attributes": True}


class MaterialUpdate(BaseModel):
    name: str | None = None
    supplier: str | None = None
    min_stock: float | None = None
    cost_per_unit: float | None = None
    is_active: bool | None = None


# ── BOM ───────────────────────────────────────────────────────

class BomLineCreate(BaseModel):
    product_code: str
    material_code: str
    quantity_per_unit: float
    unit: str = "kg"
    is_primary: bool = False
    notes: str | None = None


class BomLineRead(BaseModel):
    id: int
    product_code: str | None = None
    material_code: str | None = None
    quantity_per_unit: float
    unit: str
    is_primary: bool
    notes: str | None = None

    model_config = {"from_attributes": True}


# ── Inventory Movement ───────────────────────────────────────

class InventoryMovementCreate(BaseModel):
    material_code: str
    movement_type: str
    quantity: float
    lot_number: str | None = None
    reference: str | None = None
    performed_by: str | None = None
    notes: str | None = None


class InventoryMovementRead(BaseModel):
    id: int
    material_code: str | None = None
    movement_type: str
    quantity: float
    lot_number: str | None = None
    reference: str | None = None
    performed_by: str | None = None
    notes: str | None = None
    timestamp: datetime | None = None

    model_config = {"from_attributes": True}
