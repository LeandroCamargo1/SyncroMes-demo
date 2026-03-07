"""
Schemas: ProcessSegment — Parâmetros de processo de injeção
"""
from pydantic import BaseModel


class ProcessSegmentCreate(BaseModel):
    product_code: str
    machine_type: str = "injetora"
    cycle_time_ideal: float | None = None
    injection_pressure: float | None = None
    holding_pressure: float | None = None
    melt_temperature: float | None = None
    mold_temperature: float | None = None
    cooling_time: float | None = None
    injection_speed: float | None = None
    screw_rpm: float | None = None
    back_pressure: float | None = None
    clamping_force: float | None = None
    notes: str | None = None


class ProcessSegmentRead(BaseModel):
    id: int
    product_code: str | None = None
    machine_type: str
    cycle_time_ideal: float | None = None
    injection_pressure: float | None = None
    holding_pressure: float | None = None
    melt_temperature: float | None = None
    mold_temperature: float | None = None
    cooling_time: float | None = None
    injection_speed: float | None = None
    screw_rpm: float | None = None
    back_pressure: float | None = None
    clamping_force: float | None = None
    notes: str | None = None

    model_config = {"from_attributes": True}
