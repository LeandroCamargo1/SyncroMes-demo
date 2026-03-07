"""
Schemas: Leadership (Escala & Absenteísmo)
"""
from pydantic import BaseModel
from datetime import date, datetime


class OperatorScheduleCreate(BaseModel):
    operator_registration: str
    operator_name: str
    date: date
    shift: str
    machine_code: str | None = None
    position: str = "operador"
    notes: str | None = None


class OperatorScheduleRead(BaseModel):
    id: int
    operator_registration: str
    operator_name: str
    date: date
    shift: str
    machine_code: str | None = None
    position: str
    notes: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AbsenteeismCreate(BaseModel):
    operator_registration: str
    operator_name: str
    date: date
    shift: str | None = None
    reason: str
    hours_absent: int = 8
    justified: bool = False
    notes: str | None = None


class AbsenteeismRead(BaseModel):
    id: int
    operator_registration: str
    operator_name: str
    date: date
    shift: str | None = None
    reason: str
    hours_absent: int
    justified: bool
    notes: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
