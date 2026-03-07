import { useState, useEffect } from 'react';
import api from '../services/api';
import { Package, ClipboardList } from 'lucide-react';

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
