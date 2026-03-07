"""
Schemas: Setup entries
"""
from pydantic import BaseModel
from datetime import datetime


class SetupEntryCreate(BaseModel):
    machine_code: str
    setup_type: str
    mold_from: str | None = None
    mold_to: str | None = None
    product_from: str | None = None
    product_to: str | None = None
    operator_name: str | None = None
    shift: str | None = None
    start_time: datetime
    notes: str | None = None


class SetupEntryFinish(BaseModel):
    end_time: datetime | None = None
    notes: str | None = None


class SetupEntryRead(BaseModel):
    id: int
    machine_code: str
    setup_type: str
    mold_from: str | None = None
    mold_to: str | None = None
    product_from: str | None = None
    product_to: str | None = None
    operator_name: str | None = None
    shift: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    duration_minutes: float | None = None
    status: str
    notes: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
