"""
WebSocket Manager — Tempo real para dashboard e máquinas
"""
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Gerencia conexões WebSocket por canal (dashboard, machine:INJ-01, etc.)."""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "dashboard"):
        await websocket.accept()
        if channel not in self._connections:
            self._connections[channel] = set()
        self._connections[channel].add(websocket)
        print(f"[WS] +1 conexão no canal '{channel}' (total: {len(self._connections[channel])})")

    def disconnect(self, websocket: WebSocket, channel: str = "dashboard"):
        if channel in self._connections:
            self._connections[channel].discard(websocket)
            if not self._connections[channel]:
                del self._connections[channel]

    async def broadcast(self, channel: str, data: dict):
        """Envia dados para todos os clientes de um canal."""
        if channel not in self._connections:
            return
        message = json.dumps(data, default=str)
        dead = []
        for ws in self._connections[channel]:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections[channel].discard(ws)

    async def broadcast_all(self, data: dict):
        """Envia dados para TODOS os canais."""
        for channel in list(self._connections.keys()):
            await self.broadcast(channel, data)

    @property
    def active_connections_count(self) -> int:
        return sum(len(conns) for conns in self._connections.values())


# Instância global
ws_manager = ConnectionManager()
