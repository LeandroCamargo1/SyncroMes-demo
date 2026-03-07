"""
Schemas: MachineMaintenance — Manutenção de máquinas
"""
from pydantic import BaseModel
from datetime import datetime, date


class MachineMaintenanceCreate(BaseModel):
    machine_code: str
    maintenance_type: str
    priority: str = "media"
    description: str | None = None
    technician: str | None = None
    scheduled_date: date | None = None
    notes: str | None = None


class MachineMaintenanceFinish(BaseModel):
    end_time: datetime
    cost: float | None = None
    parts_replaced: str | None = None
    notes: str | None = None


class MachineMaintenanceRead(BaseModel):
    id: int
    machine_code: str | None = None
    maintenance_type: str
    priority: str
    description: str | None = None
    technician: str | None = None
    scheduled_date: date | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration_hours: float | None = None
    cost: float
    parts_replaced: str | None = None
    status: str
    notes: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
