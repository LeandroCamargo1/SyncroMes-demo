"""
Model: Product — Catálogo de produtos plásticos injetados
"""
from sqlalchemy import Column, String, Float, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    weight_grams = Column(Float, nullable=True)
    material = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    cycle_time_ideal = Column(Float, nullable=True)
    cavities = Column(Integer, default=1)
    category = Column(String(100), nullable=True)
    client = Column(String(200), nullable=True)
    ean = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    specs = Column(JSON, default=dict)

    # ── Relationships ─────────────────────────────────────
    molds = relationship("Mold", back_populates="product", lazy="noload")
    production_orders = relationship("ProductionOrder", back_populates="product", lazy="noload")
    planning_entries = relationship("Planning", back_populates="product", lazy="noload")
    production_entries = relationship("ProductionEntry", back_populates="product", lazy="noload")
    quality_measurements = relationship("QualityMeasurement", back_populates="product", lazy="noload")
    rework_entries = relationship("ReworkEntry", back_populates="product", lazy="noload")
    spc_data = relationship("SpcData", back_populates="product", lazy="noload")
    loss_entries = relationship("LossEntry", back_populates="product", lazy="noload")
    pmp_entries = relationship("PmpEntry", back_populates="product", lazy="noload")
    quality_lots = relationship("QualityLot", back_populates="product", lazy="noload")

    def __repr__(self):
        return f"<Product {self.code} name={self.name}>"
