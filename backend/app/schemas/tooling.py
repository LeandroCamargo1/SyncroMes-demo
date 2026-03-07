"""
Schemas: Tooling / Mold Maintenance
"""
from pydantic import BaseModel
from datetime import datetime


class MoldMaintenanceCreate(BaseModel):
    mold_code: str
    maintenance_type: str
    description: str | None = None
    technician: str | None = None
    start_time: datetime
    notes: str | None = None


class MoldMaintenanceFinish(BaseModel):
    end_time: datetime | None = None
    cost: float | None = None
    parts_replaced: str | None = None
    notes: str | None = None


class MoldMaintenanceRead(BaseModel):
    id: int
    mold_code: str
    maintenance_type: str
    description: str | None = None
    technician: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    duration_hours: float | None = None
    cost: float | None = None
    parts_replaced: str | None = None
    status: str
    notes: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class MoldUpdate(BaseModel):
    name: str | None = None
    cavities: int | None = None
    cycle_time_ideal: float | None = None
    product_code: str | None = None
    status: str | None = None
    total_cycles: int | None = None
    max_cycles: int | None = None
    weight_grams: float | None = None
    material_type: str | None = None
