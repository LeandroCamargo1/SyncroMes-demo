"""
Model: MoldMaintenance — Manutenções de moldes (Ferramentaria)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class MoldMaintenance(Base):
    __tablename__ = "mold_maintenances"

    id = Column(Integer, primary_key=True, index=True)
    mold_code = Column(String(50), nullable=False, index=True)
    maintenance_type = Column(String(50), nullable=False)  # preventiva, corretiva, limpeza
    description = Column(String(500), nullable=True)
    technician = Column(String(100), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_hours = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)
    parts_replaced = Column(String(500), nullable=True)
    status = Column(String(30), default="em_andamento")  # em_andamento, concluida
    notes = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<MoldMaintenance {self.mold_code} type={self.maintenance_type}>"
