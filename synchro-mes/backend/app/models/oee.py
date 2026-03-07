"""
Model: OeeHistory — Histórico de OEE por máquina/turno/dia
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class OeeHistory(Base):
    __tablename__ = "oee_history"
    __table_args__ = (
        Index("ix_oee_machine_date_shift", "machine_id", "date", "shift", unique=True),
    )

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    shift = Column(String(20), nullable=True)

    # OEE Components (0.0 – 100.0)
    availability = Column(Float, nullable=False, default=0.0)
    performance = Column(Float, nullable=False, default=0.0)
    quality_rate = Column(Float, nullable=False, default=0.0)
    oee = Column(Float, nullable=False, default=0.0)

    # Dados brutos para cálculo
    planned_time_minutes = Column(Float, default=480.0)
    running_time_minutes = Column(Float, default=0.0)
    downtime_minutes = Column(Float, default=0.0)
    total_produced = Column(Integer, default=0)
    good_produced = Column(Integer, default=0)
    rejected = Column(Integer, default=0)
    ideal_cycle_seconds = Column(Float, nullable=True)
    actual_cycle_seconds = Column(Float, nullable=True)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="oee_history", lazy="joined")

    @property
    def machine_code(self) -> str | None:
        return self.machine.code if self.machine else None

    def __repr__(self):
        return f"<OeeHistory machine_id={self.machine_id} {self.date} oee={self.oee}%>"
