import type { WsMessage } from '../types';

type WsCallback = (data: WsMessage) => void;

/**
 * WebSocket service — conexão tempo real com o backend
 */
class WebSocketService {
  private ws: WebSocket | null = null;
  private listeners = new Map<string, Set<WsCallback>>();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private channel = 'dashboard';

  connect(channel = 'dashboard'): void {
    this.channel = channel;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/${channel}`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log(`[WS] Conectado ao canal: ${channel}`);
      if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    };

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data as string) as WsMessage;
        const type = data.type || 'update';
        this.listeners.get(type)?.forEach((cb) => cb(data));
        this.listeners.get('*')?.forEach((cb) => cb(data));
      } catch (err) {
        console.error('[WS] Erro ao parsear mensagem:', err);
      }
    };

    this.ws.onclose = () => {
      console.log('[WS] Conexão encerrada. Reconectando em 5s...');
      this.reconnectTimer = setTimeout(() => this.connect(channel), 5000);
    };

    this.ws.onerror = (err) => {
      console.error('[WS] Erro:', err);
    };
  }

  on(type: string, callback: WsCallback): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)!.add(callback);
    return () => { this.listeners.get(type)?.delete(callback); };
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const wsService = new WebSocketService();
