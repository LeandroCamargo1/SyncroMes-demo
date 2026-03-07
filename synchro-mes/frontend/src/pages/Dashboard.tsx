import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../services/api';
import { wsService } from '../services/websocket';
import { Activity, Zap, CheckCircle, AlertTriangle, Package, XCircle, TrendingUp, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import MachineGrid from '../components/dashboard/MachineGrid';
import OeeGauge from '../components/dashboard/OeeGauge';
import { ProductionBarChart, HorizontalBarChart } from '../components/charts';

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchDashboard = useCallback(async () => {
    try {
      const { data } = await api.get('/dashboard/summary');
      setSummary(data);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Erro ao carregar dashboard:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();

    // WebSocket: atualiza dashboard em tempo real quando backend notifica
    wsService.connect('dashboard');
    setWsConnected(true);

    const unsubRefresh = wsService.on('dashboard:refresh', () => {
      fetchDashboard();
    });

    // Fallback polling a cada 30s
    pollingRef.current = setInterval(fetchDashboard, 30000);

    return () => {
      unsubRefresh();
      wsService.disconnect();
      setWsConnected(false);
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [fetchDashboard]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <div className="spinner w-10 h-10" />
          <span className="text-sm text-surface-400">Carregando dashboard...</span>
        </div>
      </div>
    );
  }

  if (!summary) return (
    <div className="text-center py-20">
      <XCircle className="w-12 h-12 text-surface-300 mx-auto mb-3" />
      <p className="text-surface-500 font-medium">Erro ao carregar dados</p>
      <button onClick={fetchDashboard} className="btn-secondary mt-4">
        <RefreshCw className="w-4 h-4" /> Tentar novamente
      </button>
    </div>
  );

  const kpis = [
    { 
      label: 'Rodando', value: summary.machines_running, total: summary.total_machines, 
      icon: Activity, iconColor: 'text-emerald-600',
      bg: 'bg-emerald-50', ring: 'ring-emerald-100',
    },
    { 
      label: 'OEE Médio', value: `${summary.oee_average}%`, 
      icon: TrendingUp, iconColor: 'text-primary-600',
      bg: 'bg-primary-50', ring: 'ring-primary-100',
    },
    { 
      label: 'Produzido', value: summary.total_produced_today.toLocaleString('pt-BR'), 
      icon: Package, iconColor: 'text-blue-600',
      bg: 'bg-blue-50', ring: 'ring-blue-100',
    },
    { 
      label: 'Refugo', value: `${summary.scrap_rate}%`, 
      icon: XCircle, iconColor: 'text-rose-600',
      bg: 'bg-red-50', ring: 'ring-red-100',
    },
    { 
      label: 'Ordens', value: summary.active_orders, 
      icon: CheckCircle, iconColor: 'text-amber-600',
      bg: 'bg-amber-50', ring: 'ring-amber-100',
    },
    { 
      label: 'Paradas', value: summary.machines_stopped + summary.machines_maintenance, 
      icon: AlertTriangle, iconColor: 'text-orange-600',
      bg: 'bg-orange-50', ring: 'ring-orange-100',
    },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {kpis.map((kpi, i) => (
          <div key={kpi.label} 
            className="card-hover group cursor-default"
            style={{ animationDelay: `${i * 60}ms` }}>
            <div className="flex items-start justify-between mb-3">
              <div className={`p-2.5 rounded-xl ${kpi.bg} ring-1 ${kpi.ring} 
                             group-hover:scale-110 transition-transform duration-300`}>
                <kpi.icon className={`w-4 h-4 ${kpi.iconColor}`} />
              </div>
            </div>
            <span className="text-2xl font-bold text-surface-900 tracking-tight">
              {kpi.total ? `${kpi.value}/${kpi.total}` : kpi.value}
            </span>
            <span className="block text-xs text-surface-400 mt-0.5 font-medium">{kpi.label}</span>
          </div>
        ))}
      </div>

      {/* OEE + Info section */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-1">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-surface-900">OEE da Fábrica</h2>
              <p className="text-xs text-surface-400 mt-0.5">Overall Equipment Effectiveness</p>
            </div>
            <Zap className="w-5 h-5 text-primary-400" />
          </div>
          <OeeGauge value={summary.oee_average} />
        </div>
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-surface-900">Máquinas</h2>
              <p className="text-xs text-surface-400 mt-0.5">
                {summary.total_machines} máquinas · {summary.machines_running} rodando
              </p>
            </div>
            {lastUpdate && (
              <span className="text-[10px] text-surface-400 flex items-center gap-1">
                {wsConnected ? <Wifi className="w-3 h-3 text-emerald-500" /> : <WifiOff className="w-3 h-3 text-surface-300" />}
                {lastUpdate.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
            )}
          </div>
          <MachineGrid machines={summary.machines} />
        </div>
      </div>

      {/* Charts — Siemens Opcenter style */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-base font-semibold text-surface-900 mb-1">Produção por Máquina</h2>
          <p className="text-xs text-surface-400 mb-4">Peças boas vs refugo — hoje</p>
          <ProductionBarChart
            data={summary.machines
              .filter((m: any) => (m.produced_today || 0) + (m.rejected_today || 0) > 0)
              .map((m: any) => ({ name: m.code, produced: m.produced_today || 0, rejected: m.rejected_today || 0 }))}
          />
        </div>
        <div className="card">
          <h2 className="text-base font-semibold text-surface-900 mb-1">OEE por Máquina</h2>
          <p className="text-xs text-surface-400 mb-4">Ranking de eficiência</p>
          <HorizontalBarChart
            data={summary.machines
              .filter((m: any) => m.oee != null && m.oee > 0)
              .sort((a: any, b: any) => (b.oee || 0) - (a.oee || 0))
              .map((m: any) => ({ name: m.code, value: m.oee || 0 }))}
            target={85}
          />
        </div>
      </div>
    </div>
  );
}
