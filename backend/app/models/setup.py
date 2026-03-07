"""
Model: SetupEntry — Registros de setup de máquinas
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import SetupType, SetupStatus


class SetupEntry(Base):
    __tablename__ = "setup_entries"

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    setup_type = Column(Enum(SetupType), nullable=False)
    mold_from = Column(String(50), nullable=True)
    mold_to = Column(String(50), nullable=True)
    product_from = Column(String(50), nullable=True)
    product_to = Column(String(50), nullable=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    shift = Column(String(20), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Float, nullable=True)
    status = Column(Enum(SetupStatus), default=SetupStatus.em_andamento, nullable=False)
    notes = Column(String(500), nullable=True)

    # ── Relationships ─────────────────────────────────────
    machine = relationship("Machine", back_populates="setup_entries", lazy="joined")
    operator = relationship("Operator", back_populates="setup_entries", lazy="joined")

    @property
    def machine_code(self) -> str | None:
        return self.machine.code if self.machine else None

    @property
    def operator_name(self) -> str | None:
        return self.operator.name if self.operator else None

    def __repr__(self):
        return f"<SetupEntry machine_id={self.machine_id} type={self.setup_type}>"
