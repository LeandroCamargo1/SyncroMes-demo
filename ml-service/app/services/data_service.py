"""
Serviço de acesso a dados para o ML Service.
Lê dados do banco principal (PostgreSQL) para alimentar os modelos.
"""
import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DataService:
    """Consultas SQL otimizadas para extração de features ML."""

    # ── OEE ───────────────────────────────────────────────────

    @staticmethod
    async def get_oee_history(db: AsyncSession, machine_code: str | None = None, limit: int = 500) -> pd.DataFrame:
        query = """
            SELECT machine_code, date, shift, availability, performance,
                   quality_rate, oee, planned_time_minutes, running_time_minutes,
                   downtime_minutes, total_produced, good_produced, rejected,
                   ideal_cycle_seconds, actual_cycle_seconds
            FROM oee_history
        """
        params: dict = {"limit": limit}
        if machine_code:
            query += " WHERE machine_code = :mc"
            params["mc"] = machine_code
        query += " ORDER BY date DESC LIMIT :limit"

        result = await db.execute(text(query), params)
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=result.keys())

    # ── Downtime ──────────────────────────────────────────────

    @staticmethod
    async def get_downtime_history(db: AsyncSession, machine_code: str | None = None, limit: int = 1000) -> pd.DataFrame:
        query = """
            SELECT machine_code, reason, category, subcategory, shift,
                   start_time, end_time, duration_minutes, is_planned
            FROM downtime_history
        """
        params: dict = {"limit": limit}
        if machine_code:
            query += " WHERE machine_code = :mc"
            params["mc"] = machine_code
        query += " ORDER BY start_time DESC LIMIT :limit"

        result = await db.execute(text(query), params)
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=result.keys())

    @staticmethod
    async def get_active_downtimes(db: AsyncSession) -> pd.DataFrame:
        result = await db.execute(text(
            "SELECT machine_code, reason, category, start_time FROM active_downtimes"
        ))
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=result.keys())

    # ── Quality ───────────────────────────────────────────────

    @staticmethod
    async def get_quality_data(db: AsyncSession, machine_code: str | None = None, limit: int = 1000) -> pd.DataFrame:
        query = """
            SELECT machine_code, product_code, dimension_name,
                   nominal_value, measured_value, tolerance_upper, tolerance_lower,
                   is_approved, defect_type, defect_severity, timestamp
            FROM quality_measurements
        """
        params: dict = {"limit": limit}
        if machine_code:
            query += " WHERE machine_code = :mc"
            params["mc"] = machine_code
        query += " ORDER BY timestamp DESC LIMIT :limit"

        result = await db.execute(text(query), params)
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=result.keys())

    @staticmethod
    async def get_spc_data(db: AsyncSession, machine_code: str | None = None, limit: int = 500) -> pd.DataFrame:
        query = """
            SELECT machine_code, product_code, parameter_name, value,
                   ucl, lcl, target, is_out_of_control, timestamp
            FROM spc_data
        """
        params: dict = {"limit": limit}
        if machine_code:
            query += " WHERE machine_code = :mc"
            params["mc"] = machine_code
        query += " ORDER BY timestamp DESC LIMIT :limit"

        result = await db.execute(text(query), params)
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=result.keys())

    @staticmethod
    async def get_loss_data(db: AsyncSession, machine_code: str | None = None, limit: int = 1000) -> pd.DataFrame:
        query = """
            SELECT machine_code, product_code, quantity, weight_kg,
                   reason, category, shift, timestamp
            FROM loss_entries
        """
        params: dict = {"limit": limit}
        if machine_code:
            query += " WHERE machine_code = :mc"
            params["mc"] = machine_code
        query += " ORDER BY timestamp DESC LIMIT :limit"

        result = await db.execute(text(query), params)
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=result.keys())

    # ── Mold / Maintenance ────────────────────────────────────

    @staticmethod
    async def get_molds(db: AsyncSession, mold_code: str | None = None) -> pd.DataFrame:
        query = """
            SELECT code, name, cavities, cycle_time_ideal, status,
                   total_cycles, max_cycles, last_maintenance, weight_grams
            FROM molds
        """
        params: dict = {}
        if mold_code:
            query += " WHERE code = :mc"
            params["mc"] = mold_code
        query += " ORDER BY code"

        result = await db.execute(text(query), params)
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=result.keys())

    @staticmethod
    async def get_mold_maintenances(db: AsyncSession, mold_code: str | None = None, limit: int = 500) -> pd.DataFrame:
        query = """
            SELECT mold_code, maintenance_type, start_time, end_time,
                   duration_hours, cost, status
            FROM mold_maintenances
        """
        params: dict = {"limit": limit}
        if mold_code:
            query += " WHERE mold_code = :mc"
            params["mc"] = mold_code
        query += " ORDER BY start_time DESC LIMIT :limit"

        result = await db.execute(text(query), params)
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=result.keys())

    # ── Production ────────────────────────────────────────────

    @staticmethod
    async def get_production_entries(db: AsyncSession, machine_code: str | None = None, limit: int = 1000) -> pd.DataFrame:
        query = """
            SELECT machine_code, product_code, shift, quantity_good,
                   quantity_rejected, cycle_time_actual, cycle_time_ideal,
                   cavities, material, timestamp
            FROM production_entries
        """
        params: dict = {"limit": limit}
        if machine_code:
            query += " WHERE machine_code = :mc"
            params["mc"] = machine_code
        query += " ORDER BY timestamp DESC LIMIT :limit"

        result = await db.execute(text(query), params)
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=result.keys())

    # ── Machines ──────────────────────────────────────────────

    @staticmethod
    async def get_machines(db: AsyncSession) -> pd.DataFrame:
        result = await db.execute(text(
            "SELECT code, name, type, tonnage, status, cycle_time_seconds, "
            "cavities, efficiency, is_active FROM machines WHERE is_active = true"
        ))
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=result.keys())
