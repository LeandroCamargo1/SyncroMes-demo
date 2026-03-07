"""
Models: ProductionOrder, Planning, ProductionEntry
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)  # OP-2025-001
    product_code = Column(String(50), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    quantity_planned = Column(Integer, nullable=False)
    quantity_produced = Column(Integer, default=0)
    quantity_good = Column(Integer, default=0)
    quantity_rejected = Column(Integer, default=0)
    status = Column(String(30), default="planned")  # planned, in_progress, completed, cancelled
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    machine_code = Column(String(20), nullable=True)
    mold_code = Column(String(50), nullable=True)
    operator_name = Column(String(100), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(Date, nullable=True)
    client = Column(String(200), nullable=True)
    notes = Column(String(500), nullable=True)
    metadata_extra = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ProductionOrder {self.order_number} status={self.status}>"


class Planning(Base):
    __tablename__ = "planning"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(20), nullable=False, index=True)
    product_code = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=False)
    mold_code = Column(String(50), nullable=True)
    order_number = Column(String(50), nullable=True)
    quantity_planned = Column(Integer, nullable=False)
    cycle_time_seconds = Column(Float, nullable=True)
    cavities = Column(Integer, default=1)
    weight_grams = Column(Float, nullable=True)
    material = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    shift = Column(String(20), nullable=True)     # A, B, C
    date = Column(Date, nullable=False, index=True)
    sequence = Column(Integer, default=1)           # ordem na fila da máquina
    status = Column(String(30), default="pendente")  # pendente, em_andamento, concluido
    operator_name = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Planning {self.machine_code} product={self.product_code}>"


class ProductionEntry(Base):
    __tablename__ = "production_entries"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(20), nullable=False, index=True)
    product_code = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=True)
    order_number = Column(String(50), nullable=True, index=True)
    operator_name = Column(String(100), nullable=True)
    shift = Column(String(20), nullable=True)
    quantity_good = Column(Integer, default=0)
    quantity_rejected = Column(Integer, default=0)
    weight_kg = Column(Float, nullable=True)
    cycle_time_actual = Column(Float, nullable=True)
    cycle_time_ideal = Column(Float, nullable=True)
    cavities = Column(Integer, default=1)
    material = Column(String(100), nullable=True)
    notes = Column(String(500), nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ProductionEntry {self.machine_code} qty={self.quantity_good}>"
