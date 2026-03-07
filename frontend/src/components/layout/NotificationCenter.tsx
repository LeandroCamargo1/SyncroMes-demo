import { useState, useEffect, useRef, useCallback } from 'react';
import { Bell, X, Check, CheckCheck, Info, AlertTriangle, XCircle, CheckCircle } from 'lucide-react';
import api from '../../services/api';
import { wsService } from '../../services/websocket';

interface Notification {
  id: number;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  link: string | null;
  created_at: string | null;
}

const typeConfig: Record<string, { icon: typeof Info; color: string; bg: string }> = {
  info:    { icon: Info,          color: 'text-blue-600',    bg: 'bg-blue-50'    },
  warning: { icon: AlertTriangle, color: 'text-amber-600',  bg: 'bg-amber-50'   },
  error:   { icon: XCircle,      color: 'text-rose-600',    bg: 'bg-red-50'     },
  success: { icon: CheckCircle,  color: 'text-emerald-600', bg: 'bg-emerald-50' },
};

export default function NotificationCenter() {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const panelRef = useRef<HTMLDivElement>(null);

  const fetchNotifications = useCallback(async () => {
    try {
      const [listRes, countRes] = await Promise.all([
        api.get('/notifications/', { params: { limit: 30 } }),
        api.get('/notifications/count'),
      ]);
      setNotifications(listRes.data);
      setUnreadCount(countRes.data.unread);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000);

    // WebSocket: escuta eventos de notificação em tempo real
    wsService.connect('notifications');
    const unsub = wsService.on('*', () => {
      fetchNotifications();
    });

    return () => {
      clearInterval(interval);
      unsub();
    };
  }, [fetchNotifications]);

  // Fechar ao clicar fora
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    if (open) document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  const markAllRead = async () => {
    try {
      await api.patch('/notifications/read-all');
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch { /* ignore */ }
  };

  const markRead = async (ids: number[]) => {
    try {
      await api.patch('/notifications/read', { ids });
      setNotifications((prev) =>
        prev.map((n) => (ids.includes(n.id) ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - ids.length));
    } catch { /* ignore */ }
  };

  const handleClick = (n: Notification) => {
    if (!n.is_read) markRead([n.id]);
    if (n.link) window.location.href = n.link;
  };

  const formatTime = (ts: string | null) => {
    if (!ts) return '';
    const d = new Date(ts);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return 'agora';
    if (diffMin < 60) return `${diffMin}min`;
    const diffH = Math.floor(diffMin / 60);
    if (diffH < 24) return `${diffH}h`;
    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
  };

  return (
    <div className="relative" ref={panelRef}>
      {/* Bell button */}
      <button
        onClick={() => setOpen(!open)}
        className="p-2.5 hover:bg-surface-100 rounded-xl text-surface-400
                   hover:text-surface-600 transition-colors relative"
      >
        <Bell className="w-[18px] h-[18px]" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1
                           bg-danger text-white text-[10px] font-bold rounded-full
                           flex items-center justify-center ring-2 ring-white">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown panel */}
      {open && (
        <div className="absolute right-0 top-12 w-96 max-h-[480px] bg-white rounded-2xl
                        shadow-2xl shadow-black/10 border border-surface-200/60 z-50
                        flex flex-col overflow-hidden animate-fade-in">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-surface-100">
            <h3 className="text-sm font-semibold text-surface-900">Notificações</h3>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllRead}
                  className="text-[11px] text-primary-600 hover:text-primary-700 font-medium
                             flex items-center gap-1"
                >
                  <CheckCheck className="w-3.5 h-3.5" /> Marcar todas
                </button>
              )}
              <button onClick={() => setOpen(false)} className="p-1 hover:bg-surface-100 rounded-lg">
                <X className="w-4 h-4 text-surface-400" />
              </button>
            </div>
          </div>

          {/* List */}
          <div className="overflow-y-auto flex-1">
            {notifications.length === 0 ? (
              <div className="py-12 text-center">
                <Bell className="w-8 h-8 text-surface-200 mx-auto mb-2" />
                <p className="text-sm text-surface-400">Nenhuma notificação</p>
              </div>
            ) : (
              notifications.map((n) => {
                const cfg = typeConfig[n.type] || typeConfig.info;
                const Icon = cfg.icon;
                return (
                  <button
                    key={n.id}
                    onClick={() => handleClick(n)}
                    className={`w-full text-left px-4 py-3 flex gap-3 hover:bg-surface-50
                               transition-colors border-b border-surface-50 last:border-0
                               ${!n.is_read ? 'bg-primary-50/30' : ''}`}
                  >
                    <div className={`p-2 rounded-xl ${cfg.bg} shrink-0 mt-0.5`}>
                      <Icon className={`w-4 h-4 ${cfg.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <p className={`text-sm leading-tight ${
                          !n.is_read ? 'font-semibold text-surface-900' : 'font-medium text-surface-600'
                        }`}>
                          {n.title}
                        </p>
                        <span className="text-[10px] text-surface-400 shrink-0 mt-0.5">
                          {formatTime(n.created_at)}
                        </span>
                      </div>
                      <p className="text-xs text-surface-400 mt-0.5 line-clamp-2">{n.message}</p>
                    </div>
                    {!n.is_read && (
                      <span className="w-2 h-2 bg-primary-500 rounded-full shrink-0 mt-2" />
                    )}
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
