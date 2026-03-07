"""
Middleware de auditoria — registra todas as mutações (POST/PUT/PATCH/DELETE)
no SystemLog automaticamente.
"""
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.database import AsyncSessionLocal
from app.models.system_log import SystemLog

_MUTATION_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
_SKIP_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/api/auth/login"}


def _extract_module(path: str) -> str | None:
    """Extrai o módulo da rota, ex: /api/production/entries → production."""
    parts = path.strip("/").split("/")
    if len(parts) >= 2 and parts[0] == "api":
        return parts[1]
    return None


def _extract_entity(path: str) -> tuple[str | None, int | None]:
    """Extrai tipo de entidade e ID (se presente) da rota."""
    parts = path.strip("/").split("/")
    if len(parts) >= 3 and parts[0] == "api":
        entity_type = parts[2] if len(parts) > 2 else parts[1]
        entity_id = None
        for p in reversed(parts):
            if p.isdigit():
                entity_id = int(p)
                break
        return entity_type, entity_id
    return None, None


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in _MUTATION_METHODS:
            return await call_next(request)

        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        response = await call_next(request)

        # Só registra se a operação teve sucesso (2xx)
        if 200 <= response.status_code < 300:
            try:
                await self._log_mutation(request, response)
            except Exception:
                pass  # Não bloqueia a resposta por falha de log

        return response

    async def _log_mutation(self, request: Request, response: Response):
        method = request.method
        path = request.url.path
        module = _extract_module(path)
        entity_type, entity_id = _extract_entity(path)

        action_map = {
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }
        action = f"{action_map.get(method, method.lower())}:{entity_type or module or 'unknown'}"

        user_email = None
        user_name = None
        user_id = None
        if hasattr(request.state, "user"):
            user = request.state.user
            user_email = getattr(user, "email", None)
            user_name = getattr(user, "name", None)
            user_id = getattr(user, "id", None)

        client_host = request.client.host if request.client else None

        async with AsyncSessionLocal() as db:
            log = SystemLog(
                action=action,
                user_id=user_id if isinstance(user_id, int) else None,
                user_email=user_email,
                user_name=user_name,
                entity_type=entity_type,
                entity_id=entity_id,
                details={"method": method, "path": path, "status": response.status_code},
                ip_address=client_host,
                user_agent=request.headers.get("user-agent", "")[:300],
                module=module,
                timestamp=datetime.now(timezone.utc),
            )
            db.add(log)
            await db.commit()
