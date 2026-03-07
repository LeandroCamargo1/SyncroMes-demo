"""
Router: Setup — Registros de setup de máquinas
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.setup import SetupEntry
from app.models.machine import Machine
from app.models.user import User
from app.schemas.setup import SetupEntryCreate, SetupEntryFinish, SetupEntryRead
from app.services.auth_service import AuthService
from app.services.fk_resolver import resolve_machine, resolve_operator_by_name

router = APIRouter()


@router.get("/", response_model=list[SetupEntryRead])
async def list_setups(
    machine_code: str | None = None,
    status: str | None = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(SetupEntry).order_by(SetupEntry.start_time.desc()).limit(limit)
    if machine_code:
        query = query.join(SetupEntry.machine).where(Machine.code == machine_code)
    if status:
        query = query.where(SetupEntry.status == status)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.post("/", response_model=SetupEntryRead, status_code=201)
async def start_setup(
    body: SetupEntryCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "operador")),
):
    data = body.model_dump(exclude={"machine_code", "operator_name"})
    data["machine_id"] = await resolve_machine(db, body.machine_code)
    data["operator_id"] = await resolve_operator_by_name(db, body.operator_name)
    entry = SetupEntry(**data)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.patch("/{setup_id}/finish", response_model=SetupEntryRead)
async def finish_setup(
    setup_id: int,
    body: SetupEntryFinish,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "operador")),
):
    result = await db.execute(select(SetupEntry).where(SetupEntry.id == setup_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Setup não encontrado")

    now = body.end_time or datetime.now(timezone.utc)
    entry.end_time = now
    entry.duration_minutes = round((now - entry.start_time).total_seconds() / 60, 1)
    entry.status = "concluido"
    if body.notes:
        entry.notes = body.notes
    await db.commit()
    await db.refresh(entry)
    return entry
