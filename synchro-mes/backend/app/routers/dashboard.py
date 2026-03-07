"""
Router: Dashboard — Dados agregados para o painel principal
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Retorna o resumo completo do dashboard com todas as máquinas."""
    return await DashboardService.get_summary(db)
