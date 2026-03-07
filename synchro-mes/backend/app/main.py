"""
Synchro MES — Backend FastAPI
Entry point: uvicorn app.main:app --reload
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db, AsyncSessionLocal
from app.routers import all_routers
from app.seed.seed_data import seed_all
from app.services.websocket_manager import ws_manager
from app.services.audit_middleware import AuditMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: cria tabelas + seed | Shutdown: cleanup."""
    # ── Startup ───────────────────────────────────────────────
    print(f"🚀 {settings.app_title} v{settings.app_version} — Iniciando...")
    await init_db()
    async with AsyncSessionLocal() as db:
        await seed_all(db)
    print(f"✅ API pronta — {settings.app_title}")
    yield
    # ── Shutdown ──────────────────────────────────────────────
    print("🛑 Encerrando servidor...")


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="Sistema MES (Manufacturing Execution System) para indústria de injeção plástica",
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

# ── Audit Middleware ──────────────────────────────────────────
app.add_middleware(AuditMiddleware)

# ── Routers ───────────────────────────────────────────────────
for router, prefix, tags in all_routers:
    app.include_router(router, prefix=prefix, tags=tags)


# ── WebSocket ─────────────────────────────────────────────────
@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str = "dashboard"):
    """WebSocket para atualizações em tempo real.
    Canais: dashboard, machine:INJ-01, notifications, etc.
    """
    await ws_manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            # Pode processar mensagens do cliente aqui (ex: ping)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel)


# ── Health Check ──────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "app": settings.app_title,
        "version": settings.app_version,
        "ws_connections": ws_manager.active_connections_count,
    }
