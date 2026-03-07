"""
Models: ActiveDowntime, DowntimeHistory — Paradas de máquina
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import DowntimeCategory


class ActiveDowntime(Base):
    __tablename__ = "active_downtimes"

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    reason = Column(String(200), nullable=False)
    category = Column(Enum(DowntimeCategory), nullable=False)
    subcategory = Column(String(100), nullable=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    shift = Column(String(20), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    notes = Column(String(500), nullable=True)
    is_planned = Column(Boolean, default=False)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="active_downtimes", lazy="joined")
    operator = relationship("Operator", back_populates="active_downtimes", lazy="joined")

    @property
    def machine_code(self) -> str | None:
        return self.machine.code if self.machine else None

    @property
    def operator_name(self) -> str | None:
        return self.operator.name if self.operator else None

    def __repr__(self):
        return f"<ActiveDowntime machine_id={self.machine_id} reason={self.reason}>"


class DowntimeHistory(Base):
    __tablename__ = "downtime_history"
    __table_args__ = (
        Index("ix_dth_machine_start", "machine_id", "start_time"),
        Index("ix_dth_category", "category"),
    )

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    reason = Column(String(200), nullable=False)
    category = Column(Enum(DowntimeCategory), nullable=False)
    subcategory = Column(String(100), nullable=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    shift = Column(String(20), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Float, nullable=False)
    is_planned = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)
    resolved_by = Column(String(100), nullable=True)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="downtime_history", lazy="joined")
    operator = relationship("Operator", back_populates="downtime_history", lazy="joined")

    @property
    def machine_code(self) -> str | None:
        return self.machine.code if self.machine else None

    @property
    def operator_name(self) -> str | None:
        return self.operator.name if self.operator else None

    def __repr__(self):
        return f"<DowntimeHistory machine_id={self.machine_id} dur={self.duration_minutes}min>"
