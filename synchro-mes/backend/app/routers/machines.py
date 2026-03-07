"""
Router: Machines — CRUD de máquinas
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.machine import Machine, Mold
from app.models.user import User
from app.schemas.machine import MachineRead, MachineUpdate, MoldRead
from app.services.auth_service import AuthService
from app.services.event_dispatcher import dispatcher

router = APIRouter()


@router.get("/", response_model=list[MachineRead])
async def list_machines(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Lista todas as máquinas ativas."""
    result = await db.execute(
        select(Machine).where(Machine.is_active == True).order_by(Machine.code)
    )
    return result.scalars().all()


@router.get("/{code}", response_model=MachineRead)
async def get_machine(
    code: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    result = await db.execute(select(Machine).where(Machine.code == code))
    machine = result.scalar_one_or_none()
    if not machine:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    return machine


@router.patch("/{code}", response_model=MachineRead)
async def update_machine(
    code: str,
    body: MachineUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor")),
):
    result = await db.execute(select(Machine).where(Machine.code == code))
    machine = result.scalar_one_or_none()
    if not machine:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")

    old_status = machine.status
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(machine, field, value)
    await db.commit()
    await db.refresh(machine)
    if machine.status != old_status:
        await dispatcher.machine_status_changed(db, code, str(old_status), str(machine.status), machine_id=machine.id)
        await db.commit()
    return machine


# ── Moldes ────────────────────────────────────────────────────
@router.get("/molds/all", response_model=list[MoldRead])
async def list_molds(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    result = await db.execute(select(Mold).order_by(Mold.code))
    return result.scalars().all()
