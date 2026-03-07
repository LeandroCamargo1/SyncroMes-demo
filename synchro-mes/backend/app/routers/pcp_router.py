"""
Router: PCP — Planejamento e Controle da Produção
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.pcp import PcpMessage
from app.models.user import User
from app.schemas.pcp import PcpMessageCreate, PcpMessageRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/messages", response_model=list[PcpMessageRead])
async def list_messages(
    active_only: bool = True,
    priority: int | None = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(PcpMessage).order_by(PcpMessage.priority.desc(), PcpMessage.created_at.desc()).limit(limit)
    if active_only:
        query = query.where(PcpMessage.is_active == True)
    if priority is not None:
        query = query.where(PcpMessage.priority >= priority)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/messages", response_model=PcpMessageRead, status_code=201)
async def create_message(
    body: PcpMessageCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "pcp")),
):
    msg = PcpMessage(**body.model_dump())
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


@router.patch("/messages/{msg_id}/deactivate")
async def deactivate_message(
    msg_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "pcp")),
):
    result = await db.execute(select(PcpMessage).where(PcpMessage.id == msg_id))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    msg.is_active = False
    await db.commit()
    return {"ok": True}


@router.get("/queue")
async def production_queue(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Fila de produção priorizando ordens com maior prioridade."""
    from app.models.production import ProductionOrder
    result = await db.execute(
        select(ProductionOrder)
        .where(ProductionOrder.status.in_(["planejada", "em_producao"]))
        .order_by(ProductionOrder.priority.desc(), ProductionOrder.start_date.asc())
    )
    orders = result.scalars().all()
    return [
        {
            "id": o.id,
            "order_number": o.order_number,
            "product_code": o.product_code,
            "machine_code": o.machine_code,
            "quantity_planned": o.quantity_planned,
            "quantity_produced": o.quantity_produced,
            "priority": o.priority,
            "status": o.status,
            "start_date": o.start_date.isoformat() if o.start_date else None,
        }
        for o in orders
    ]
