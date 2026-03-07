"""
Model: User — Usuários do sistema com RBAC
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.operador)
    is_active = Column(Boolean, default=True)
    custom_claims = Column(JSON, default=dict)
    sector = Column(String(100), default="producao")
    avatar_initials = Column(String(5), default="US")

    last_login = Column(DateTime(timezone=True), nullable=True)

    # ── Relationships ─────────────────────────────────────
    system_logs = relationship("SystemLog", back_populates="user", lazy="noload")
    notifications = relationship("Notification", back_populates="user", lazy="noload")

    def __repr__(self):
        return f"<User {self.email} role={self.role}>"
