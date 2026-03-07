"""
Model: Operator — Operadores de produção
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    registration = Column(String(20), unique=True, nullable=False, index=True)  # matrícula
    name = Column(String(150), nullable=False)
    shift = Column(String(20), nullable=True)         # A, B, C
    sector = Column(String(100), default="injeção")
    role = Column(String(50), default="operador")     # operador, lider, preparador
    skills = Column(JSON, default=list)               # ["INJ-01","INJ-02"]
    is_active = Column(Boolean, default=True)
    phone = Column(String(20), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Operator {self.registration} name={self.name}>"
