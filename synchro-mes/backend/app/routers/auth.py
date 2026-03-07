"""
Router: Auth — Login, registro e perfil do usuário
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, Token, LoginRequest
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Autenticação — retorna JWT."""
    user = await AuthService.authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    token = AuthService.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    return Token(
        access_token=token,
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(AuthService.get_current_user)):
    """Dados do usuário autenticado."""
    return UserRead.model_validate(current_user)


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(AuthService.require_role("admin")),
):
    """Cadastro de novo usuário (só admin)."""
    from sqlalchemy import select
    exists = await db.execute(select(User).where(User.email == body.email))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    initials = "".join(w[0] for w in body.name.split()[:2]).upper()
    user = User(
        email=body.email,
        name=body.name,
        hashed_password=AuthService.hash_password(body.password),
        role=body.role,
        sector=body.sector,
        avatar_initials=initials,
        custom_claims={"role": body.role, "permissions": _get_permissions(body.role)},
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)


def _get_permissions(role: str) -> list[str]:
    perms = {
        "admin": ["dashboard", "producao", "qualidade", "paradas", "planejamento", "relatorios", "admin", "usuarios", "configuracoes"],
        "supervisor": ["dashboard", "producao", "qualidade", "paradas", "planejamento", "relatorios"],
        "operador": ["dashboard", "producao", "paradas"],
        "qualidade": ["dashboard", "qualidade", "relatorios"],
        "pcp": ["dashboard", "planejamento", "relatorios"],
    }
    return perms.get(role, ["dashboard"])
