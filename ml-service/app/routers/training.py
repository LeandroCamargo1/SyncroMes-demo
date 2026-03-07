"""
Router de treinamento e status dos modelos ML.
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.data_service import DataService
from app.schemas.predictions import (
    TrainingRequest, TrainingResponse,
    HealthResponse, ModelStatus,
)
from app.models.oee_predictor import OeePredictor
from app.models.downtime_predictor import DowntimePredictor
from app.models.quality_predictor import QualityPredictor
from app.models.maintenance_predictor import MaintenancePredictor

router = APIRouter(prefix="/ml", tags=["ML Management"])

_oee = OeePredictor()
_downtime = DowntimePredictor()
_quality = QualityPredictor()
_maintenance = MaintenancePredictor()

_predictors = {
    "oee": _oee,
    "downtime": _downtime,
    "quality": _quality,
    "maintenance": _maintenance,
}


@router.post("/train", response_model=TrainingResponse)
async def train_model(req: TrainingRequest, db: AsyncSession = Depends(get_db)):
    """Treina ou re-treina um modelo específico."""
    if req.model_type not in _predictors:
        return TrainingResponse(
            model_type=req.model_type,
            status="error",
            samples_used=0,
            metrics={},
            trained_at=datetime.now(),
            message=f"Modelo '{req.model_type}' não encontrado. Use: {list(_predictors.keys())}",
        )

    if req.model_type == "oee":
        df = await DataService.get_oee_history(db, machine_code=req.machine_code, limit=5000)
        result = _oee.train(df)
    elif req.model_type == "downtime":
        df = await DataService.get_downtime_history(db, machine_code=req.machine_code, limit=5000)
        result = _downtime.train(df)
    elif req.model_type == "quality":
        quality_df = await DataService.get_quality_data(db, machine_code=req.machine_code, limit=5000)
        loss_df = await DataService.get_loss_data(db, machine_code=req.machine_code, limit=5000)
        prod_df = await DataService.get_production_entries(db, machine_code=req.machine_code, limit=5000)
        result = _quality.train(quality_df, loss_df, prod_df)
    else:  # maintenance
        molds_df = await DataService.get_molds(db)
        maint_df = await DataService.get_mold_maintenances(db, limit=5000)
        result = _maintenance.train(molds_df, maint_df)

    return TrainingResponse(
        model_type=req.model_type,
        status=result.get("status", "unknown"),
        samples_used=result.get("samples", 0),
        metrics=result.get("metrics", {}),
        trained_at=datetime.now(),
        message=f"Modelo '{req.model_type}' — {result.get('status', 'unknown')}",
    )


@router.post("/train-all")
async def train_all_models(db: AsyncSession = Depends(get_db)):
    """Treina todos os modelos de uma vez."""
    results = {}
    for model_type in _predictors:
        req = TrainingRequest(model_type=model_type)
        resp = await train_model(req, db)
        results[model_type] = {"status": resp.status, "samples": resp.samples_used}
    return {"message": "Treinamento completo", "results": results}


@router.get("/health", response_model=HealthResponse)
async def ml_health(db: AsyncSession = Depends(get_db)):
    """Status de saúde e métricas dos modelos."""
    from app.config import get_settings
    settings = get_settings()

    models_status = []
    for name, predictor in _predictors.items():
        # Conta de amostras no banco
        sample_count = 0
        if name == "oee":
            df = await DataService.get_oee_history(db, limit=1)
            sample_count = predictor.samples_used
        elif name == "downtime":
            sample_count = predictor.samples_used
        elif name == "quality":
            sample_count = predictor.samples_used
        else:
            sample_count = predictor.samples_used

        accuracy = None
        if predictor.metrics:
            accuracy = list(predictor.metrics.values())[0] if predictor.metrics else None
            if isinstance(accuracy, dict):
                accuracy = list(accuracy.values())[0] if accuracy else None

        models_status.append(ModelStatus(
            model_type=name,
            is_trained=predictor.is_trained,
            last_trained=predictor.last_trained,
            samples_count=sample_count,
            accuracy_metric=accuracy,
        ))

    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        models=models_status,
    )
