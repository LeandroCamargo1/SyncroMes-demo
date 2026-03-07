"""
Router: Leadership — Escala de operadores e absenteísmo
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.leadership import OperatorSchedule, AbsenteeismEntry
from app.models.user import User
from app.schemas.leadership import (
    OperatorScheduleCreate, OperatorScheduleRead,
    AbsenteeismCreate, AbsenteeismRead,
)
from app.services.auth_service import AuthService
from app.services.fk_resolver import resolve_operator_by_reg, resolve_machine_optional

router = APIRouter()


# ── Escala ───────────────────────────────────────────────
@router.get("/schedule", response_model=list[OperatorScheduleRead])
async def list_schedule(
    shift: str | None = None,
    date: str | None = None,
    limit: int = Query(200, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(OperatorSchedule).order_by(OperatorSchedule.date.desc()).limit(limit)
    if shift:
        query = query.where(OperatorSchedule.shift == shift)
    if date:
        query = query.where(OperatorSchedule.date == date)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.post("/schedule", response_model=OperatorScheduleRead, status_code=201)
async def create_schedule(
    body: OperatorScheduleCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor")),
):
    data = body.model_dump(exclude={"operator_registration", "machine_code"})
    data["operator_id"] = await resolve_operator_by_reg(db, body.operator_registration)
    data["machine_id"] = await resolve_machine_optional(db, body.machine_code)
    entry = OperatorSchedule(**data)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


# ── Absenteísmo ──────────────────────────────────────────
@router.get("/absenteeism", response_model=list[AbsenteeismRead])
async def list_absenteeism(
    reason: str | None = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(AbsenteeismEntry).order_by(AbsenteeismEntry.date.desc()).limit(limit)
    if reason:
        query = query.where(AbsenteeismEntry.reason == reason)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.post("/absenteeism", response_model=AbsenteeismRead, status_code=201)
async def create_absenteeism(
    body: AbsenteeismCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor")),
):
    data = body.model_dump(exclude={"operator_registration"})
    data["operator_id"] = await resolve_operator_by_reg(db, body.operator_registration)
    entry = AbsenteeismEntry(**data)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/summary")
async def leadership_summary(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    total_scheduled = await db.execute(select(func.count()).select_from(OperatorSchedule))
    total_absent = await db.execute(select(func.count()).select_from(AbsenteeismEntry))
    justified = await db.execute(
        select(func.count()).select_from(AbsenteeismEntry).where(AbsenteeismEntry.justified == True)
    )
    return {
        "total_scheduled": total_scheduled.scalar() or 0,
        "total_absences": total_absent.scalar() or 0,
        "justified_absences": justified.scalar() or 0,
    }
