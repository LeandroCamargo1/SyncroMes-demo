import { useState, useEffect, useMemo } from 'react';
import api from '../services/api';
import { Package, ClipboardList } from 'lucide-react';
import { DonutChart, OutputVsTargetChart } from '../components/charts';

export default function Production() {
  const [orders, setOrders] = useState<any[]>([]);
  const [entries, setEntries] = useState<any[]>([]);
  const [tab, setTab] = useState('orders');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [tab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (tab === 'orders') {
        const { data } = await api.get('/production/orders');
        setOrders(data);
      } else {
        const { data } = await api.get('/production/entries?limit=50');
        setEntries(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Order stats for charts
  const orderStatusData = useMemo(() => {
    const st: Record<string, number> = {};
    orders.forEach(o => { st[o.status] = (st[o.status] || 0) + 1; });
    const labels: Record<string, string> = { in_progress: 'Em Produção', planned: 'Planejada', completed: 'Concluída', cancelled: 'Cancelada' };
    return Object.entries(st).map(([k, v]) => ({ name: labels[k] || k, value: v }));
  }, [orders]);

  const orderOutputData = useMemo(() => {
    return orders
      .filter(o => o.quantity_planned > 0)
      .slice(0, 8)
      .map(o => ({
        name: o.order_number?.slice(-6) || `#${o.id}`,
        planned: o.quantity_planned || 0,
        produced: o.quantity_produced || 0,
      }));
  }, [orders]);

  const statusBadge = (status: string) => {
    const map: Record<string, { cls: string; label: string }> = {
      in_progress: { cls: 'bg-emerald-50 text-emerald-700 ring-emerald-200', label: 'Em Produção' },
      planned: { cls: 'bg-blue-50 text-blue-700 ring-blue-200', label: 'Planejada' },
      completed: { cls: 'bg-surface-100 text-surface-600 ring-surface-200', label: 'Concluída' },
      cancelled: { cls: 'bg-red-50 text-red-700 ring-red-200', label: 'Cancelada' },
    };
    const cfg = map[status] || { cls: 'bg-surface-100 text-surface-600 ring-surface-200', label: status };
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold 
                        ring-1 uppercase tracking-wider ${cfg.cls}`}>
        {cfg.label}
      </span>
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Produção</h1>
        <p className="page-subtitle">Ordens e lançamentos de produção</p>
      </div>

      {/* Modern tabs */}
      <div className="tab-bar w-fit">
        <button onClick={() => setTab('orders')}
          className={tab === 'orders' ? 'tab-item-active' : 'tab-item'}>
          <Package className="w-4 h-4 inline mr-1.5 -mt-0.5" />Ordens
        </button>
        <button onClick={() => setTab('entries')}
          className={tab === 'entries' ? 'tab-item-active' : 'tab-item'}>
          <ClipboardList className="w-4 h-4 inline mr-1.5 -mt-0.5" />Lançamentos
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <div className="spinner w-8 h-8" />
        </div>
      ) : tab === 'orders' ? (
        <div className="space-y-6">
          {/* Order Charts */}
          {orders.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card">
                <h3 className="text-sm font-semibold text-surface-800 mb-1">Planejado vs Produzido</h3>
                <p className="text-xs text-surface-400 mb-4">Acompanhamento por ordem</p>
                <OutputVsTargetChart data={orderOutputData} />
              </div>
              <div className="card">
                <h3 className="text-sm font-semibold text-surface-800 mb-1">Status das Ordens</h3>
                <p className="text-xs text-surface-400 mb-4">Distribuição por status</p>
                <DonutChart
                  data={orderStatusData}
                  colors={['#10b981', '#3b82f6', '#94a3b8', '#ef4444']}
                  innerValue={String(orders.length)}
                  innerLabel="Ordens"
                />
              </div>
            </div>
          )}

          {/* Orders Table */}
          <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr>
                  <th>Ordem</th>
                  <th>Produto</th>
                  <th>Máquina</th>
                  <th className="text-right">Planejado</th>
                  <th className="text-right">Produzido</th>
                  <th className="text-right">Refugo</th>
                  <th>Status</th>
                  <th>Cliente</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((o) => (
                  <tr key={o.id}>
                    <td className="font-mono font-semibold text-primary-600 text-sm">{o.order_number}</td>
                    <td className="font-medium text-surface-800">{o.product_name}</td>
                    <td className="font-mono text-xs text-surface-500">{o.machine_code || '—'}</td>
                    <td className="text-right tabular-nums">{o.quantity_planned.toLocaleString('pt-BR')}</td>
                    <td className="text-right tabular-nums font-medium">{o.quantity_produced.toLocaleString('pt-BR')}</td>
                    <td className="text-right tabular-nums text-red-600 font-medium">{o.quantity_rejected.toLocaleString('pt-BR')}</td>
                    <td>{statusBadge(o.status)}</td>
                    <td className="text-surface-400 text-sm">{o.client || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          </div>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr>
                  <th>Máquina</th>
                  <th>Produto</th>
                  <th>Operador</th>
                  <th>Turno</th>
                  <th className="text-right">Boas</th>
                  <th className="text-right">Refugo</th>
                  <th className="text-right">Ciclo</th>
                  <th>Data/Hora</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((e) => (
                  <tr key={e.id}>
                    <td className="font-mono font-semibold text-sm">{e.machine_code}</td>
                    <td className="font-medium text-surface-800">{e.product_code}</td>
                    <td className="text-surface-500">{e.operator_name || '—'}</td>
                    <td>
                      {e.shift ? (
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-surface-100 text-xs font-medium text-surface-600">
                          {e.shift}
                        </span>
                      ) : '—'}
                    </td>
                    <td className="text-right tabular-nums text-emerald-600 font-semibold">{e.quantity_good}</td>
                    <td className="text-right tabular-nums text-red-600 font-medium">{e.quantity_rejected}</td>
                    <td className="text-right tabular-nums text-surface-500">{e.cycle_time_actual?.toFixed(1) || '—'}s</td>
                    <td className="text-surface-400 text-xs tabular-nums">
                      {e.timestamp ? new Date(e.timestamp).toLocaleString('pt-BR') : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
