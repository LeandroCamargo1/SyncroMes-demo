"""
Synchro MES — Conexão assíncrona com banco de dados (SQLAlchemy 2.0 async)
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool
from app.config import get_settings

settings = get_settings()

_is_sqlite = settings.database_url.startswith("sqlite")

_engine_kwargs = {
    "echo": settings.debug,
}
if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    _engine_kwargs["poolclass"] = StaticPool
else:
    _engine_kwargs["pool_size"] = 20
    _engine_kwargs["max_overflow"] = 10

engine = create_async_engine(settings.database_url, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Classe-base para todos os models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency injection — fornece sessão do banco por request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Cria todas as tabelas (útil para dev/demo)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
