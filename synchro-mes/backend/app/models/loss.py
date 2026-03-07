"""
Model: LossEntry — Registros de perdas de produção
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class LossEntry(Base):
    __tablename__ = "loss_entries"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(20), nullable=False, index=True)
    product_code = Column(String(50), nullable=False)
    order_number = Column(String(50), nullable=True, index=True)
    operator_name = Column(String(100), nullable=True)
    shift = Column(String(20), nullable=True)
    quantity = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=True)
    reason = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # refugo, rebarba, dimensional, cor, contaminacao
    material = Column(String(100), nullable=True)
    is_manual = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<LossEntry {self.machine_code} qty={self.quantity} reason={self.reason}>"
