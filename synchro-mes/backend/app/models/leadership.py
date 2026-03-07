"""
Model: OperatorSchedule & AbsenteeismEntry — Liderança
"""
from sqlalchemy import Column, Integer, String, Date, Boolean, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import AbsenteeismReason


class OperatorSchedule(Base):
    __tablename__ = "operator_schedules"
    __table_args__ = (
        Index("ix_opsch_operator_date", "operator_id", "date"),
    )

    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False, index=True)
    operator_name = Column(String(150), nullable=False)
    date = Column(Date, nullable=False, index=True)
    shift = Column(String(20), nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)
    position = Column(String(50), default="operador")
    notes = Column(String(300), nullable=True)

    # ── Relationships ─────────────────────────────────────
    operator = relationship("Operator", back_populates="operator_schedules", lazy="joined")
    machine = relationship("Machine", back_populates="operator_schedules", lazy="joined")

    @property
    def operator_registration(self) -> str | None:
        return self.operator.registration if self.operator else None

    @property
    def machine_code(self) -> str | None:
        return self.machine.code if self.machine else None

    def __repr__(self):
        return f"<OperatorSchedule {self.operator_name} shift={self.shift} date={self.date}>"


class AbsenteeismEntry(Base):
    __tablename__ = "absenteeism_entries"
    __table_args__ = (
        Index("ix_abs_operator_date", "operator_id", "date"),
    )

    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False, index=True)
    operator_name = Column(String(150), nullable=False)
    date = Column(Date, nullable=False, index=True)
    shift = Column(String(20), nullable=True)
    reason = Column(Enum(AbsenteeismReason), nullable=False)
    hours_absent = Column(Integer, default=8)
    justified = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)

    # ── Relationships ─────────────────────────────────────
    operator = relationship("Operator", back_populates="absenteeism_entries", lazy="joined")

    @property
    def operator_registration(self) -> str | None:
        return self.operator.registration if self.operator else None

    def __repr__(self):
        return f"<AbsenteeismEntry {self.operator_name} reason={self.reason}>"
