"""
Models: QualityMeasurement, ReworkEntry, SpcData — Qualidade e SPC
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import DefectSeverity, ReworkStatus


class QualityMeasurement(Base):
    __tablename__ = "quality_measurements"
    __table_args__ = (
        Index("ix_qm_product_machine", "product_id", "machine_id"),
    )

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    inspector = Column(String(100), nullable=True)
    dimension_name = Column(String(100), nullable=True)
    nominal_value = Column(Float, nullable=True)
    measured_value = Column(Float, nullable=True)
    tolerance_upper = Column(Float, nullable=True)
    tolerance_lower = Column(Float, nullable=True)
    unit = Column(String(20), default="mm")
    is_approved = Column(Boolean, default=True)
    defect_type = Column(String(100), nullable=True)
    defect_severity = Column(Enum(DefectSeverity), nullable=True)
    sample_size = Column(Integer, default=1)
    notes = Column(String(500), nullable=True)

    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="quality_measurements", lazy="joined")
    product = relationship("Product", back_populates="quality_measurements", lazy="joined")
    order = relationship("ProductionOrder", lazy="joined")
    operator = relationship("Operator", back_populates="quality_measurements", lazy="joined")

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
        return f"<QualityMeasurement product_id={self.product_id} approved={self.is_approved}>"


class ReworkEntry(Base):
    __tablename__ = "rework_entries"

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=False)
    action_taken = Column(String(300), nullable=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    shift = Column(String(20), nullable=True)
    status = Column(Enum(ReworkStatus), default=ReworkStatus.pendente, nullable=False)

    timestamp = Column(DateTime(timezone=True), nullable=False)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="rework_entries", lazy="joined")
    product = relationship("Product", back_populates="rework_entries", lazy="joined")
    order = relationship("ProductionOrder", lazy="joined")
    operator = relationship("Operator", back_populates="rework_entries", lazy="joined")

    def __repr__(self):
        return f"<ReworkEntry product_id={self.product_id} qty={self.quantity}>"


class SpcData(Base):
    __tablename__ = "spc_data"

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    parameter_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    ucl = Column(Float, nullable=True)
    lcl = Column(Float, nullable=True)
    target = Column(Float, nullable=True)
    is_out_of_control = Column(Boolean, default=False)
    subgroup = Column(Integer, nullable=True)
    sample_number = Column(Integer, nullable=True)

    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="spc_data", lazy="joined")
    product = relationship("Product", back_populates="spc_data", lazy="joined")

    def __repr__(self):
        return f"<SpcData {self.parameter_name}={self.value}>"
