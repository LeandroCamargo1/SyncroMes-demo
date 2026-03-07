"""
Model: Notification — Notificações do sistema
"""
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    title = Column(String(200), nullable=False)
    message = Column(String(500), nullable=False)
    type = Column(Enum(NotificationType), default=NotificationType.info, nullable=False)
    target_role = Column(String(50), nullable=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)
    link = Column(String(300), nullable=True)

    # ── Relationships ─────────────────────────────────────
    user = relationship("User", back_populates="notifications", lazy="joined")
    machine = relationship("Machine", back_populates="notifications", lazy="joined")

    @property
    def machine_code(self) -> str | None:
        return self.machine.code if self.machine else None

    def __repr__(self):
        return f"<Notification {self.title} type={self.type}>"
