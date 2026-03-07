"""
OeeService — Cálculo e consulta de OEE (Overall Equipment Effectiveness)
"""
from datetime import date, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.oee import OeeHistory
from app.models.machine import Machine
from app.models.production import ProductionEntry
from app.models.downtime import DowntimeHistory
from app.schemas.oee import OeeSummary


class OeeService:

    @staticmethod
    async def get_history(
        db: AsyncSession,
        machine_code: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 30,
    ) -> list[OeeHistory]:
        query = select(OeeHistory).order_by(OeeHistory.date.desc())
        if machine_code:
            query = query.join(OeeHistory.machine).where(Machine.code == machine_code)
        if start_date:
            query = query.where(OeeHistory.date >= start_date)
        if end_date:
            query = query.where(OeeHistory.date <= end_date)
        query = query.limit(limit)
        result = await db.execute(query)
        return result.scalars().unique().all()

    @staticmethod
    async def get_summary_by_machine(
        db: AsyncSession,
        machine_code: str,
        target_date: date | None = None,
    ) -> OeeSummary:
        d = target_date or date.today()
        result = await db.execute(
            select(OeeHistory)
            .join(OeeHistory.machine)
            .where(Machine.code == machine_code, OeeHistory.date == d)
            .limit(1)
        )
        record = result.scalar_one_or_none()
        if record:
            return OeeSummary(
                machine_code=machine_code,
                oee=record.oee,
                availability=record.availability,
                performance=record.performance,
                quality_rate=record.quality_rate,
                period="today",
            )
        return OeeSummary(
            machine_code=machine_code,
            oee=0, availability=0, performance=0, quality_rate=0,
            period="today",
        )

    @staticmethod
    async def get_factory_average(
        db: AsyncSession,
        target_date: date | None = None,
    ) -> dict:
        """Retorna média OEE da fábrica inteira para a data."""
        d = target_date or date.today()
        result = await db.execute(
            select(
                func.avg(OeeHistory.oee).label("avg_oee"),
                func.avg(OeeHistory.availability).label("avg_avail"),
                func.avg(OeeHistory.performance).label("avg_perf"),
                func.avg(OeeHistory.quality_rate).label("avg_quality"),
                func.count(OeeHistory.id).label("count"),
            ).where(OeeHistory.date == d)
        )
        row = result.one()
        return {
            "oee": round(row.avg_oee or 0, 1),
            "availability": round(row.avg_avail or 0, 1),
            "performance": round(row.avg_perf or 0, 1),
            "quality_rate": round(row.avg_quality or 0, 1),
            "machines_count": row.count,
            "date": d.isoformat(),
        }

    @staticmethod
    def calculate_oee(
        planned_minutes: float,
        running_minutes: float,
        total_produced: int,
        good_produced: int,
        ideal_cycle_seconds: float,
    ) -> dict:
        """Cálculo puro de OEE — sem banco de dados."""
        if planned_minutes <= 0 or ideal_cycle_seconds <= 0:
            return {"availability": 0, "performance": 0, "quality_rate": 0, "oee": 0}

        availability = (running_minutes / planned_minutes) * 100
        max_possible = (running_minutes * 60) / ideal_cycle_seconds
        performance = (total_produced / max_possible * 100) if max_possible > 0 else 0
        quality_rate = (good_produced / total_produced * 100) if total_produced > 0 else 0
        oee = (availability * performance * quality_rate) / 10000

        return {
            "availability": round(min(availability, 100), 1),
            "performance": round(min(performance, 100), 1),
            "quality_rate": round(min(quality_rate, 100), 1),
            "oee": round(min(oee, 100), 1),
        }
