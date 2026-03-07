"""
Router: OEE — Histórico e cálculos de OEE
"""
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.oee import OeeHistoryRead, OeeSummary
from app.services.auth_service import AuthService
from app.services.oee_service import OeeService

router = APIRouter()


@router.get("/history", response_model=list[OeeHistoryRead])
async def get_oee_history(
    machine_code: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    return await OeeService.get_history(db, machine_code, start_date, end_date, limit)


@router.get("/machine/{machine_code}", response_model=OeeSummary)
async def get_machine_oee(
    machine_code: str,
    target_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    return await OeeService.get_summary_by_machine(db, machine_code, target_date)


@router.get("/factory", response_model=dict)
async def get_factory_oee(
    target_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    return await OeeService.get_factory_average(db, target_date)
