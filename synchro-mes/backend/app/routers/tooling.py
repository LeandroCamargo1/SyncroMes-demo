"""
Router: Tooling (Ferramentaria) — Moldes e Manutenções
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.mold_maintenance import MoldMaintenance
from app.models.machine import Mold
from app.models.user import User
from app.schemas.tooling import (
    MoldMaintenanceCreate, MoldMaintenanceFinish, MoldMaintenanceRead, MoldUpdate,
)
from app.services.auth_service import AuthService

router = APIRouter()


# ── Moldes ───────────────────────────────────────────────
@router.get("/molds")
async def list_molds(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    result = await db.execute(select(Mold).order_by(Mold.code))
    molds = result.scalars().all()
    return [
        {
            "id": m.id,
            "code": m.code,
            "description": m.description,
            "cavities": m.cavities,
            "cycle_time": m.cycle_time,
            "current_shots": m.current_shots,
            "max_shots": m.max_shots,
            "status": m.status,
        }
        for m in molds
    ]


@router.patch("/molds/{mold_code}")
async def update_mold(
    mold_code: str,
    body: MoldUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor")),
):
    result = await db.execute(select(Mold).where(Mold.code == mold_code))
    mold = result.scalar_one_or_none()
    if not mold:
        raise HTTPException(status_code=404, detail="Molde não encontrado")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(mold, field, value)
    await db.commit()
    await db.refresh(mold)
    return {"ok": True, "code": mold.code}


# ── Manutenções ──────────────────────────────────────────
@router.get("/maintenance", response_model=list[MoldMaintenanceRead])
async def list_maintenance(
    mold_code: str | None = None,
    status: str | None = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(MoldMaintenance).order_by(MoldMaintenance.created_at.desc()).limit(limit)
    if mold_code:
        query = query.where(MoldMaintenance.mold_code == mold_code)
    if status:
        query = query.where(MoldMaintenance.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/maintenance", response_model=MoldMaintenanceRead, status_code=201)
async def create_maintenance(
    body: MoldMaintenanceCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor")),
):
    entry = MoldMaintenance(**body.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.patch("/maintenance/{maint_id}/finish", response_model=MoldMaintenanceRead)
async def finish_maintenance(
    maint_id: int,
    body: MoldMaintenanceFinish,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor")),
):
    result = await db.execute(select(MoldMaintenance).where(MoldMaintenance.id == maint_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")

    entry.status = "concluida"
    entry.duration_hours = body.duration_hours
    if body.cost is not None:
        entry.cost = body.cost
    if body.parts_replaced:
        entry.parts_replaced = body.parts_replaced
    if body.notes:
        entry.notes = body.notes
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/alerts")
async def mold_alerts(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Alertas: moldes próximos do limite de batidas e manutenções pendentes."""
    result = await db.execute(select(Mold))
    molds = result.scalars().all()

    alerts = []
    for m in molds:
        if m.max_shots and m.current_shots:
            ratio = m.current_shots / m.max_shots
            if ratio >= 0.9:
                alerts.append({
                    "type": "shots_limit",
                    "severity": "critical" if ratio >= 1.0 else "warning",
                    "mold_code": m.code,
                    "current_shots": m.current_shots,
                    "max_shots": m.max_shots,
                    "percentage": round(ratio * 100, 1),
                })

    pending = await db.execute(
        select(func.count()).select_from(MoldMaintenance).where(MoldMaintenance.status == "pendente")
    )
    pending_count = pending.scalar() or 0
    if pending_count > 0:
        alerts.append({
            "type": "pending_maintenance",
            "severity": "info",
            "count": pending_count,
        })

    return alerts
