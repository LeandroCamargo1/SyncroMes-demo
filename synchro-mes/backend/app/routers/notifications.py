"""
Router: Notifications — Listagem, marcar como lida, contagem de não-lidas
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationRead, NotificationMarkRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/", response_model=list[NotificationRead])
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Lista notificações (mais recentes primeiro)."""
    stmt = select(Notification).order_by(Notification.created_at.desc()).limit(limit)
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)
    result = await db.execute(stmt)
    return result.scalars().unique().all()


@router.get("/count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Retorna contagem de notificações não lidas."""
    result = await db.execute(
        select(func.count(Notification.id)).where(Notification.is_read == False)
    )
    return {"unread": result.scalar() or 0}


@router.patch("/read")
async def mark_as_read(
    body: NotificationMarkRead,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Marca uma lista de notificações como lidas."""
    await db.execute(
        update(Notification)
        .where(Notification.id.in_(body.ids))
        .values(is_read=True)
    )
    await db.commit()
    return {"marked": len(body.ids)}


@router.patch("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Marca todas as notificações como lidas."""
    result = await db.execute(
        update(Notification)
        .where(Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()
    return {"marked": result.rowcount}
