"""
Router: Quality — Medições de qualidade
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.quality import QualityMeasurement
from app.models.user import User
from app.schemas.quality import QualityMeasurementCreate, QualityMeasurementRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/measurements", response_model=list[QualityMeasurementRead])
async def list_measurements(
    machine_code: str | None = None,
    product_code: str | None = None,
    approved: bool | None = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(QualityMeasurement).order_by(QualityMeasurement.timestamp.desc()).limit(limit)
    if machine_code:
        query = query.where(QualityMeasurement.machine_code == machine_code)
    if product_code:
        query = query.where(QualityMeasurement.product_code == product_code)
    if approved is not None:
        query = query.where(QualityMeasurement.is_approved == approved)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/measurements", response_model=QualityMeasurementRead, status_code=201)
async def create_measurement(
    body: QualityMeasurementCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "qualidade", "operador")),
):
    measurement = QualityMeasurement(**body.model_dump())
    db.add(measurement)
    await db.commit()
    await db.refresh(measurement)
    return measurement
