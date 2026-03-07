"""
Models: Material, MaterialInventory, BomLine — Gestão de materiais e BOM
ISA-95 Material Model para rastreabilidade de insumos na injeção plástica.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime, Enum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import MaterialType, MaterialUnit, InventoryMovementType


class Material(Base):
    __tablename__ = "materials"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    type = Column(Enum(MaterialType), nullable=False)
    unit = Column(Enum(MaterialUnit), default=MaterialUnit.kg, nullable=False)
    density = Column(Float, nullable=True)
    supplier = Column(String(200), nullable=True)
    min_stock = Column(Float, default=0)
    current_stock = Column(Float, default=0)
    cost_per_unit = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    # ── Relationships ─────────────────────────────────────
    bom_lines = relationship("BomLine", back_populates="material", lazy="noload")
    inventory_movements = relationship("InventoryMovement", back_populates="material", lazy="noload")

    @property
    def below_min_stock(self) -> bool:
        return self.current_stock < self.min_stock

    def __repr__(self):
        return f"<Material {self.code} stock={self.current_stock}>"


class BomLine(Base):
    """Bill of Materials — linha de composição material→produto."""
    __tablename__ = "bom_lines"
    __table_args__ = (
        UniqueConstraint("product_id", "material_id", name="uq_bom_product_material"),
    )

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity_per_unit = Column(Float, nullable=False)
    unit = Column(Enum(MaterialUnit), default=MaterialUnit.kg)
    is_primary = Column(Boolean, default=False)
    notes = Column(String(300), nullable=True)

    # ── Relationships ─────────────────────────────────────
    product = relationship("Product", back_populates="bom_lines", lazy="joined")
    material = relationship("Material", back_populates="bom_lines", lazy="joined")

    @property
    def product_code(self) -> str | None:
        return self.product.code if self.product else None

    @property
    def material_code(self) -> str | None:
        return self.material.code if self.material else None

    def __repr__(self):
        return f"<BomLine product={self.product_id} material={self.material_id}>"


class InventoryMovement(Base):
    """Movimentação de estoque de materiais."""
    __tablename__ = "inventory_movements"

    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    movement_type = Column(Enum(InventoryMovementType), nullable=False)
    quantity = Column(Float, nullable=False)
    lot_number = Column(String(50), nullable=True)
    reference = Column(String(200), nullable=True)
    performed_by = Column(String(100), nullable=True)
    notes = Column(String(500), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=True)

    # ── Relationships ─────────────────────────────────────
    material = relationship("Material", back_populates="inventory_movements", lazy="joined")

    @property
    def material_code(self) -> str | None:
        return self.material.code if self.material else None

    def __repr__(self):
        return f"<InventoryMovement {self.movement_type} qty={self.quantity}>"
