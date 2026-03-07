"""
Router: Production — Ordens, Planejamento e Lançamentos
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.production import ProductionOrder, Planning, ProductionEntry
from app.models.user import User
from app.schemas.production import (
    ProductionOrderCreate, ProductionOrderRead, ProductionOrderUpdate,
    PlanningCreate, PlanningRead,
    ProductionEntryCreate, ProductionEntryRead,
)
from app.services.auth_service import AuthService

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
    return result.scalars().all()


@router.post("/orders", response_model=ProductionOrderRead, status_code=201)
async def create_order(
    body: ProductionOrderCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "pcp")),
):
    order = ProductionOrder(**body.model_dump())
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
    for field, value in body.model_dump(exclude_unset=True).items():
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
        query = query.where(Planning.machine_code == machine_code)
    if target_date:
        query = query.where(Planning.date == target_date)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/planning", response_model=PlanningRead, status_code=201)
async def create_planning(
    body: PlanningCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "pcp")),
):
    planning = Planning(**body.model_dump())
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
        query = query.where(ProductionEntry.machine_code == machine_code)
    if order_number:
        query = query.where(ProductionEntry.order_number == order_number)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/entries", response_model=ProductionEntryRead, status_code=201)
async def create_entry(
    body: ProductionEntryCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "operador")),
):
    entry = ProductionEntry(**body.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry
