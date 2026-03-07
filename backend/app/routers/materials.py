"""
Router: Materials — Materiais, BOM e Movimentações de Estoque
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.material import Material, BomLine, InventoryMovement
from app.models.product import Product
from app.models.user import User
from app.models.enums import InventoryMovementType
from app.schemas.material import (
    MaterialCreate, MaterialRead, MaterialUpdate,
    BomLineCreate, BomLineRead,
    InventoryMovementCreate, InventoryMovementRead,
)
from app.services.auth_service import AuthService

router = APIRouter()


# ── Materials ─────────────────────────────────────────────────

@router.get("/", response_model=list[MaterialRead])
async def list_materials(
    type: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    q = select(Material).where(Material.is_active == True)
    if type:
        q = q.where(Material.type == type)
    result = await db.execute(q.order_by(Material.code))
    return result.scalars().all()


@router.post("/", response_model=MaterialRead, status_code=201)
async def create_material(
    data: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "pcp")),
):
    mat = Material(**data.model_dump())
    db.add(mat)
    await db.commit()
    await db.refresh(mat)
    return mat


@router.patch("/{code}", response_model=MaterialRead)
async def update_material(
    code: str,
    data: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "pcp")),
):
    result = await db.execute(select(Material).where(Material.code == code))
    mat = result.scalar_one_or_none()
    if not mat:
        raise HTTPException(404, "Material não encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(mat, k, v)
    await db.commit()
    await db.refresh(mat)
    return mat


@router.get("/alerts")
async def material_alerts(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Materiais com estoque abaixo do mínimo."""
    result = await db.execute(
        select(Material).where(
            Material.is_active == True,
            Material.current_stock < Material.min_stock,
        ).order_by(Material.code)
    )
    return [
        {
            "code": m.code,
            "name": m.name,
            "current_stock": m.current_stock,
            "min_stock": m.min_stock,
            "deficit": m.min_stock - m.current_stock,
            "unit": m.unit.value if m.unit else "kg",
        }
        for m in result.scalars().all()
    ]


# ── BOM ───────────────────────────────────────────────────────

@router.get("/bom/{product_code}", response_model=list[BomLineRead])
async def get_bom(
    product_code: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    prod_result = await db.execute(select(Product).where(Product.code == product_code))
    product = prod_result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Produto não encontrado")
    result = await db.execute(
        select(BomLine).where(BomLine.product_id == product.id)
    )
    return result.scalars().unique().all()


@router.post("/bom", response_model=BomLineRead, status_code=201)
async def create_bom_line(
    data: BomLineCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "pcp")),
):
    prod_result = await db.execute(select(Product).where(Product.code == data.product_code))
    product = prod_result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, f"Produto '{data.product_code}' não encontrado")

    mat_result = await db.execute(select(Material).where(Material.code == data.material_code))
    material = mat_result.scalar_one_or_none()
    if not material:
        raise HTTPException(404, f"Material '{data.material_code}' não encontrado")

    bom = BomLine(
        product_id=product.id,
        material_id=material.id,
        quantity_per_unit=data.quantity_per_unit,
        unit=data.unit,
        is_primary=data.is_primary,
        notes=data.notes,
    )
    db.add(bom)
    await db.commit()
    await db.refresh(bom)
    return bom


# ── Inventory Movements ──────────────────────────────────────

@router.get("/movements", response_model=list[InventoryMovementRead])
async def list_movements(
    material_code: str | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    q = select(InventoryMovement)
    if material_code:
        q = q.join(InventoryMovement.material).where(Material.code == material_code)
    result = await db.execute(
        q.order_by(InventoryMovement.timestamp.desc()).limit(limit)
    )
    return result.scalars().unique().all()


@router.post("/movements", response_model=InventoryMovementRead, status_code=201)
async def create_movement(
    data: InventoryMovementCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "pcp", "operador")),
):
    mat_result = await db.execute(select(Material).where(Material.code == data.material_code))
    material = mat_result.scalar_one_or_none()
    if not material:
        raise HTTPException(404, f"Material '{data.material_code}' não encontrado")

    mov = InventoryMovement(
        material_id=material.id,
        movement_type=data.movement_type,
        quantity=data.quantity,
        lot_number=data.lot_number,
        reference=data.reference,
        performed_by=data.performed_by,
        notes=data.notes,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(mov)

    # Update current_stock
    if data.movement_type in (
        InventoryMovementType.entrada.value,
        InventoryMovementType.devolucao.value,
    ):
        material.current_stock += data.quantity
    elif data.movement_type in (
        InventoryMovementType.saida.value,
        InventoryMovementType.consumo.value,
    ):
        material.current_stock -= data.quantity
    # ajuste: set absolute value
    elif data.movement_type == InventoryMovementType.ajuste.value:
        material.current_stock = data.quantity

    await db.commit()
    await db.refresh(mov)

    # Check stock alert after movement
    if material.current_stock < material.min_stock:
        from app.services.event_dispatcher import dispatcher
        await dispatcher.stock_below_minimum(db, material.code, material.current_stock, material.min_stock)
        await db.commit()

    return mov
