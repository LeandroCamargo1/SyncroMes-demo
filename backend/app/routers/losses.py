"""
Router: Losses — Registros de perdas de produção
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.loss import LossEntry
from app.models.machine import Machine
from app.models.user import User
from app.schemas.loss import LossEntryCreate, LossEntryRead
from app.services.auth_service import AuthService
from app.services.fk_resolver import (
    resolve_machine, resolve_product, resolve_operator_by_name, resolve_order,
)

router = APIRouter()


@router.get("/", response_model=list[LossEntryRead])
async def list_losses(
    machine_code: str | None = None,
    category: str | None = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(LossEntry).order_by(LossEntry.timestamp.desc()).limit(limit)
    if machine_code:
        query = query.join(LossEntry.machine).where(Machine.code == machine_code)
    if category:
        query = query.where(LossEntry.category == category)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.post("/", response_model=LossEntryRead, status_code=201)
async def create_loss(
    body: LossEntryCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "operador")),
):
    data = body.model_dump(exclude={"machine_code", "product_code", "order_number", "operator_name"})
    data["machine_id"] = await resolve_machine(db, body.machine_code)
    data["product_id"] = await resolve_product(db, body.product_code)
    data["order_id"] = await resolve_order(db, body.order_number)
    data["operator_id"] = await resolve_operator_by_name(db, body.operator_name)
    entry = LossEntry(**data)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/summary", response_model=dict)
async def losses_summary(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    result = await db.execute(
        select(
            LossEntry.category,
            func.sum(LossEntry.quantity).label("total_qty"),
            func.count(LossEntry.id).label("count"),
        ).group_by(LossEntry.category)
    )
    rows = result.all()
    return {
        "by_category": [
            {"category": r.category, "total_qty": r.total_qty or 0, "count": r.count}
            for r in rows
        ]
    }
