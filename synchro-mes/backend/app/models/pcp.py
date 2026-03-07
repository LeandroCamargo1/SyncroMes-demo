"""
Model: PcpMessage — Mensagens do PCP para Dashboard TV
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class PcpMessage(Base):
    __tablename__ = "pcp_messages"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(500), nullable=False)
    priority = Column(Integer, default=0)  # 0-5
    type = Column(String(30), default="info")  # info, warning, urgent
    target_machine = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<PcpMessage priority={self.priority} active={self.is_active}>"
