"""
Router: Hierarchy — ISA-95 Equipment Hierarchy (Site / Area / WorkCenter)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.hierarchy import Site, Area, WorkCenter
from app.models.user import User
from app.schemas.hierarchy import (
    SiteCreate, SiteRead,
    AreaCreate, AreaRead,
    WorkCenterCreate, WorkCenterRead,
)
from app.services.auth_service import AuthService

router = APIRouter()


# ── Sites ─────────────────────────────────────────────────────

@router.get("/sites", response_model=list[SiteRead])
async def list_sites(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    result = await db.execute(
        select(Site).where(Site.is_active == True).order_by(Site.code)
    )
    return result.scalars().all()


@router.post("/sites", response_model=SiteRead, status_code=201)
async def create_site(
    data: SiteCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin")),
):
    site = Site(**data.model_dump())
    db.add(site)
    await db.commit()
    await db.refresh(site)
    return site


# ── Areas ─────────────────────────────────────────────────────

@router.get("/areas", response_model=list[AreaRead])
async def list_areas(
    site_code: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    q = select(Area).where(Area.is_active == True)
    if site_code:
        q = q.join(Area.site).where(Site.code == site_code)
    result = await db.execute(q.order_by(Area.code))
    return result.scalars().unique().all()


@router.post("/areas", response_model=AreaRead, status_code=201)
async def create_area(
    data: AreaCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin")),
):
    site_result = await db.execute(select(Site).where(Site.code == data.site_code))
    site = site_result.scalar_one_or_none()
    if not site:
        raise HTTPException(404, f"Site '{data.site_code}' não encontrado")
    area = Area(
        code=data.code,
        name=data.name,
        description=data.description,
        site_id=site.id,
    )
    db.add(area)
    await db.commit()
    await db.refresh(area)
    return area


# ── Work Centers ──────────────────────────────────────────────

@router.get("/work-centers", response_model=list[WorkCenterRead])
async def list_work_centers(
    area_code: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    q = select(WorkCenter).where(WorkCenter.is_active == True)
    if area_code:
        q = q.join(WorkCenter.area).where(Area.code == area_code)
    result = await db.execute(q.order_by(WorkCenter.code))
    return result.scalars().unique().all()


@router.post("/work-centers", response_model=WorkCenterRead, status_code=201)
async def create_work_center(
    data: WorkCenterCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin")),
):
    area_result = await db.execute(select(Area).where(Area.code == data.area_code))
    area = area_result.scalar_one_or_none()
    if not area:
        raise HTTPException(404, f"Area '{data.area_code}' não encontrada")
    wc = WorkCenter(
        code=data.code,
        name=data.name,
        description=data.description,
        area_id=area.id,
        capacity=data.capacity,
    )
    db.add(wc)
    await db.commit()
    await db.refresh(wc)
    return wc


@router.get("/tree")
async def get_hierarchy_tree(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    """Retorna a árvore hierárquica completa Site → Area → WorkCenter → Machines."""
    sites_result = await db.execute(
        select(Site).where(Site.is_active == True).order_by(Site.code)
    )
    sites = sites_result.scalars().all()

    tree = []
    for site in sites:
        areas_result = await db.execute(
            select(Area).where(Area.site_id == site.id, Area.is_active == True).order_by(Area.code)
        )
        areas_list = []
        for area in areas_result.scalars().all():
            wcs_result = await db.execute(
                select(WorkCenter).where(
                    WorkCenter.area_id == area.id, WorkCenter.is_active == True
                ).order_by(WorkCenter.code)
            )
            wcs_list = []
            for wc in wcs_result.scalars().all():
                from app.models.machine import Machine
                machines_result = await db.execute(
                    select(Machine).where(
                        Machine.work_center_id == wc.id, Machine.is_active == True
                    ).order_by(Machine.code)
                )
                wcs_list.append({
                    "code": wc.code,
                    "name": wc.name,
                    "machines": [
                        {"code": m.code, "name": m.name, "status": m.status.value if m.status else None}
                        for m in machines_result.scalars().all()
                    ],
                })
            areas_list.append({
                "code": area.code,
                "name": area.name,
                "work_centers": wcs_list,
            })
        tree.append({
            "code": site.code,
            "name": site.name,
            "areas": areas_list,
        })
    return tree
