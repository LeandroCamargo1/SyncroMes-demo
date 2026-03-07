"""
Models: QualityMeasurement, ReworkEntry, SpcData — Qualidade e SPC
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base


class QualityMeasurement(Base):
    __tablename__ = "quality_measurements"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(20), nullable=False, index=True)
    product_code = Column(String(50), nullable=False, index=True)
    order_number = Column(String(50), nullable=True)
    operator_name = Column(String(100), nullable=True)
    inspector = Column(String(100), nullable=True)
    dimension_name = Column(String(100), nullable=True)       # ex: "Diâmetro externo"
    nominal_value = Column(Float, nullable=True)
    measured_value = Column(Float, nullable=True)
    tolerance_upper = Column(Float, nullable=True)
    tolerance_lower = Column(Float, nullable=True)
    unit = Column(String(20), default="mm")
    is_approved = Column(Boolean, default=True)
    defect_type = Column(String(100), nullable=True)           # rebarba, bolha, mancha, dimensional
    defect_severity = Column(String(20), nullable=True)        # minor, major, critical
    sample_size = Column(Integer, default=1)
    notes = Column(String(500), nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<QualityMeasurement {self.product_code} approved={self.is_approved}>"


class ReworkEntry(Base):
    __tablename__ = "rework_entries"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(20), nullable=False, index=True)
    product_code = Column(String(50), nullable=False)
    order_number = Column(String(50), nullable=True)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=False)
    action_taken = Column(String(300), nullable=True)
    operator_name = Column(String(100), nullable=True)
    shift = Column(String(20), nullable=True)
    status = Column(String(30), default="pendente")  # pendente, em_andamento, concluido, descartado

    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ReworkEntry {self.product_code} qty={self.quantity}>"


class SpcData(Base):
    __tablename__ = "spc_data"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(20), nullable=False, index=True)
    product_code = Column(String(50), nullable=False)
    parameter_name = Column(String(100), nullable=False)   # peso, dimensao, temperatura
    value = Column(Float, nullable=False)
    ucl = Column(Float, nullable=True)    # upper control limit
    lcl = Column(Float, nullable=True)    # lower control limit
    target = Column(Float, nullable=True)
    is_out_of_control = Column(Boolean, default=False)
    subgroup = Column(Integer, nullable=True)
    sample_number = Column(Integer, nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<SpcData {self.parameter_name}={self.value}>"
