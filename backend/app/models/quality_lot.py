"""
Model: QualityLot — Lotes de triagem/quarentena
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import QualityLotStatus


class QualityLot(Base):
    __tablename__ = "quality_lots"

    lot_number = Column(String(50), unique=True, nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=True)
    reason = Column(String(200), nullable=False)
    status = Column(Enum(QualityLotStatus), default=QualityLotStatus.quarentena, nullable=False)
    approved_qty = Column(Integer, default=0)
    rejected_qty = Column(Integer, default=0)
    returned_to_production = Column(Boolean, default=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    inspector = Column(String(100), nullable=True)
    shift = Column(String(20), nullable=True)
    notes = Column(String(500), nullable=True)
    conclusion_notes = Column(String(500), nullable=True)
    concluded_at = Column(DateTime(timezone=True), nullable=True)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="quality_lots", lazy="joined")
    product = relationship("Product", back_populates="quality_lots", lazy="joined")
    order = relationship("ProductionOrder", lazy="joined")
    operator = relationship("Operator", back_populates="quality_lots", lazy="joined")

    @property
    def machine_code(self) -> str | None:
        return self.machine.code if self.machine else None

    @property
    def product_code(self) -> str | None:
        return self.product.code if self.product else None

    @property
    def order_number(self) -> str | None:
        return self.order.order_number if self.order else None

    @property
    def operator_name(self) -> str | None:
        return self.operator.name if self.operator else None

    def __repr__(self):
        return f"<QualityLot {self.lot_number} status={self.status}>"
