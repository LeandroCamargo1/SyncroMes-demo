"""
Router: Quality Lots — Triagem e quarentena de lotes
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.quality_lot import QualityLot
from app.models.user import User
from app.schemas.quality_lot import QualityLotCreate, QualityLotUpdate, QualityLotRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/lots", response_model=list[QualityLotRead])
async def list_lots(
    status: str | None = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    query = select(QualityLot).order_by(QualityLot.created_at.desc()).limit(limit)
    if status:
        query = query.where(QualityLot.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/lots", response_model=QualityLotRead, status_code=201)
async def create_lot(
    body: QualityLotCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "qualidade")),
):
    lot = QualityLot(**body.model_dump())
    db.add(lot)
    await db.commit()
    await db.refresh(lot)
    return lot


@router.patch("/lots/{lot_id}", response_model=QualityLotRead)
async def update_lot(
    lot_id: int,
    body: QualityLotUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin", "qualidade")),
):
    result = await db.execute(select(QualityLot).where(QualityLot.id == lot_id))
    lot = result.scalar_one_or_none()
    if not lot:
        raise HTTPException(status_code=404, detail="Lote não encontrado")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(lot, field, value)

    if body.status == "concluida":
        lot.concluded_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(lot)
    return lot


@router.get("/lots/summary")
async def lots_summary(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    result = await db.execute(select(QualityLot))
    lots = result.scalars().all()
    summary = {"quarentena": 0, "em_triagem": 0, "concluida": 0, "total_approved": 0, "total_rejected": 0}
    for lot in lots:
        if lot.status in summary:
            summary[lot.status] += 1
        summary["total_approved"] += lot.approved_qty or 0
        summary["total_rejected"] += lot.rejected_qty or 0
    return summary


@router.get("/reports")
async def quality_reports(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Relatório agregado de qualidade."""
    from app.models.quality import QualityMeasurement
    from sqlalchemy import func

    total = await db.execute(select(func.count()).select_from(QualityMeasurement))
    approved = await db.execute(
        select(func.count()).select_from(QualityMeasurement).where(QualityMeasurement.approved == True)
    )
    total_val = total.scalar() or 0
    approved_val = approved.scalar() or 0
    rejected_val = total_val - approved_val

    return {
        "total_measurements": total_val,
        "approved": approved_val,
        "rejected": rejected_val,
        "approval_rate": round((approved_val / total_val * 100) if total_val > 0 else 0, 1),
    }
