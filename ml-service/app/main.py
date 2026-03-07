"""
Synchro MES — ML Service
Entry point: uvicorn app.main:app --reload --port 8001
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🧠 {settings.app_title} v{settings.app_version} — Iniciando...")
    print(f"✅ ML Service pronto — porta 8001")
    yield
    print("🛑 ML Service encerrando...")


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="Serviço de Machine Learning para predições industriais (OEE, Paradas, Qualidade, Manutenção)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
from app.routers.predictions import router as predictions_router
from app.routers.training import router as training_router

app.include_router(predictions_router)
app.include_router(training_router)


@app.get("/")
async def root():
    return {
        "service": settings.app_title,
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "predictions": "/predictions/{oee,downtime,quality,maintenance}",
            "training": "/ml/{train,train-all,health}",
        },
    }
