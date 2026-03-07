"""
Model: PmpEntry — Registros de PMP (Moído/Borra/Sucata)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import PmpType, PmpDestination


class PmpEntry(Base):
    __tablename__ = "pmp_entries"

    type = Column(Enum(PmpType), nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    material = Column(String(100), nullable=True)
    weight_kg = Column(Float, nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    shift = Column(String(20), nullable=True)
    destination = Column(Enum(PmpDestination), nullable=True)
    notes = Column(String(500), nullable=True)

    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="pmp_entries", lazy="joined")
    product = relationship("Product", back_populates="pmp_entries", lazy="joined")
    operator = relationship("Operator", back_populates="pmp_entries", lazy="joined")

    @property
    def machine_code(self) -> str | None:
        return self.machine.code if self.machine else None

    @property
    def product_code(self) -> str | None:
        return self.product.code if self.product else None

    @property
    def operator_name(self) -> str | None:
        return self.operator.name if self.operator else None

    def __repr__(self):
        return f"<PmpEntry {self.type} weight={self.weight_kg}kg>"
