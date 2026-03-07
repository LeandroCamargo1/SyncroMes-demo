"""
Model: MachineMaintenance — Manutenção de máquinas (complementa MoldMaintenance)
Preenche lacuna ISA-95: manutenção de equipamentos além de moldes.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import MaintenanceType, MaintenanceStatus, MaintenancePriority


class MachineMaintenance(Base):
    __tablename__ = "machine_maintenances"

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    priority = Column(Enum(MaintenancePriority), default=MaintenancePriority.media)
    description = Column(String(500), nullable=True)
    technician = Column(String(100), nullable=True)
    scheduled_date = Column(Date, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_hours = Column(Float, nullable=True)
    cost = Column(Float, default=0)
    parts_replaced = Column(String(500), nullable=True)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.pendente, nullable=False)
    notes = Column(String(500), nullable=True)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="machine_maintenances", lazy="joined")

    @property
    def machine_code(self) -> str | None:
        return self.machine.code if self.machine else None

    def __repr__(self):
        return f"<MachineMaintenance machine_id={self.machine_id} type={self.maintenance_type}>"
