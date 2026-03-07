"""
Model: SystemLog — Logs de auditoria do sistema
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SystemLog(Base):
    __tablename__ = "system_logs"

    action = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    user_name = Column(String(150), nullable=True)
    entity_type = Column(String(50), nullable=True, index=True)
    entity_id = Column(Integer, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(300), nullable=True)
    module = Column(String(50), nullable=True)

    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # ── Relationships ─────────────────────────────────────
    user = relationship("User", back_populates="system_logs", lazy="joined")

    def __repr__(self):
        return f"<SystemLog {self.action} user={self.user_email}>"
