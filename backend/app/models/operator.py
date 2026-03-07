"""
Model: Operator — Operadores de produção
"""
from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Operator(Base):
    __tablename__ = "operators"

    registration = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    shift = Column(String(20), nullable=True)
    sector = Column(String(100), default="injeção")
    role = Column(String(50), default="operador")
    skills = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    phone = Column(String(20), nullable=True)

    # ── Relationships ─────────────────────────────────────
    production_orders = relationship("ProductionOrder", back_populates="operator", lazy="noload")
    planning_entries = relationship("Planning", back_populates="operator", lazy="noload")
    production_entries = relationship("ProductionEntry", back_populates="operator", lazy="noload")
    active_downtimes = relationship("ActiveDowntime", back_populates="operator", lazy="noload")
    downtime_history = relationship("DowntimeHistory", back_populates="operator", lazy="noload")
    quality_measurements = relationship("QualityMeasurement", back_populates="operator", lazy="noload")
    rework_entries = relationship("ReworkEntry", back_populates="operator", lazy="noload")
    loss_entries = relationship("LossEntry", back_populates="operator", lazy="noload")
    setup_entries = relationship("SetupEntry", back_populates="operator", lazy="noload")
    pmp_entries = relationship("PmpEntry", back_populates="operator", lazy="noload")
    quality_lots = relationship("QualityLot", back_populates="operator", lazy="noload")
    operator_schedules = relationship("OperatorSchedule", back_populates="operator", lazy="noload")
    absenteeism_entries = relationship("AbsenteeismEntry", back_populates="operator", lazy="noload")

    def __repr__(self):
        return f"<Operator {self.registration} name={self.name}>"
