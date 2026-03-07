"""
Model: User — Usuários do sistema com RBAC
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="operador")  # admin, supervisor, operador, qualidade, pcp
    is_active = Column(Boolean, default=True)
    custom_claims = Column(JSON, default=dict)  # {role, permissions[], sector}
    sector = Column(String(100), default="producao")
    avatar_initials = Column(String(5), default="US")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User {self.email} role={self.role}>"
