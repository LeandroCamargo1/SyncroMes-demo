import { useState, useEffect } from 'react';
import { Factory, Gauge, Timer, AlertTriangle, TrendingUp, Zap } from 'lucide-react';

const API_BASE = '/api';

export default function DashboardTV() {
  const [data, setData] = useState<any>(null);
  const [machines, setMachines] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [clock, setClock] = useState(new Date());
  const [loading, setLoading] = useState(true);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    const clockInterval = setInterval(() => setClock(new Date()), 1000);
    return () => { clearInterval(interval); clearInterval(clockInterval); };
  }, []);

  const fetchData = async () => {
    try {
      // Dashboard TV doesn't require auth — try to fetch with stored token or public endpoints
      const token = localStorage.getItem('token');
      const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

      const [dash, mch, msgs] = await Promise.all([
        fetch(`${API_BASE}/dashboard/summary`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API_BASE}/machines`, { headers }).then(r => r.ok ? r.json() : []),
        fetch(`${API_BASE}/pcp/messages?active_only=true`, { headers }).then(r => r.ok ? r.json() : []),
      ]);
      if (dash) setData(dash);
      setMachines(mch || []);
      setMessages(msgs || []);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const statusColors: Record<string, string> = {
    running: 'bg-emerald-500 shadow-emerald-500/30',
    stopped: 'bg-red-500 shadow-red-500/30',
    idle: 'bg-surface-400',
    maintenance: 'bg-amber-500 shadow-amber-500/30',
    setup: 'bg-blue-500 shadow-blue-500/30',
  };

  const statusLabels: Record<string, string> = {
    running: 'Produzindo',
    stopped: 'Parada',
    idle: 'Ociosa',
    maintenance: 'Manutenção',
    setup: 'Setup',
  };

  if (loading) {
    return (
      <div className="h-screen w-screen bg-surface-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-surface-400 mt-4 text-lg">Carregando Dashboard TV...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-surface-950 text-white overflow-hidden flex flex-col">
      {/* Header */}
      <header className="h-14 bg-surface-900/80 border-b border-surface-800 flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-primary-500 to-primary-700 p-1.5 rounded-lg">
            <Factory className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-bold">
            <span className="text-white">Synchro</span>
            <span className="text-primary-400 ml-1">MES</span>
          </span>
          <span className="text-xs text-surface-500 ml-2">Dashboard TV</span>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs text-surface-400">Atualização automática a cada 30s</span>
          </div>
          <div className="text-right">
            <p className="text-xl font-mono font-bold text-white tabular-nums">
              {clock.toLocaleTimeString('pt-BR')}
            </p>
            <p className="text-[10px] text-surface-500 uppercase">
              {clock.toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'short' })}
            </p>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 p-4 grid grid-rows-[auto_1fr_auto] gap-4 overflow-hidden">
        {/* Top KPIs */}
        <div className="grid grid-cols-5 gap-3">
          {[
            { label: 'OEE Fábrica', value: `${data?.oee_average?.toFixed(1) || '—'}%`, icon: Gauge, color: 'from-primary-500 to-primary-700' },
            { label: 'Produção Hoje', value: data?.production_today?.toLocaleString('pt-BR') || '—', icon: TrendingUp, color: 'from-emerald-500 to-emerald-700' },
            { label: 'Máquinas Ativas', value: `${machines.filter(m => m.status === 'running').length}/${machines.length}`, icon: Factory, color: 'from-blue-500 to-blue-700' },
            { label: 'Paradas Ativas', value: data?.active_downtimes || '0', icon: AlertTriangle, color: 'from-red-500 to-red-700' },
            { label: 'Eficiência Média', value: `${(machines.reduce((s, m) => s + (m.efficiency || 0), 0) / (machines.length || 1)).toFixed(1)}%`, icon: Timer, color: 'from-violet-500 to-violet-700' },
          ].map((kpi, i) => (
            <div key={i} className="bg-surface-900/60 rounded-xl p-4 border border-surface-800/50 backdrop-blur-sm">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${kpi.color} flex items-center justify-center shadow-lg`}>
                  <kpi.icon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-surface-400 uppercase tracking-wider">{kpi.label}</p>
                  <p className="text-2xl font-bold text-white mt-0.5 tabular-nums">{kpi.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Machine Grid */}
        <div className="grid grid-cols-5 lg:grid-cols-10 gap-2 content-start overflow-y-auto">
          {machines.map(m => (
            <div key={m.code} className="bg-surface-900/40 rounded-xl p-3 border border-surface-800/30 text-center hover:bg-surface-800/50 transition-colors">
              <div className={`w-4 h-4 rounded-full mx-auto mb-2 shadow-lg ${statusColors[m.status] || 'bg-surface-600'}`} />
              <p className="font-mono text-sm font-bold text-white">{m.code}</p>
              <p className={`text-[10px] uppercase font-semibold mt-1 ${
                m.status === 'running' ? 'text-emerald-400' :
                m.status === 'stopped' ? 'text-red-400' :
                m.status === 'maintenance' ? 'text-amber-400' :
                m.status === 'setup' ? 'text-blue-400' :
                'text-surface-500'
              }`}>{statusLabels[m.status] || m.status}</p>
              {m.current_product && (
                <p className="text-[10px] text-surface-400 mt-1 truncate">{m.current_product}</p>
              )}
              {m.efficiency != null && (
                <div className="mt-2">
                  <div className="h-1 rounded-full bg-surface-700 overflow-hidden">
                    <div className={`h-full rounded-full transition-all ${
                      m.efficiency >= 75 ? 'bg-emerald-500' : m.efficiency >= 60 ? 'bg-amber-500' : 'bg-red-500'
                    }`} style={{ width: `${Math.min(m.efficiency, 100)}%` }} />
                  </div>
                  <p className="text-[9px] text-surface-500 mt-0.5 tabular-nums">{m.efficiency?.toFixed(0)}%</p>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Bottom PCP Messages */}
        {messages.length > 0 && (
          <div className="bg-surface-900/60 rounded-xl border border-surface-800/50 p-3 overflow-hidden">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-semibold text-surface-400 uppercase tracking-wider">Mensagens PCP</span>
            </div>
            <div className="flex gap-4 overflow-x-auto">
              {messages.slice(0, 6).map(m => (
                <div key={m.id} className={`shrink-0 px-4 py-2 rounded-lg border-l-2 ${
                  m.type === 'urgent' ? 'border-l-red-500 bg-red-500/10' :
                  m.type === 'warning' ? 'border-l-amber-500 bg-amber-500/10' :
                  'border-l-blue-500 bg-blue-500/10'
                }`}>
                  <p className="text-sm text-white font-medium">{m.message}</p>
                  {m.target_machine && (
                    <p className="text-[10px] text-surface-400 mt-0.5 font-mono">{m.target_machine}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
