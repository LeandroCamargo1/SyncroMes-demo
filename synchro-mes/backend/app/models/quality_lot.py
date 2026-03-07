"""
Model: QualityLot — Lotes de triagem/quarentena
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class QualityLot(Base):
    __tablename__ = "quality_lots"

    id = Column(Integer, primary_key=True, index=True)
    lot_number = Column(String(50), unique=True, nullable=False, index=True)
    machine_code = Column(String(20), nullable=False, index=True)
    product_code = Column(String(50), nullable=False)
    order_number = Column(String(50), nullable=True)
    quantity = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=True)
    reason = Column(String(200), nullable=False)
    status = Column(String(30), default="quarentena")  # quarentena, em_triagem, concluida
    approved_qty = Column(Integer, default=0)
    rejected_qty = Column(Integer, default=0)
    returned_to_production = Column(Boolean, default=False)
    operator_name = Column(String(100), nullable=True)
    inspector = Column(String(100), nullable=True)
    shift = Column(String(20), nullable=True)
    notes = Column(String(500), nullable=True)
    conclusion_notes = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    concluded_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<QualityLot {self.lot_number} status={self.status}>"
