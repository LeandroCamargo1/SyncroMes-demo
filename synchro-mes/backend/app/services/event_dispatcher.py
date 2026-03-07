"""
EventDispatcher — Domain events + WebSocket broadcast + auto-notifications.

Centraliza disparos de eventos do sistema. Cada mutation relevante
chama dispatcher.emit() e o dispatcher:
  1. Grava Notification no banco (quando aplicavel)
  2. Faz broadcast WS para canais relevantes
"""
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.enums import NotificationType
from app.services.websocket_manager import ws_manager


class EventDispatcher:

    # ── helpers ────────────────────────────────────────────────

    @staticmethod
    async def _save_notification(
        db: AsyncSession,
        title: str,
        message: str,
        ntype: NotificationType = NotificationType.info,
        machine_id: int | None = None,
        target_role: str | None = None,
        link: str | None = None,
    ) -> Notification:
        notif = Notification(
            title=title,
            message=message,
            type=ntype,
            machine_id=machine_id,
            target_role=target_role,
            link=link,
        )
        db.add(notif)
        await db.flush()
        return notif

    @staticmethod
    async def _broadcast(channel: str, event_type: str, payload: dict):
        await ws_manager.broadcast(channel, {"type": event_type, "data": payload})

    # ── Dashboard refresh ─────────────────────────────────────

    @staticmethod
    async def dashboard_changed():
        """Notifica clientes do dashboard que os dados mudaram."""
        await ws_manager.broadcast("dashboard", {
            "type": "dashboard:refresh",
            "ts": datetime.now(timezone.utc).isoformat(),
        })

    # ── Production events ─────────────────────────────────────

    @staticmethod
    async def order_created(db: AsyncSession, order_number: str, product_name: str):
        await EventDispatcher._save_notification(
            db,
            title="Nova ordem criada",
            message=f"Ordem {order_number} — {product_name}",
            ntype=NotificationType.info,
            target_role="pcp",
            link="/orders",
        )
        await EventDispatcher._broadcast("notifications", "order:created", {
            "order_number": order_number,
            "product_name": product_name,
        })
        await EventDispatcher.dashboard_changed()

    @staticmethod
    async def order_status_changed(db: AsyncSession, order_number: str, old_status: str, new_status: str):
        ntype = NotificationType.success if new_status == "completed" else NotificationType.info
        await EventDispatcher._save_notification(
            db,
            title=f"Ordem {order_number} — {new_status}",
            message=f"Status alterado de {old_status} para {new_status}",
            ntype=ntype,
            target_role="pcp",
            link="/orders",
        )
        await EventDispatcher._broadcast("notifications", "order:status", {
            "order_number": order_number,
            "status": new_status,
        })
        await EventDispatcher.dashboard_changed()

    @staticmethod
    async def production_entry_created(db: AsyncSession, machine_code: str, qty_good: int, qty_rejected: int):
        await EventDispatcher._broadcast(f"machine:{machine_code}", "production:entry", {
            "machine_code": machine_code,
            "qty_good": qty_good,
            "qty_rejected": qty_rejected,
        })
        await EventDispatcher.dashboard_changed()

    # ── Downtime events ───────────────────────────────────────

    @staticmethod
    async def downtime_started(db: AsyncSession, machine_code: str, reason: str, machine_id: int | None = None):
        await EventDispatcher._save_notification(
            db,
            title=f"Parada — {machine_code}",
            message=f"Motivo: {reason}",
            ntype=NotificationType.warning,
            machine_id=machine_id,
            target_role="supervisor",
            link="/downtimes",
        )
        await EventDispatcher._broadcast(f"machine:{machine_code}", "downtime:started", {
            "machine_code": machine_code,
            "reason": reason,
        })
        await EventDispatcher._broadcast("notifications", "downtime:started", {
            "machine_code": machine_code,
            "reason": reason,
        })
        await EventDispatcher.dashboard_changed()

    @staticmethod
    async def downtime_stopped(db: AsyncSession, machine_code: str, duration_minutes: float):
        await EventDispatcher._broadcast(f"machine:{machine_code}", "downtime:stopped", {
            "machine_code": machine_code,
            "duration_minutes": duration_minutes,
        })
        await EventDispatcher.dashboard_changed()

    # ── Machine events ────────────────────────────────────────

    @staticmethod
    async def machine_status_changed(db: AsyncSession, machine_code: str, old_status: str, new_status: str, machine_id: int | None = None):
        if new_status == "maintenance":
            await EventDispatcher._save_notification(
                db,
                title=f"{machine_code} em manutenção",
                message=f"Status alterado de {old_status} para manutenção",
                ntype=NotificationType.warning,
                machine_id=machine_id,
                target_role="supervisor",
                link="/admin",
            )
        await EventDispatcher._broadcast(f"machine:{machine_code}", "machine:status", {
            "machine_code": machine_code,
            "status": new_status,
        })
        await EventDispatcher.dashboard_changed()

    # ── Quality events ────────────────────────────────────────

    @staticmethod
    async def quality_alert(db: AsyncSession, machine_code: str, defect_type: str, machine_id: int | None = None):
        await EventDispatcher._save_notification(
            db,
            title=f"Alerta de qualidade — {machine_code}",
            message=f"Defeito: {defect_type}",
            ntype=NotificationType.error,
            machine_id=machine_id,
            target_role="qualidade",
            link="/quality",
        )
        await EventDispatcher._broadcast("notifications", "quality:alert", {
            "machine_code": machine_code,
            "defect_type": defect_type,
        })

    # ── Stock events ──────────────────────────────────────────

    @staticmethod
    async def stock_below_minimum(db: AsyncSession, material_code: str, current: float, minimum: float):
        await EventDispatcher._save_notification(
            db,
            title=f"Estoque baixo — {material_code}",
            message=f"Atual: {current:.1f} | Mínimo: {minimum:.1f}",
            ntype=NotificationType.warning,
            target_role="pcp",
            link="/materials",
        )
        await EventDispatcher._broadcast("notifications", "stock:low", {
            "material_code": material_code,
            "current": current,
            "minimum": minimum,
        })


dispatcher = EventDispatcher()
