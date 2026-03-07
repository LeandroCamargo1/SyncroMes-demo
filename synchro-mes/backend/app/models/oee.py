"""
Model: OeeHistory — Histórico de OEE por máquina/turno/dia
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base


class OeeHistory(Base):
    __tablename__ = "oee_history"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    shift = Column(String(20), nullable=True)

    # OEE Components (0.0 – 100.0)
    availability = Column(Float, nullable=False, default=0.0)
    performance = Column(Float, nullable=False, default=0.0)
    quality_rate = Column(Float, nullable=False, default=0.0)
    oee = Column(Float, nullable=False, default=0.0)

    # Dados brutos para cálculo
    planned_time_minutes = Column(Float, default=480.0)     # 8h turno
    running_time_minutes = Column(Float, default=0.0)
    downtime_minutes = Column(Float, default=0.0)
    total_produced = Column(Integer, default=0)
    good_produced = Column(Integer, default=0)
    rejected = Column(Integer, default=0)
    ideal_cycle_seconds = Column(Float, nullable=True)
    actual_cycle_seconds = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<OeeHistory {self.machine_code} {self.date} oee={self.oee}%>"
