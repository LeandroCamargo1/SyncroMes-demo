"""
Model: Notification — Notificações do sistema
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(String(500), nullable=False)
    type = Column(String(30), default="info")    # info, warning, error, success
    target_role = Column(String(50), nullable=True)  # admin, supervisor, null=todos
    target_user_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, default=False)
    machine_code = Column(String(20), nullable=True)
    link = Column(String(300), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Notification {self.title} type={self.type}>"
