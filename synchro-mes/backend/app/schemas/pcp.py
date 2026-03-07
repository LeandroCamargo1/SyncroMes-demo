"""
Schemas: PCP (Planning & Control)
"""
from pydantic import BaseModel
from datetime import datetime


class PcpMessageCreate(BaseModel):
    message: str
    priority: int = 0
    type: str = "info"
    target_machine: str | None = None
    created_by: str | None = None
    expires_at: datetime | None = None


class PcpMessageRead(BaseModel):
    id: int
    message: str
    priority: int
    type: str
    target_machine: str | None = None
    is_active: bool
    created_by: str | None = None
    expires_at: datetime | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
