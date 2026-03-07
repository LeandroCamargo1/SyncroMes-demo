"""
FK Resolver — Resolve string codes to FK integer IDs.
Used by routers to bridge the API (string codes) with models (FK integers).
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.machine import Machine, Mold
from app.models.product import Product
from app.models.operator import Operator
from app.models.production import ProductionOrder


async def resolve_machine(db: AsyncSession, code: str) -> int:
    r = await db.execute(select(Machine.id).where(Machine.code == code))
    mid = r.scalar_one_or_none()
    if mid is None:
        raise HTTPException(404, f"Máquina '{code}' não encontrada")
    return mid


async def resolve_machine_optional(db: AsyncSession, code: str | None) -> int | None:
    if not code:
        return None
    r = await db.execute(select(Machine.id).where(Machine.code == code))
    return r.scalar_one_or_none()


async def resolve_product(db: AsyncSession, code: str) -> int:
    r = await db.execute(select(Product.id).where(Product.code == code))
    pid = r.scalar_one_or_none()
    if pid is None:
        raise HTTPException(404, f"Produto '{code}' não encontrado")
    return pid


async def resolve_product_optional(db: AsyncSession, code: str | None) -> int | None:
    if not code:
        return None
    r = await db.execute(select(Product.id).where(Product.code == code))
    return r.scalar_one_or_none()


async def resolve_operator_by_name(db: AsyncSession, name: str | None) -> int | None:
    if not name:
        return None
    r = await db.execute(select(Operator.id).where(Operator.name == name))
    return r.scalar_one_or_none()


async def resolve_operator_by_reg(db: AsyncSession, reg: str) -> int:
    r = await db.execute(select(Operator.id).where(Operator.registration == reg))
    oid = r.scalar_one_or_none()
    if oid is None:
        raise HTTPException(404, f"Operador '{reg}' não encontrado")
    return oid


async def resolve_order(db: AsyncSession, order_number: str | None) -> int | None:
    if not order_number:
        return None
    r = await db.execute(select(ProductionOrder.id).where(ProductionOrder.order_number == order_number))
    return r.scalar_one_or_none()


async def resolve_mold(db: AsyncSession, code: str | None) -> int | None:
    if not code:
        return None
    r = await db.execute(select(Mold.id).where(Mold.code == code))
    return r.scalar_one_or_none()
