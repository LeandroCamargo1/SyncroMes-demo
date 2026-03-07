"""
Router: History — Log de auditoria do sistema
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.system_log import SystemLog
from app.models.user import User
from app.schemas.common import SystemLogRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/", response_model=list[SystemLogRead])
async def list_logs(
    action: str | None = None,
    user_email: str | None = None,
    entity_type: str | None = None,
    limit: int = Query(200, le=1000),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin")),
):
    query = select(SystemLog).order_by(SystemLog.timestamp.desc()).limit(limit)
    if action:
        query = query.where(SystemLog.action == action)
    if user_email:
        query = query.where(SystemLog.user_email == user_email)
    if entity_type:
        query = query.where(SystemLog.entity_type == entity_type)
    result = await db.execute(query)
    return result.scalars().all()
