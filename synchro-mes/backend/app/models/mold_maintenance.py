"""
Model: MoldMaintenance — Manutenções de moldes (Ferramentaria)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import MaintenanceType, MaintenanceStatus


class MoldMaintenance(Base):
    __tablename__ = "mold_maintenances"

    mold_id = Column(Integer, ForeignKey("molds.id"), nullable=False, index=True)
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    description = Column(String(500), nullable=True)
    technician = Column(String(100), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_hours = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)
    parts_replaced = Column(String(500), nullable=True)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.em_andamento, nullable=False)
    notes = Column(String(500), nullable=True)

    # ── Relationships ─────────────────────────────────────
    mold = relationship("Mold", back_populates="maintenances", lazy="joined")

    @property
    def mold_code(self) -> str | None:
        return self.mold.code if self.mold else None

    def __repr__(self):
        return f"<MoldMaintenance mold_id={self.mold_id} type={self.maintenance_type}>"
