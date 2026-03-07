"""
Router: PMP — Moído, Borra e Sucata
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.pmp import PmpEntry
from app.models.user import User
from app.schemas.pmp import PmpEntryCreate, PmpEntryRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/", response_model=list[PmpEntryRead])
async def list_pmp(
    pmp_type: str | None = None,
    machine_code: str | None = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(PmpEntry).order_by(PmpEntry.created_at.desc()).limit(limit)
    if pmp_type:
        query = query.where(PmpEntry.type == pmp_type)
    if machine_code:
        query = query.where(PmpEntry.machine_code == machine_code)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=PmpEntryRead, status_code=201)
async def create_pmp(
    body: PmpEntryCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "operador")),
):
    entry = PmpEntry(**body.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/summary")
async def pmp_summary(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = (
        select(PmpEntry.type, func.sum(PmpEntry.weight_kg), func.count())
        .group_by(PmpEntry.type)
    )
    result = await db.execute(query)
    rows = result.all()
    return [{"type": r[0], "total_kg": float(r[1] or 0), "count": r[2]} for r in rows]
