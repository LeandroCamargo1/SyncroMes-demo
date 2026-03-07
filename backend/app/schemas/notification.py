"""
Schemas: Notification — CRUD de notificações do sistema
"""
from datetime import datetime
from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: int
    title: str
    message: str
    type: str
    target_role: str | None = None
    is_read: bool = False
    machine_code: str | None = None
    link: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class NotificationMarkRead(BaseModel):
    ids: list[int]
