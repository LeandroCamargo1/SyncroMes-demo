"""
Schemas: OEE
"""
from pydantic import BaseModel
from datetime import date, datetime


class OeeHistoryRead(BaseModel):
    id: int
    machine_code: str
    date: date
    shift: str | None = None
    availability: float
    performance: float
    quality_rate: float
    oee: float
    planned_time_minutes: float
    running_time_minutes: float
    downtime_minutes: float
    total_produced: int
    good_produced: int
    rejected: int

    model_config = {"from_attributes": True}


class OeeSummary(BaseModel):
    """Resumo OEE para cards do dashboard."""
    machine_code: str
    oee: float
    availability: float
    performance: float
    quality_rate: float
    trend: str = "stable"  # up, down, stable
    period: str = "today"
