"""
Schemas de predição para o ML Service.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime


# ── OEE Prediction ────────────────────────────────────────────

class OeePredictionRequest(BaseModel):
    machine_code: str = Field(..., example="INJ-01")
    horizon_days: int = Field(default=7, ge=1, le=30)


class OeeDailyForecast(BaseModel):
    date: date
    oee: float
    availability: float
    performance: float
    quality_rate: float
    confidence: float = Field(ge=0, le=1)


class OeePredictionResponse(BaseModel):
    machine_code: str
    generated_at: datetime
    model_used: str
    forecasts: list[OeeDailyForecast]
    trend: str = Field(description="up / stable / down")
    avg_predicted_oee: float


# ── Downtime Prediction ──────────────────────────────────────

class DowntimePredictionRequest(BaseModel):
    machine_code: str = Field(..., example="INJ-01")


class DowntimeRisk(BaseModel):
    category: str
    probability: float = Field(ge=0, le=1)
    avg_duration_minutes: float
    top_reason: str


class DowntimePredictionResponse(BaseModel):
    machine_code: str
    generated_at: datetime
    model_used: str
    overall_risk: float = Field(ge=0, le=1, description="Risco geral de parada nas próximas 24h")
    risk_level: str = Field(description="low / medium / high / critical")
    risks_by_category: list[DowntimeRisk]
    recommended_actions: list[str]


# ── Quality Prediction ────────────────────────────────────────

class QualityPredictionRequest(BaseModel):
    machine_code: str = Field(..., example="INJ-01")
    product_code: str | None = None


class DefectForecast(BaseModel):
    defect_type: str
    probability: float = Field(ge=0, le=1)
    expected_rate_pct: float


class QualityPredictionResponse(BaseModel):
    machine_code: str
    product_code: str | None
    generated_at: datetime
    model_used: str
    predicted_scrap_rate: float
    risk_level: str
    defect_forecasts: list[DefectForecast]
    spc_alerts: list[str]


# ── Mold Maintenance Prediction ──────────────────────────────

class MoldMaintenanceRequest(BaseModel):
    mold_code: str | None = None


class MoldHealthReport(BaseModel):
    mold_code: str
    mold_name: str
    current_cycles: int
    max_cycles: int | None
    cycle_usage_pct: float | None
    days_since_last_maintenance: int | None
    predicted_days_to_maintenance: int | None
    health_score: float = Field(ge=0, le=100)
    risk_level: str
    recommendation: str


class MoldMaintenanceResponse(BaseModel):
    generated_at: datetime
    model_used: str
    molds: list[MoldHealthReport]


# ── Training ─────────────────────────────────────────────────

class TrainingRequest(BaseModel):
    model_type: str = Field(..., description="oee / downtime / quality / maintenance")
    machine_code: str | None = None
    force_retrain: bool = False


class TrainingResponse(BaseModel):
    model_type: str
    status: str
    samples_used: int
    metrics: dict
    trained_at: datetime
    message: str


# ── Health ────────────────────────────────────────────────────

class ModelStatus(BaseModel):
    model_type: str
    is_trained: bool
    last_trained: datetime | None
    samples_count: int
    accuracy_metric: float | None


class HealthResponse(BaseModel):
    status: str
    version: str
    models: list[ModelStatus]
