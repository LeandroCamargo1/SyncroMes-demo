"""
Router: Quality — Medições de qualidade
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.quality import QualityMeasurement
from app.models.machine import Machine
from app.models.product import Product
from app.models.user import User
from app.schemas.quality import QualityMeasurementCreate, QualityMeasurementRead
from app.services.auth_service import AuthService
from app.services.fk_resolver import (
    resolve_machine, resolve_product, resolve_operator_by_name, resolve_order,
)

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
        query = query.join(QualityMeasurement.machine).where(Machine.code == machine_code)
    if product_code:
        query = query.join(QualityMeasurement.product).where(Product.code == product_code)
    if approved is not None:
        query = query.where(QualityMeasurement.is_approved == approved)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.post("/measurements", response_model=QualityMeasurementRead, status_code=201)
async def create_measurement(
    body: QualityMeasurementCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "supervisor", "qualidade", "operador")),
):
    data = body.model_dump(exclude={"machine_code", "product_code", "order_number", "operator_name"})
    data["machine_id"] = await resolve_machine(db, body.machine_code)
    data["product_id"] = await resolve_product(db, body.product_code)
    data["order_id"] = await resolve_order(db, body.order_number)
    data["operator_id"] = await resolve_operator_by_name(db, body.operator_name)
    measurement = QualityMeasurement(**data)
    db.add(measurement)
    await db.commit()
    await db.refresh(measurement)
    return measurement
