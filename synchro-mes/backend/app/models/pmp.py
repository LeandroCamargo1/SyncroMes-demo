"""
Model: PmpEntry — Registros de PMP (Moído/Borra/Sucata)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class PmpEntry(Base):
    __tablename__ = "pmp_entries"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(30), nullable=False, index=True)  # moido, borra, sucata
    machine_code = Column(String(20), nullable=True, index=True)
    product_code = Column(String(50), nullable=True)
    material = Column(String(100), nullable=True)
    weight_kg = Column(Float, nullable=False)
    operator_name = Column(String(100), nullable=True)
    shift = Column(String(20), nullable=True)
    destination = Column(String(100), nullable=True)  # reprocesso, descarte, venda
    notes = Column(String(500), nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<PmpEntry {self.type} weight={self.weight_kg}kg>"
