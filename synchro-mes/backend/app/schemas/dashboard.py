"""
Schemas: Dashboard — dados agregados para o painel principal
"""
from pydantic import BaseModel


class MachineCardData(BaseModel):
    """Card de máquina no dashboard (grid de máquinas)."""
    code: str
    name: str
    status: str                       # running, stopped, maintenance, setup
    current_product: str | None = None
    current_operator: str | None = None
    oee: float = 0.0
    efficiency: float = 0.0
    cycle_time: float | None = None
    produced_today: int = 0
    rejected_today: int = 0
    downtime_minutes_today: float = 0.0
    active_downtime_reason: str | None = None


class DashboardSummary(BaseModel):
    """Resumo geral da fábrica para o topo do dashboard."""
    total_machines: int
    machines_running: int
    machines_stopped: int
    machines_maintenance: int
    oee_average: float
    total_produced_today: int
    total_rejected_today: int
    scrap_rate: float
    active_orders: int
    planned_orders: int
    top_downtime_reason: str | None = None
    machines: list[MachineCardData] = []
