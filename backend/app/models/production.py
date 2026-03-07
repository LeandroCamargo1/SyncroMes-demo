"""
Models: ProductionOrder, Planning, ProductionEntry
"""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, JSON, Enum, ForeignKey, Index,
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import OrderStatus, OrderPriority, PlanningStatus


class ProductionOrder(Base):
    __tablename__ = "production_orders"
    __table_args__ = (
        Index("ix_po_product_status", "product_id", "status"),
    )

    order_number = Column(String(50), unique=True, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    quantity_planned = Column(Integer, nullable=False)
    quantity_produced = Column(Integer, default=0)
    quantity_good = Column(Integer, default=0)
    quantity_rejected = Column(Integer, default=0)
    status = Column(Enum(OrderStatus), default=OrderStatus.planned, nullable=False)
    priority = Column(Enum(OrderPriority), default=OrderPriority.normal, nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True, index=True)
    mold_id = Column(Integer, ForeignKey("molds.id"), nullable=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(Date, nullable=True)
    client = Column(String(200), nullable=True)
    notes = Column(String(500), nullable=True)
    metadata_extra = Column(JSON, default=dict)

    # ── Relationships ─────────────────────────────────────
    product = relationship("Product", back_populates="production_orders", lazy="joined")
    machine = relationship("Machine", back_populates="production_orders", lazy="joined")
    mold = relationship("Mold", back_populates="production_orders", lazy="joined")
    operator = relationship("Operator", back_populates="production_orders", lazy="joined")
    production_entries = relationship("ProductionEntry", back_populates="order", lazy="noload")
    planning_entries = relationship("Planning", back_populates="order", lazy="noload")

    @property
    def product_code(self) -> str | None:
        return self.product.code if self.product else None

    @property
    def machine_code(self) -> str | None:
        return self.machine.code if self.machine else None

    @property
    def mold_code(self) -> str | None:
        return self.mold.code if self.mold else None

    @property
    def operator_name(self) -> str | None:
        return self.operator.name if self.operator else None

    def __repr__(self):
        return f"<ProductionOrder {self.order_number} status={self.status}>"


class Planning(Base):
    __tablename__ = "planning"
    __table_args__ = (
        Index("ix_planning_machine_date", "machine_id", "date"),
    )

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    mold_id = Column(Integer, ForeignKey("molds.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True, index=True)
    quantity_planned = Column(Integer, nullable=False)
    cycle_time_seconds = Column(Float, nullable=True)
    cavities = Column(Integer, default=1)
    weight_grams = Column(Float, nullable=True)
    material = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    shift = Column(String(20), nullable=True)
    date = Column(Date, nullable=False, index=True)
    sequence = Column(Integer, default=1)
    status = Column(Enum(PlanningStatus), default=PlanningStatus.pendente, nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="planning_entries", lazy="joined")
    product = relationship("Product", back_populates="planning_entries", lazy="joined")
    mold = relationship("Mold", lazy="joined")
    order = relationship("ProductionOrder", back_populates="planning_entries", lazy="joined")
    operator = relationship("Operator", back_populates="planning_entries", lazy="joined")

    @property
    def machine_code(self) -> str | None:
        return self.machine.code if self.machine else None

    @property
    def product_code(self) -> str | None:
        return self.product.code if self.product else None

    @property
    def mold_code(self) -> str | None:
        return self.mold.code if self.mold else None

    @property
    def operator_name(self) -> str | None:
        return self.operator.name if self.operator else None

    def __repr__(self):
        return f"<Planning machine_id={self.machine_id} product_id={self.product_id}>"


class ProductionEntry(Base):
    __tablename__ = "production_entries"
    __table_args__ = (
        Index("ix_pe_machine_timestamp", "machine_id", "timestamp"),
    )

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    product_name = Column(String(200), nullable=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    shift = Column(String(20), nullable=True)
    quantity_good = Column(Integer, default=0)
    quantity_rejected = Column(Integer, default=0)
    weight_kg = Column(Float, nullable=True)
    cycle_time_actual = Column(Float, nullable=True)
    cycle_time_ideal = Column(Float, nullable=True)
    cavities = Column(Integer, default=1)
    material = Column(String(100), nullable=True)
    notes = Column(String(500), nullable=True)

    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="production_entries", lazy="joined")
    product = relationship("Product", back_populates="production_entries", lazy="joined")
    order = relationship("ProductionOrder", back_populates="production_entries", lazy="joined")
    operator = relationship("Operator", back_populates="production_entries", lazy="joined")

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
        return f"<ProductionEntry machine_id={self.machine_id} qty={self.quantity_good}>"
