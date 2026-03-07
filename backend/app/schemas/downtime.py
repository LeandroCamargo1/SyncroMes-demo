"""
Schemas: Downtime
"""
from pydantic import BaseModel
from datetime import datetime


class ActiveDowntimeCreate(BaseModel):
    machine_code: str
    reason: str
    category: str
    subcategory: str | None = None
    operator_name: str | None = None
    shift: str | None = None
    is_planned: bool = False
    notes: str | None = None


class ActiveDowntimeRead(BaseModel):
    id: int
    machine_code: str
    reason: str
    category: str
    subcategory: str | None = None
    operator_name: str | None = None
    shift: str | None = None
    start_time: datetime
    is_planned: bool
    notes: str | None = None

    model_config = {"from_attributes": True}


class DowntimeHistoryRead(BaseModel):
    id: int
    machine_code: str
    reason: str
    category: str
    subcategory: str | None = None
    operator_name: str | None = None
    shift: str | None = None
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    is_planned: bool
    notes: str | None = None
    resolved_by: str | None = None

    model_config = {"from_attributes": True}
