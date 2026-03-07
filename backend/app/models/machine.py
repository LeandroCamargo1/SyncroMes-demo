"""
Models: Machine & Mold — Máquinas injetoras e moldes
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import MachineStatus, MoldStatus



class Machine(Base):
    __tablename__ = "machines"

    code = Column(String(20), unique=True, nullable=False, index=True)   # INJ-01..INJ-10
    name = Column(String(100), nullable=False)
    type = Column(String(50), default="injetora")
    tonnage = Column(Float, nullable=True)
    status = Column(Enum(MachineStatus), default=MachineStatus.stopped, nullable=False)
    current_product = Column(String(100), nullable=True)
    current_mold = Column(String(100), nullable=True)
    current_operator = Column(String(100), nullable=True)
    cycle_time_seconds = Column(Float, nullable=True)
    cavities = Column(Integer, default=1)
    efficiency = Column(Float, default=0.0)
    location = Column(String(100), default="Galpão Principal")
    work_center_id = Column(Integer, ForeignKey("work_centers.id"), nullable=True)
    metadata_extra = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)

    # ── Relationships ─────────────────────────────────────
    work_center = relationship("WorkCenter", back_populates="machines", lazy="joined")
    production_orders = relationship("ProductionOrder", back_populates="machine", lazy="noload")
    planning_entries = relationship("Planning", back_populates="machine", lazy="noload")
    production_entries = relationship("ProductionEntry", back_populates="machine", lazy="noload")
    active_downtimes = relationship("ActiveDowntime", back_populates="machine", lazy="noload")
    downtime_history = relationship("DowntimeHistory", back_populates="machine", lazy="noload")
    quality_measurements = relationship("QualityMeasurement", back_populates="machine", lazy="noload")
    rework_entries = relationship("ReworkEntry", back_populates="machine", lazy="noload")
    spc_data = relationship("SpcData", back_populates="machine", lazy="noload")
    oee_history = relationship("OeeHistory", back_populates="machine", lazy="noload")
    loss_entries = relationship("LossEntry", back_populates="machine", lazy="noload")
    setup_entries = relationship("SetupEntry", back_populates="machine", lazy="noload")
    pmp_entries = relationship("PmpEntry", back_populates="machine", lazy="noload")
    quality_lots = relationship("QualityLot", back_populates="machine", lazy="noload")
    operator_schedules = relationship("OperatorSchedule", back_populates="machine", lazy="noload")
    notifications = relationship("Notification", back_populates="machine", lazy="noload")
    machine_maintenances = relationship("MachineMaintenance", back_populates="machine", lazy="noload")

    @property
    def work_center_code(self) -> str | None:
        return self.work_center.code if self.work_center else None

    def __repr__(self):
        return f"<Machine {self.code} status={self.status}>"


class Mold(Base):
    __tablename__ = "molds"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    cavities = Column(Integer, default=1)
    cycle_time_ideal = Column(Float, nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    status = Column(Enum(MoldStatus), default=MoldStatus.disponivel, nullable=False)
    total_cycles = Column(Integer, default=0)
    max_cycles = Column(Integer, nullable=True)
    last_maintenance = Column(DateTime(timezone=True), nullable=True)
    weight_grams = Column(Float, nullable=True)
    material_type = Column(String(100), nullable=True)

    # ── Relationships ─────────────────────────────────────
    product = relationship("Product", back_populates="molds", lazy="joined")
    maintenances = relationship("MoldMaintenance", back_populates="mold", lazy="noload")
    production_orders = relationship("ProductionOrder", back_populates="mold", lazy="noload")

    @property
    def product_code(self) -> str | None:
        return self.product.code if self.product else None

    def __repr__(self):
        return f"<Mold {self.code} cavities={self.cavities}>"


# keep import for DateTime used by last_maintenance
from sqlalchemy import DateTime  # noqa: E402
