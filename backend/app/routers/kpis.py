"""
Router: KPIs — ISO-22400 Advanced KPIs + Process Segments
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.process_segment import ProcessSegment
from app.models.product import Product
from app.models.user import User
from app.schemas.kpi import AdvancedKpiResponse
from app.schemas.process_segment import ProcessSegmentCreate, ProcessSegmentRead
from app.services.auth_service import AuthService
from app.services.kpi_service import KpiService
from app.services.fk_resolver import resolve_product

router = APIRouter()


# ── Advanced KPIs ─────────────────────────────────────────────

@router.get("/advanced", response_model=AdvancedKpiResponse)
async def get_advanced_kpis(
    machine_code: str | None = None,
    period_days: int = 1,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """KPIs avançados ISO-22400: TEEP, NEE, MTBF, MTTR, Setup Ratio, etc."""
    data = await KpiService.get_advanced_kpis(db, machine_code, period_days)
    return AdvancedKpiResponse(**data)


# ── Process Segments ──────────────────────────────────────────

@router.get("/process-segments", response_model=list[ProcessSegmentRead])
async def list_process_segments(
    product_code: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    q = select(ProcessSegment)
    if product_code:
        q = q.join(ProcessSegment.product).where(Product.code == product_code)
    result = await db.execute(q.order_by(ProcessSegment.id))
    return result.scalars().unique().all()


@router.post("/process-segments", response_model=ProcessSegmentRead, status_code=201)
async def create_process_segment(
    data: ProcessSegmentCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "pcp")),
):
    product_id = await resolve_product(db, data.product_code)
    ps = ProcessSegment(
        product_id=product_id,
        machine_type=data.machine_type,
        cycle_time_ideal=data.cycle_time_ideal,
        injection_pressure=data.injection_pressure,
        holding_pressure=data.holding_pressure,
        melt_temperature=data.melt_temperature,
        mold_temperature=data.mold_temperature,
        cooling_time=data.cooling_time,
        injection_speed=data.injection_speed,
        screw_rpm=data.screw_rpm,
        back_pressure=data.back_pressure,
        clamping_force=data.clamping_force,
        notes=data.notes,
    )
    db.add(ps)
    await db.commit()
    await db.refresh(ps)
    return ps
