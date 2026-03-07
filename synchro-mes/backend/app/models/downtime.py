"""
Models: ActiveDowntime, DowntimeHistory — Paradas de máquina
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class ActiveDowntime(Base):
    __tablename__ = "active_downtimes"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(20), nullable=False, index=True)
    reason = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # mecanica, eletrica, setup, processo, qualidade, falta_material, programada
    subcategory = Column(String(100), nullable=True)
    operator_name = Column(String(100), nullable=True)
    shift = Column(String(20), nullable=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String(500), nullable=True)
    is_planned = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ActiveDowntime {self.machine_code} reason={self.reason}>"


class DowntimeHistory(Base):
    __tablename__ = "downtime_history"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(20), nullable=False, index=True)
    reason = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(100), nullable=True)
    operator_name = Column(String(100), nullable=True)
    shift = Column(String(20), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Float, nullable=False)
    is_planned = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)
    resolved_by = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<DowntimeHistory {self.machine_code} dur={self.duration_minutes}min>"
