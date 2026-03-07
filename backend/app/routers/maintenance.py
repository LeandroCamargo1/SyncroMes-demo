"""
Router: Machine Maintenance — Manutenção de máquinas injetoras
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.machine_maintenance import MachineMaintenance
from app.models.machine import Machine
from app.models.user import User
from app.models.enums import MaintenanceStatus
from app.schemas.machine_maintenance import (
    MachineMaintenanceCreate, MachineMaintenanceFinish, MachineMaintenanceRead,
)
from app.services.auth_service import AuthService
from app.services.fk_resolver import resolve_machine

router = APIRouter()


@router.get("/", response_model=list[MachineMaintenanceRead])
async def list_maintenances(
    machine_code: str | None = None,
    status: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    q = select(MachineMaintenance)
    if machine_code:
        q = q.join(MachineMaintenance.machine).where(Machine.code == machine_code)
    if status:
        q = q.where(MachineMaintenance.status == status)
    result = await db.execute(
        q.order_by(MachineMaintenance.created_at.desc()).limit(limit)
    )
    return result.scalars().unique().all()


@router.post("/", response_model=MachineMaintenanceRead, status_code=201)
async def create_maintenance(
    data: MachineMaintenanceCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor")),
):
    machine_id = await resolve_machine(db, data.machine_code)
    maint = MachineMaintenance(
        machine_id=machine_id,
        maintenance_type=data.maintenance_type,
        priority=data.priority,
        description=data.description,
        technician=data.technician,
        scheduled_date=data.scheduled_date,
        start_time=datetime.now(timezone.utc),
        notes=data.notes,
        status=MaintenanceStatus.em_andamento,
    )
    db.add(maint)
    await db.commit()
    await db.refresh(maint)
    return maint


@router.patch("/{maint_id}/finish", response_model=MachineMaintenanceRead)
async def finish_maintenance(
    maint_id: int,
    data: MachineMaintenanceFinish,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor")),
):
    result = await db.execute(
        select(MachineMaintenance).where(MachineMaintenance.id == maint_id)
    )
    maint = result.scalar_one_or_none()
    if not maint:
        raise HTTPException(404, "Manutenção não encontrada")
    maint.end_time = data.end_time
    if maint.start_time:
        maint.duration_hours = (data.end_time - maint.start_time).total_seconds() / 3600
    if data.cost is not None:
        maint.cost = data.cost
    if data.parts_replaced is not None:
        maint.parts_replaced = data.parts_replaced
    if data.notes is not None:
        maint.notes = data.notes
    maint.status = MaintenanceStatus.concluida
    await db.commit()
    await db.refresh(maint)
    return maint


@router.get("/pending")
async def pending_maintenances(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Manutenções pendentes ou agendadas."""
    result = await db.execute(
        select(MachineMaintenance).where(
            MachineMaintenance.status.in_([
                MaintenanceStatus.pendente,
                MaintenanceStatus.em_andamento,
            ])
        ).order_by(MachineMaintenance.scheduled_date)
    )
    return [
        {
            "id": m.id,
            "machine_code": m.machine_code,
            "maintenance_type": m.maintenance_type.value if m.maintenance_type else None,
            "priority": m.priority.value if m.priority else None,
            "description": m.description,
            "scheduled_date": str(m.scheduled_date) if m.scheduled_date else None,
            "status": m.status.value if m.status else None,
        }
        for m in result.scalars().unique().all()
    ]
