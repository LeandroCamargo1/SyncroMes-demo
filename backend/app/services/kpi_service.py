"""
KpiService — ISO-22400 Advanced KPIs
Calcula métricas avançadas: TEEP, NEE, MTBF, MTTR, Setup Ratio,
First Pass Yield, Throughput Rate, Worker Efficiency.
"""
from datetime import date, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.oee import OeeHistory
from app.models.machine import Machine
from app.models.downtime import DowntimeHistory
from app.models.setup import SetupEntry
from app.models.production import ProductionEntry
from app.models.quality import QualityMeasurement
from app.models.loss import LossEntry
from app.models.machine_maintenance import MachineMaintenance
from app.models.enums import DowntimeCategory


class KpiService:

    @staticmethod
    async def get_advanced_kpis(
        db: AsyncSession,
        machine_code: str | None = None,
        period_days: int = 1,
    ) -> dict:
        """Calcula KPIs avançados ISO-22400 para uma máquina ou fábrica."""
        target_start = date.today() - timedelta(days=period_days - 1)
        target_end = date.today()

        # ── OEE base data ────────────────────────────────
        oee_q = select(
            func.avg(OeeHistory.oee).label("avg_oee"),
            func.avg(OeeHistory.availability).label("avg_avail"),
            func.avg(OeeHistory.performance).label("avg_perf"),
            func.avg(OeeHistory.quality_rate).label("avg_quality"),
            func.sum(OeeHistory.planned_time_minutes).label("total_planned"),
            func.sum(OeeHistory.running_time_minutes).label("total_running"),
            func.sum(OeeHistory.downtime_minutes).label("total_downtime"),
            func.sum(OeeHistory.total_produced).label("total_produced"),
            func.sum(OeeHistory.good_produced).label("total_good"),
            func.sum(OeeHistory.rejected).label("total_rejected"),
        ).where(OeeHistory.date.between(target_start, target_end))

        if machine_code:
            oee_q = oee_q.join(OeeHistory.machine).where(Machine.code == machine_code)

        oee_result = await db.execute(oee_q)
        oee = oee_result.one()

        avg_oee = float(oee.avg_oee or 0)
        avg_avail = float(oee.avg_avail or 0)
        avg_perf = float(oee.avg_perf or 0)
        avg_quality = float(oee.avg_quality or 0)
        total_planned = float(oee.total_planned or 0)
        total_running = float(oee.total_running or 0)
        total_produced = int(oee.total_produced or 0)
        total_good = int(oee.total_good or 0)
        total_rejected = int(oee.total_rejected or 0)

        # ── TEEP: Total Effective Equipment Performance ───
        # TEEP = OEE × (planned_time / calendar_time)
        calendar_minutes = period_days * 24 * 60
        loading_ratio = total_planned / calendar_minutes if calendar_minutes > 0 else 0
        teep = avg_oee * loading_ratio / 100 if avg_oee > 0 else 0

        # ── NEE: Net Equipment Effectiveness ──────────────
        # NEE = Availability × Performance (sem qualidade)
        nee = (avg_avail * avg_perf) / 100 if avg_avail > 0 and avg_perf > 0 else 0

        # ── Setup Ratio ───────────────────────────────────
        setup_q = select(
            func.sum(SetupEntry.duration_minutes).label("total_setup")
        ).where(SetupEntry.start_time >= str(target_start))
        if machine_code:
            setup_q = setup_q.join(SetupEntry.machine).where(Machine.code == machine_code)
        setup_result = await db.execute(setup_q)
        total_setup = float(setup_result.scalar_one() or 0)
        setup_ratio = (total_setup / total_planned * 100) if total_planned > 0 else 0

        # ── Scrap Rate ────────────────────────────────────
        scrap_rate = (total_rejected / total_produced * 100) if total_produced > 0 else 0

        # ── First Pass Yield ──────────────────────────────
        first_pass_yield = (total_good / total_produced * 100) if total_produced > 0 else 0

        # ── Throughput Rate (peças/hora) ──────────────────
        running_hours = total_running / 60 if total_running > 0 else 0
        throughput_rate = total_good / running_hours if running_hours > 0 else 0

        # ── Worker Efficiency ─────────────────────────────
        # Simplificado: good_produced / total_produced
        worker_efficiency = first_pass_yield

        # ── MTBF: Mean Time Between Failures ──────────────
        failure_q = select(func.count(DowntimeHistory.id).label("failure_count")).where(
            DowntimeHistory.start_time >= str(target_start),
            DowntimeHistory.is_planned == False,
        )
        if machine_code:
            failure_q = failure_q.join(DowntimeHistory.machine).where(Machine.code == machine_code)
        failure_result = await db.execute(failure_q)
        failure_count = int(failure_result.scalar_one() or 0)
        mtbf_hours = running_hours / failure_count if failure_count > 0 else running_hours

        # ── MTTR: Mean Time To Repair ─────────────────────
        repair_q = select(
            func.avg(DowntimeHistory.duration_minutes).label("avg_repair")
        ).where(
            DowntimeHistory.start_time >= str(target_start),
            DowntimeHistory.is_planned == False,
        )
        if machine_code:
            repair_q = repair_q.join(DowntimeHistory.machine).where(Machine.code == machine_code)
        repair_result = await db.execute(repair_q)
        avg_repair_minutes = float(repair_result.scalar_one() or 0)
        mttr_hours = avg_repair_minutes / 60

        return {
            "oee": round(avg_oee, 2),
            "availability": round(avg_avail, 2),
            "performance": round(avg_perf, 2),
            "quality_rate": round(avg_quality, 2),
            "teep": round(teep, 2),
            "nee": round(nee, 2),
            "setup_ratio": round(setup_ratio, 2),
            "scrap_rate": round(scrap_rate, 2),
            "first_pass_yield": round(first_pass_yield, 2),
            "throughput_rate": round(throughput_rate, 2),
            "worker_efficiency": round(worker_efficiency, 2),
            "mtbf_hours": round(mtbf_hours, 2),
            "mttr_hours": round(mttr_hours, 2),
            "machine_code": machine_code,
            "period_days": period_days,
        }
