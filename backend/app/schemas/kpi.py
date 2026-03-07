"""
Schemas: KPI — ISO-22400 Advanced KPIs
"""
from pydantic import BaseModel


class AdvancedKpiResponse(BaseModel):
    """KPIs avançados ISO-22400 para uma máquina ou fábrica."""
    # OEE components
    oee: float = 0
    availability: float = 0
    performance: float = 0
    quality_rate: float = 0

    # Extended KPIs
    teep: float = 0          # Total Effective Equipment Performance
    nee: float = 0           # Net Equipment Effectiveness
    setup_ratio: float = 0   # % do tempo em setup
    scrap_rate: float = 0    # % refugo
    first_pass_yield: float = 0  # % aprovado na 1a passada
    throughput_rate: float = 0   # peças/hora efetivas
    worker_efficiency: float = 0  # comparação operador vs ideal

    # Maintenance KPIs
    mtbf_hours: float = 0    # Mean Time Between Failures
    mttr_hours: float = 0    # Mean Time To Repair

    # Context
    machine_code: str | None = None
    period_days: int = 1

    model_config = {"from_attributes": True}
