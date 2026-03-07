"""
Models: Machine & Mold — Máquinas injetoras e moldes
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)   # INJ-01..INJ-10
    name = Column(String(100), nullable=False)
    type = Column(String(50), default="injetora")
    tonnage = Column(Float, nullable=True)           # tonelagem da injetora
    status = Column(String(30), default="stopped")   # running, stopped, maintenance, setup
    current_product = Column(String(100), nullable=True)
    current_mold = Column(String(100), nullable=True)
    current_operator = Column(String(100), nullable=True)
    cycle_time_seconds = Column(Float, nullable=True)
    cavities = Column(Integer, default=1)
    efficiency = Column(Float, default=0.0)          # % eficiência atual
    location = Column(String(100), default="Galpão Principal")
    metadata_extra = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Machine {self.code} status={self.status}>"


class Mold(Base):
    __tablename__ = "molds"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    cavities = Column(Integer, default=1)
    cycle_time_ideal = Column(Float, nullable=True)  # segundos
    product_code = Column(String(50), nullable=True)
    status = Column(String(30), default="disponivel")  # disponivel, em_uso, manutencao
    total_cycles = Column(Integer, default=0)
    max_cycles = Column(Integer, nullable=True)
    last_maintenance = Column(DateTime(timezone=True), nullable=True)
    weight_grams = Column(Float, nullable=True)
    material_type = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Mold {self.code} cavities={self.cavities}>"
