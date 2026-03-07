"""
Model: Product — Catálogo de produtos plásticos injetados
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)   # TFT-28, FR-500
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    weight_grams = Column(Float, nullable=True)
    material = Column(String(100), nullable=True)    # PP, PE, ABS, PA, etc.
    color = Column(String(50), nullable=True)
    mold_code = Column(String(50), nullable=True)
    cycle_time_ideal = Column(Float, nullable=True)
    cavities = Column(Integer, default=1)
    category = Column(String(100), nullable=True)    # automotivo, eletrodomestico, etc.
    client = Column(String(200), nullable=True)
    ean = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    specs = Column(JSON, default=dict)               # especificações técnicas adicionais

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Product {self.code} name={self.name}>"
