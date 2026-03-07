"""
Model: SetupEntry — Registros de setup de máquinas
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SetupEntry(Base):
    __tablename__ = "setup_entries"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(20), nullable=False, index=True)
    setup_type = Column(String(50), nullable=False)  # troca_molde, troca_cor, troca_material, ajuste
    mold_from = Column(String(50), nullable=True)
    mold_to = Column(String(50), nullable=True)
    product_from = Column(String(50), nullable=True)
    product_to = Column(String(50), nullable=True)
    operator_name = Column(String(100), nullable=True)
    shift = Column(String(20), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Float, nullable=True)
    status = Column(String(30), default="em_andamento")  # em_andamento, concluido
    notes = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SetupEntry {self.machine_code} type={self.setup_type}>"
