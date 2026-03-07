"""
Router de predições ML.
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.data_service import DataService
from app.schemas.predictions import (
    OeePredictionRequest, OeePredictionResponse, OeeDailyForecast,
    DowntimePredictionRequest, DowntimePredictionResponse, DowntimeRisk,
    QualityPredictionRequest, QualityPredictionResponse, DefectForecast,
    MoldMaintenanceRequest, MoldMaintenanceResponse, MoldHealthReport,
)
from app.models.oee_predictor import OeePredictor
from app.models.downtime_predictor import DowntimePredictor
from app.models.quality_predictor import QualityPredictor
from app.models.maintenance_predictor import MaintenancePredictor

router = APIRouter(prefix="/predictions", tags=["Predictions"])

# Singletons dos preditores
_oee = OeePredictor()
_downtime = DowntimePredictor()
_quality = QualityPredictor()
_maintenance = MaintenancePredictor()


@router.post("/oee", response_model=OeePredictionResponse)
async def predict_oee(req: OeePredictionRequest, db: AsyncSession = Depends(get_db)):
    """Prevê OEE para uma máquina nos próximos N dias."""
    df = await DataService.get_oee_history(db, machine_code=req.machine_code, limit=365)

    if df.empty:
        return OeePredictionResponse(
            machine_code=req.machine_code,
            generated_at=datetime.now(),
            model_used="gradient_boosting",
            forecasts=[],
            trend="stable",
            avg_predicted_oee=0,
        )

    # Auto-treina se necessário
    if not _oee.is_trained:
        all_data = await DataService.get_oee_history(db, limit=2000)
        _oee.train(all_data)

    forecasts_raw = _oee.predict(df, horizon_days=req.horizon_days)

    forecasts = [OeeDailyForecast(**f) for f in forecasts_raw]
    avg_oee = sum(f.oee for f in forecasts) / len(forecasts) if forecasts else 0

    return OeePredictionResponse(
        machine_code=req.machine_code,
        generated_at=datetime.now(),
        model_used="gradient_boosting",
        forecasts=forecasts,
        trend=_oee.get_trend(forecasts_raw),
        avg_predicted_oee=round(avg_oee, 1),
    )


@router.post("/downtime", response_model=DowntimePredictionResponse)
async def predict_downtime(req: DowntimePredictionRequest, db: AsyncSession = Depends(get_db)):
    """Prevê risco de parada para uma máquina nas próximas 24h."""
    df = await DataService.get_downtime_history(db, limit=2000)

    if df.empty:
        return DowntimePredictionResponse(
            machine_code=req.machine_code,
            generated_at=datetime.now(),
            model_used="random_forest",
            overall_risk=0,
            risk_level="low",
            risks_by_category=[],
            recommended_actions=[],
        )

    if not _downtime.is_trained:
        _downtime.train(df)

    result = _downtime.predict(df, req.machine_code)

    return DowntimePredictionResponse(
        machine_code=req.machine_code,
        generated_at=datetime.now(),
        model_used="random_forest",
        overall_risk=result["overall_risk"],
        risk_level=result["risk_level"],
        risks_by_category=[DowntimeRisk(**r) for r in result["risks"]],
        recommended_actions=result["actions"],
    )


@router.post("/quality", response_model=QualityPredictionResponse)
async def predict_quality(req: QualityPredictionRequest, db: AsyncSession = Depends(get_db)):
    """Prevê taxa de refugo e tipos de defeito."""
    quality_df = await DataService.get_quality_data(db, machine_code=req.machine_code)
    production_df = await DataService.get_production_entries(db, machine_code=req.machine_code)
    spc_df = await DataService.get_spc_data(db, machine_code=req.machine_code)

    if quality_df.empty and production_df.empty:
        return QualityPredictionResponse(
            machine_code=req.machine_code,
            product_code=req.product_code,
            generated_at=datetime.now(),
            model_used="gradient_boosting",
            predicted_scrap_rate=0,
            risk_level="unknown",
            defect_forecasts=[],
            spc_alerts=[],
        )

    if not _quality.is_trained:
        all_quality = await DataService.get_quality_data(db, limit=5000)
        all_loss = await DataService.get_loss_data(db, limit=5000)
        all_prod = await DataService.get_production_entries(db, limit=5000)
        _quality.train(all_quality, all_loss, all_prod)

    result = _quality.predict(production_df, spc_df, req.machine_code, req.product_code)

    return QualityPredictionResponse(
        machine_code=req.machine_code,
        product_code=req.product_code,
        generated_at=datetime.now(),
        model_used="gradient_boosting",
        predicted_scrap_rate=result["predicted_scrap_rate"],
        risk_level=result["risk_level"],
        defect_forecasts=[DefectForecast(**d) for d in result["defects"]],
        spc_alerts=result["spc_alerts"],
    )


@router.post("/maintenance", response_model=MoldMaintenanceResponse)
async def predict_maintenance(req: MoldMaintenanceRequest, db: AsyncSession = Depends(get_db)):
    """Prevê necessidade de manutenção para moldes."""
    molds_df = await DataService.get_molds(db, mold_code=req.mold_code)
    maint_df = await DataService.get_mold_maintenances(db, mold_code=req.mold_code)

    if molds_df.empty:
        return MoldMaintenanceResponse(
            generated_at=datetime.now(),
            model_used="random_forest + heuristics",
            molds=[],
        )

    if not _maintenance.is_trained:
        all_molds = await DataService.get_molds(db)
        all_maint = await DataService.get_mold_maintenances(db, limit=2000)
        _maintenance.train(all_molds, all_maint)

    reports = _maintenance.predict(molds_df, maint_df)

    return MoldMaintenanceResponse(
        generated_at=datetime.now(),
        model_used="random_forest + heuristics",
        molds=[MoldHealthReport(**r) for r in reports],
    )
