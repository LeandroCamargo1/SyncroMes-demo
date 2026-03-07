"""
Router: Production — Ordens, Planejamento e Lançamentos
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.production import ProductionOrder, Planning, ProductionEntry
from app.models.machine import Machine
from app.models.user import User
from app.schemas.production import (
    ProductionOrderCreate, ProductionOrderRead, ProductionOrderUpdate,
    PlanningCreate, PlanningRead,
    ProductionEntryCreate, ProductionEntryRead,
)
from app.services.auth_service import AuthService
from app.services.fk_resolver import (
    resolve_machine, resolve_machine_optional, resolve_product,
    resolve_operator_by_name, resolve_order, resolve_mold,
)

router = APIRouter()


# ── Ordens de Produção ────────────────────────────────────────
@router.get("/orders", response_model=list[ProductionOrderRead])
async def list_orders(
    status: str | None = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(ProductionOrder).order_by(ProductionOrder.created_at.desc()).limit(limit)
    if status:
        query = query.where(ProductionOrder.status == status)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.post("/orders", response_model=ProductionOrderRead, status_code=201)
async def create_order(
    body: ProductionOrderCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "pcp")),
):
    data = body.model_dump(exclude={"product_code", "machine_code", "mold_code"})
    data["product_id"] = await resolve_product(db, body.product_code)
    data["machine_id"] = await resolve_machine_optional(db, body.machine_code)
    data["mold_id"] = await resolve_mold(db, body.mold_code)
    order = ProductionOrder(**data)
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


@router.patch("/orders/{order_id}", response_model=ProductionOrderRead)
async def update_order(
    order_id: int,
    body: ProductionOrderUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "operador")),
):
    result = await db.execute(select(ProductionOrder).where(ProductionOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Ordem não encontrada")
    update_data = body.model_dump(exclude_unset=True)
    # Resolve FK fields from string codes
    if "machine_code" in update_data:
        update_data["machine_id"] = await resolve_machine_optional(db, update_data.pop("machine_code"))
    if "operator_name" in update_data:
        update_data["operator_id"] = await resolve_operator_by_name(db, update_data.pop("operator_name"))
    for field, value in update_data.items():
        setattr(order, field, value)
    await db.commit()
    await db.refresh(order)
    return order


# ── Planejamento ──────────────────────────────────────────────
@router.get("/planning", response_model=list[PlanningRead])
async def list_planning(
    machine_code: str | None = None,
    target_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(Planning).order_by(Planning.date, Planning.sequence)
    if machine_code:
        query = query.join(Planning.machine).where(Machine.code == machine_code)
    if target_date:
        query = query.where(Planning.date == target_date)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.post("/planning", response_model=PlanningRead, status_code=201)
async def create_planning(
    body: PlanningCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "pcp")),
):
    data = body.model_dump(exclude={"machine_code", "product_code", "mold_code", "operator_name"})
    data["machine_id"] = await resolve_machine(db, body.machine_code)
    data["product_id"] = await resolve_product(db, body.product_code)
    data["mold_id"] = await resolve_mold(db, body.mold_code)
    data["operator_id"] = await resolve_operator_by_name(db, body.operator_name)
    planning = Planning(**data)
    db.add(planning)
    await db.commit()
    await db.refresh(planning)
    return planning


# ── Lançamentos de Produção ───────────────────────────────────
@router.get("/entries", response_model=list[ProductionEntryRead])
async def list_entries(
    machine_code: str | None = None,
    order_number: str | None = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(ProductionEntry).order_by(ProductionEntry.timestamp.desc()).limit(limit)
    if machine_code:
        query = query.join(ProductionEntry.machine).where(Machine.code == machine_code)
    if order_number:
        query = query.join(ProductionEntry.order).where(ProductionOrder.order_number == order_number)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.post("/entries", response_model=ProductionEntryRead, status_code=201)
async def create_entry(
    body: ProductionEntryCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "operador")),
):
    data = body.model_dump(exclude={"machine_code", "product_code", "order_number", "operator_name"})
    data["machine_id"] = await resolve_machine(db, body.machine_code)
    data["product_id"] = await resolve_product(db, body.product_code)
    data["order_id"] = await resolve_order(db, body.order_number)
    data["operator_id"] = await resolve_operator_by_name(db, body.operator_name)
    entry = ProductionEntry(**data)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry
