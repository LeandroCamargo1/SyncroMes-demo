"""
Router: Admin Data — Gestão de dados mestres (produtos, operadores, máquinas)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.models.operator import Operator
from app.models.machine import Machine, Mold
from app.models.user import User
from app.services.auth_service import AuthService

router = APIRouter()


# ── Produtos ─────────────────────────────────────────────
@router.get("/products")
async def list_products(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    result = await db.execute(select(Product).order_by(Product.code))
    products = result.scalars().all()
    return [
        {"id": p.id, "code": p.code, "name": p.name, "weight_grams": p.weight_grams, "cycle_time_ideal": p.cycle_time_ideal}
        for p in products
    ]


@router.post("/products")
async def create_product(
    body: dict,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin")),
):
    product = Product(
        code=body["code"],
        name=body.get("name", body.get("description", "")),
        description=body.get("description"),
        weight_grams=body.get("weight_grams"),
        cycle_time_ideal=body.get("cycle_time_ideal"),
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return {"id": product.id, "code": product.code}


# ── Operadores ───────────────────────────────────────────
@router.get("/operators")
async def list_operators(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.get_current_user),
):
    result = await db.execute(select(Operator).order_by(Operator.name))
    operators = result.scalars().all()
    return [
        {"id": o.id, "registration": o.registration, "name": o.name, "shift": o.shift, "is_active": o.is_active}
        for o in operators
    ]


@router.post("/operators")
async def create_operator(
    body: dict,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin")),
):
    operator = Operator(
        registration=body["registration"],
        name=body["name"],
        shift=body.get("shift", "A"),
        is_active=body.get("is_active", True),
    )
    db.add(operator)
    await db.commit()
    await db.refresh(operator)
    return {"id": operator.id, "registration": operator.registration}


# ── Máquinas ─────────────────────────────────────────────
@router.get("/machines-admin")
async def list_machines_admin(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin")),
):
    result = await db.execute(select(Machine).order_by(Machine.code))
    machines = result.scalars().all()
    return [
        {
            "id": m.id,
            "code": m.code,
            "name": m.name,
            "type": m.type,
            "status": m.status,
            "tonnage": m.tonnage,
        }
        for m in machines
    ]


# ── Moldes ───────────────────────────────────────────────
@router.get("/molds-admin")
async def list_molds_admin(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(AuthService.require_role("admin")),
):
    result = await db.execute(select(Mold).order_by(Mold.code))
    molds = result.scalars().all()
    return [
        {
            "id": m.id,
            "code": m.code,
            "name": m.name,
            "cavities": m.cavities,
            "cycle_time_ideal": m.cycle_time_ideal,
            "total_cycles": m.total_cycles,
            "max_cycles": m.max_cycles,
            "status": m.status,
        }
        for m in molds
    ]
