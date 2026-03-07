"""
Schemas: Quality
"""
from pydantic import BaseModel
from datetime import datetime


class QualityMeasurementCreate(BaseModel):
    machine_code: str
    product_code: str
    order_number: str | None = None
    operator_name: str | None = None
    inspector: str | None = None
    dimension_name: str | None = None
    nominal_value: float | None = None
    measured_value: float | None = None
    tolerance_upper: float | None = None
    tolerance_lower: float | None = None
    unit: str = "mm"
    is_approved: bool = True
    defect_type: str | None = None
    defect_severity: str | None = None
    sample_size: int = 1
    notes: str | None = None


class QualityMeasurementRead(BaseModel):
    id: int
    machine_code: str
    product_code: str
    order_number: str | None = None
    inspector: str | None = None
    dimension_name: str | None = None
    nominal_value: float | None = None
    measured_value: float | None = None
    tolerance_upper: float | None = None
    tolerance_lower: float | None = None
    unit: str
    is_approved: bool
    defect_type: str | None = None
    defect_severity: str | None = None
    timestamp: datetime | None = None

    model_config = {"from_attributes": True}
