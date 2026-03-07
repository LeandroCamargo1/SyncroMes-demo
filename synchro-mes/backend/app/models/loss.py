"""
Model: LossEntry — Registros de perdas de produção
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import LossCategory


class LossEntry(Base):
    __tablename__ = "loss_entries"
    __table_args__ = (
        Index("ix_loss_category_ts", "category", "timestamp"),
    )

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    shift = Column(String(20), nullable=True)
    quantity = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=True)
    reason = Column(String(200), nullable=False)
    category = Column(Enum(LossCategory), nullable=False)
    material = Column(String(100), nullable=True)
    is_manual = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)

    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="loss_entries", lazy="joined")
    product = relationship("Product", back_populates="loss_entries", lazy="joined")
    order = relationship("ProductionOrder", lazy="joined")
    operator = relationship("Operator", back_populates="loss_entries", lazy="joined")

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
        return f"<LossEntry machine_id={self.machine_id} qty={self.quantity} reason={self.reason}>"
