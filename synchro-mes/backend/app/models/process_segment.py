"""
Model: ProcessSegment — Definição de processo de fabricação por produto
ISA-95 Process Segment: parâmetros ideais de injeção para cada produto/máquina.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class ProcessSegment(Base):
    __tablename__ = "process_segments"
    __table_args__ = (
        UniqueConstraint("product_id", "machine_type", name="uq_process_product_machine_type"),
    )

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    machine_type = Column(String(50), default="injetora")
    cycle_time_ideal = Column(Float, nullable=True)
    injection_pressure = Column(Float, nullable=True)
    holding_pressure = Column(Float, nullable=True)
    melt_temperature = Column(Float, nullable=True)
    mold_temperature = Column(Float, nullable=True)
    cooling_time = Column(Float, nullable=True)
    injection_speed = Column(Float, nullable=True)
    screw_rpm = Column(Float, nullable=True)
    back_pressure = Column(Float, nullable=True)
    clamping_force = Column(Float, nullable=True)
    notes = Column(String(500), nullable=True)

    # ── Relationships ─────────────────────────────────────
    product = relationship("Product", back_populates="process_segments", lazy="joined")

    @property
    def product_code(self) -> str | None:
        return self.product.code if self.product else None

    def __repr__(self):
        return f"<ProcessSegment product_id={self.product_id} cycle={self.cycle_time_ideal}>"
