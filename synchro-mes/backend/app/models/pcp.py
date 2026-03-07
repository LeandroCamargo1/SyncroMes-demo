"""
Model: PcpMessage — Mensagens do PCP para Dashboard TV
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import PcpMessageType


class PcpMessage(Base):
    __tablename__ = "pcp_messages"

    message = Column(String(500), nullable=False)
    priority = Column(Integer, default=0)
    type = Column(Enum(PcpMessageType), default=PcpMessageType.info, nullable=False)
    target_machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # ── Relationships ─────────────────────────────────────
    target_machine_rel = relationship("Machine", lazy="joined")

    @property
    def target_machine(self) -> str | None:
        return self.target_machine_rel.code if self.target_machine_rel else None

    def __repr__(self):
        return f"<PcpMessage priority={self.priority} active={self.is_active}>"
