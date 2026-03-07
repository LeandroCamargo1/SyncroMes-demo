"""
AuthService — Autenticação JWT + hashing de senhas
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import get_settings
from app.database import get_db
from app.models.user import User

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# ── DEV MODE: bypass de autenticação ─────────────────────────
# Usuário admin fictício para desenvolvimento (sem login)
_DEV_BYPASS = True


class _DevUser:
    """Objeto que simula um User do SQLAlchemy para dev sem login."""
    id = 1
    email = "admin@synchro.dev"
    name = "Admin Dev"
    role = "admin"
    is_active = True
    custom_claims = {"role": "admin", "permissions": [
        "dashboard", "production", "quality", "downtimes", "planning",
        "orders", "launch", "analysis", "pmp", "history", "reports",
        "admin", "leadership", "setup", "tooling", "pcp", "machines",
    ]}
    sector = "producao"
    avatar_initials = "AD"
    created_at = None
    updated_at = None
    last_login = None


class AuthService:

    # ── Password ──────────────────────────────────────────────
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    # ── JWT ───────────────────────────────────────────────────
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # ── Authenticate  ────────────────────────────────────────
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not AuthService.verify_password(password, user.hashed_password):
            return None
        # Atualizar last_login
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
        return user

    # ── Current User (Dependency) ─────────────────────────────
    @staticmethod
    async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        # DEV BYPASS — retorna admin sem verificar token
        if _DEV_BYPASS:
            return _DevUser()

        payload = AuthService.decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail="Usuário não encontrado ou inativo")
        return user

    @staticmethod
    def require_role(*roles: str):
        """Dependency factory — restringe acesso por role."""
        async def role_checker(
            current_user: User = Depends(AuthService.get_current_user),
        ) -> User:
            # DEV BYPASS — permite tudo
            if _DEV_BYPASS:
                return current_user
            if current_user.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acesso restrito. Roles permitidas: {', '.join(roles)}",
                )
            return current_user
        return role_checker
