"""
DashboardService — Dados agregados para o painel principal
"""
from datetime import date, datetime, timezone
from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.machine import Machine
from app.models.production import ProductionEntry, ProductionOrder
from app.models.downtime import ActiveDowntime
from app.models.oee import OeeHistory
from app.schemas.dashboard import DashboardSummary, MachineCardData


class DashboardService:

    @staticmethod
    async def get_summary(db: AsyncSession) -> DashboardSummary:
        """Monta o resumo completo do dashboard — otimizado (sem N+1)."""

        today = date.today()

        # 1. Máquinas
        machines_result = await db.execute(
            select(Machine).where(Machine.is_active == True)
        )
        machines = machines_result.scalars().all()

        running = sum(1 for m in machines if m.status == "running")
        stopped = sum(1 for m in machines if m.status == "stopped")
        maintenance = sum(1 for m in machines if m.status == "maintenance")

        # 2. Produção do dia (total)
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

        # 6. Produção por máquina (batch — substitui N+1)
        per_machine_prod = await db.execute(
            select(
                ProductionEntry.machine_id,
                func.sum(ProductionEntry.quantity_good).label("good"),
                func.sum(ProductionEntry.quantity_rejected).label("rej"),
            )
            .where(func.date(ProductionEntry.timestamp) == today)
            .group_by(ProductionEntry.machine_id)
        )
        prod_by_machine = {r.machine_id: (r.good or 0, r.rej or 0) for r in per_machine_prod}

        # 7. Paradas ativas por máquina (batch — substitui N+1)
        active_dts = await db.execute(
            select(ActiveDowntime.machine_id, ActiveDowntime.reason)
        )
        dt_by_machine = {}
        for r in active_dts:
            if r.machine_id not in dt_by_machine:
                dt_by_machine[r.machine_id] = r.reason

        # 8. Montar machine_cards sem queries adicionais
        machine_cards = []
        for m in machines:
            good, rej = prod_by_machine.get(m.id, (0, 0))
            machine_cards.append(MachineCardData(
                code=m.code,
                name=m.name,
                status=m.status,
                current_product=m.current_product,
                current_operator=m.current_operator,
                oee=m.efficiency,
                efficiency=m.efficiency,
                cycle_time=m.cycle_time_seconds,
                produced_today=good,
                rejected_today=rej,
                active_downtime_reason=dt_by_machine.get(m.id),
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
