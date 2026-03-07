"""
Model: SystemLog — Logs de auditoria do sistema
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # login, logout, lancamento_producao, etc.
    user_email = Column(String(255), nullable=True)
    user_name = Column(String(150), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(300), nullable=True)
    module = Column(String(50), nullable=True)  # producao, qualidade, paradas

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<SystemLog {self.action} user={self.user_email}>"
