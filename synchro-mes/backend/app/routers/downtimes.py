"""
Router: Downtimes — Paradas ativas e histórico
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.downtime import ActiveDowntime, DowntimeHistory
from app.models.machine import Machine
from app.models.user import User
from app.schemas.downtime import ActiveDowntimeCreate, ActiveDowntimeRead, DowntimeHistoryRead
from app.services.auth_service import AuthService
from app.services.fk_resolver import resolve_machine, resolve_operator_by_name

router = APIRouter()


# ── Paradas Ativas ────────────────────────────────────────────
@router.get("/active", response_model=list[ActiveDowntimeRead])
async def list_active(
    machine_code: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(ActiveDowntime).order_by(ActiveDowntime.start_time.desc())
    if machine_code:
        query = query.join(ActiveDowntime.machine).where(Machine.code == machine_code)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.post("/start", response_model=ActiveDowntimeRead, status_code=201)
async def start_downtime(
    body: ActiveDowntimeCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "operador")),
):
    """Inicia uma parada de máquina."""
    machine_id = await resolve_machine(db, body.machine_code)
    operator_id = await resolve_operator_by_name(db, body.operator_name)

    data = body.model_dump(exclude={"machine_code", "operator_name"})
    data["machine_id"] = machine_id
    data["operator_id"] = operator_id
    dt = ActiveDowntime(**data)
    db.add(dt)

    # Atualizar status da máquina
    result = await db.execute(select(Machine).where(Machine.id == machine_id))
    machine = result.scalar_one_or_none()
    if machine:
        machine.status = "stopped"

    await db.commit()
    await db.refresh(dt)
    return dt


@router.post("/stop/{downtime_id}", response_model=DowntimeHistoryRead)
async def stop_downtime(
    downtime_id: int,
    resolved_by: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "operador")),
):
    """Encerra uma parada e move para o histórico."""
    result = await db.execute(select(ActiveDowntime).where(ActiveDowntime.id == downtime_id))
    active = result.scalar_one_or_none()
    if not active:
        raise HTTPException(status_code=404, detail="Parada ativa não encontrada")

    now = datetime.now(timezone.utc)
    duration = (now - active.start_time).total_seconds() / 60

    history = DowntimeHistory(
        machine_id=active.machine_id,
        reason=active.reason,
        category=active.category,
        subcategory=active.subcategory,
        operator_id=active.operator_id,
        shift=active.shift,
        start_time=active.start_time,
        end_time=now,
        duration_minutes=round(duration, 1),
        is_planned=active.is_planned,
        notes=active.notes,
        resolved_by=resolved_by or _user.name,
    )
    db.add(history)
    await db.delete(active)

    # Checar se máquina tem outras paradas ativas
    remaining = await db.execute(
        select(ActiveDowntime).where(
            ActiveDowntime.machine_id == active.machine_id,
            ActiveDowntime.id != downtime_id,
        )
    )
    if not remaining.scalars().first():
        machine_result = await db.execute(
            select(Machine).where(Machine.id == active.machine_id)
        )
        machine = machine_result.scalar_one_or_none()
        if machine:
            machine.status = "running"

    await db.commit()
    await db.refresh(history)
    return history


# ── Histórico ─────────────────────────────────────────────────
@router.get("/history", response_model=list[DowntimeHistoryRead])
async def list_history(
    machine_code: str | None = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(DowntimeHistory).order_by(DowntimeHistory.end_time.desc()).limit(limit)
    if machine_code:
        query = query.join(DowntimeHistory.machine).where(Machine.code == machine_code)
    result = await db.execute(query)
    return result.scalars().unique().all()
