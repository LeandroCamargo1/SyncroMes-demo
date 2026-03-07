"""
DashboardService — Dados agregados para o painel principal
"""
from datetime import date, datetime, timezone
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.machine import Machine
from app.models.production import ProductionEntry, ProductionOrder
from app.models.downtime import ActiveDowntime
from app.models.oee import OeeHistory
from app.schemas.dashboard import DashboardSummary, MachineCardData


class DashboardService:

    @staticmethod
    async def get_summary(db: AsyncSession) -> DashboardSummary:
        """Monta o resumo completo do dashboard."""

        # 1. Máquinas
        machines_result = await db.execute(
            select(Machine).where(Machine.is_active == True)
        )
        machines = machines_result.scalars().all()

        running = sum(1 for m in machines if m.status == "running")
        stopped = sum(1 for m in machines if m.status == "stopped")
        maintenance = sum(1 for m in machines if m.status == "maintenance")

        # 2. Produção do dia
        today = date.today()
        prod_result = await db.execute(
            select(
                func.sum(ProductionEntry.quantity_good).label("good"),
                func.sum(ProductionEntry.quantity_rejected).label("rej"),
            ).where(func.date(ProductionEntry.timestamp) == today)
        )
        prod_row = prod_result.one()
        total_good = prod_row.good or 0
        total_rej = prod_row.rej or 0
        total_prod = total_good + total_rej
        scrap_rate = round((total_rej / total_prod * 100) if total_prod > 0 else 0, 2)

        # 3. OEE médio do dia
        oee_result = await db.execute(
            select(func.avg(OeeHistory.oee)).where(OeeHistory.date == today)
        )
        oee_avg = round(oee_result.scalar() or 0, 1)

        # 4. Ordens ativas
        orders_result = await db.execute(
            select(
                func.count(case((ProductionOrder.status == "in_progress", 1))).label("active"),
                func.count(case((ProductionOrder.status == "planned", 1))).label("planned"),
            )
        )
        orders_row = orders_result.one()

        # 5. Paradas ativas — top reason
        dt_result = await db.execute(
            select(ActiveDowntime.reason, func.count(ActiveDowntime.id).label("cnt"))
            .group_by(ActiveDowntime.reason)
            .order_by(func.count(ActiveDowntime.id).desc())
            .limit(1)
        )
        top_dt = dt_result.first()

        # 6. Cards de máquina
        machine_cards = []
        for m in machines:
            # produção do dia por máquina
            mc_prod = await db.execute(
                select(
                    func.sum(ProductionEntry.quantity_good).label("good"),
                    func.sum(ProductionEntry.quantity_rejected).label("rej"),
                ).where(
                    ProductionEntry.machine_id == m.id,
                    func.date(ProductionEntry.timestamp) == today,
                )
            )
            mc_row = mc_prod.one()

            # parada ativa
            active_dt = await db.execute(
                select(ActiveDowntime.reason).where(
                    ActiveDowntime.machine_id == m.id
                ).limit(1)
            )
            dt_reason = active_dt.scalar_one_or_none()

            machine_cards.append(MachineCardData(
                code=m.code,
                name=m.name,
                status=m.status,
                current_product=m.current_product,
                current_operator=m.current_operator,
                oee=m.efficiency,
                efficiency=m.efficiency,
                cycle_time=m.cycle_time_seconds,
                produced_today=mc_row.good or 0,
                rejected_today=mc_row.rej or 0,
                active_downtime_reason=dt_reason,
            ))

        return DashboardSummary(
            total_machines=len(machines),
            machines_running=running,
            machines_stopped=stopped,
            machines_maintenance=maintenance,
            oee_average=oee_avg,
            total_produced_today=total_good,
            total_rejected_today=total_rej,
            scrap_rate=scrap_rate,
            active_orders=orders_row.active,
            planned_orders=orders_row.planned,
            top_downtime_reason=top_dt.reason if top_dt else None,
            machines=machine_cards,
        )
