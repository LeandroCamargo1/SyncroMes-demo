"""
Model: OperatorSchedule & AbsenteeismEntry — Liderança
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class OperatorSchedule(Base):
    __tablename__ = "operator_schedules"

    id = Column(Integer, primary_key=True, index=True)
    operator_registration = Column(String(20), nullable=False, index=True)
    operator_name = Column(String(150), nullable=False)
    date = Column(Date, nullable=False, index=True)
    shift = Column(String(20), nullable=False)
    machine_code = Column(String(20), nullable=True)
    position = Column(String(50), default="operador")  # operador, lider, auxiliar
    notes = Column(String(300), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<OperatorSchedule {self.operator_name} shift={self.shift} date={self.date}>"


class AbsenteeismEntry(Base):
    __tablename__ = "absenteeism_entries"

    id = Column(Integer, primary_key=True, index=True)
    operator_registration = Column(String(20), nullable=False, index=True)
    operator_name = Column(String(150), nullable=False)
    date = Column(Date, nullable=False, index=True)
    shift = Column(String(20), nullable=True)
    reason = Column(String(50), nullable=False)  # falta, atestado, atraso, ferias, folga
    hours_absent = Column(Integer, default=8)
    justified = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AbsenteeismEntry {self.operator_name} reason={self.reason}>"
