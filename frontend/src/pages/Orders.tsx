import { useState, useEffect } from 'react';
import api from '../services/api';
import { ClipboardList, Filter, Download, Search } from 'lucide-react';

export default function Orders() {
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => { fetchOrders(); }, []);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/production/orders');
      setOrders(data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const filtered = orders.filter(o => {
    const matchSearch = !search || o.order_number?.toLowerCase().includes(search.toLowerCase())
      || o.product_name?.toLowerCase().includes(search.toLowerCase())
      || o.client?.toLowerCase().includes(search.toLowerCase());
    const matchStatus = filterStatus === 'all' || o.status === filterStatus;
    return matchSearch && matchStatus;
  });

  const statusBadge = (status: string) => {
    const map: Record<string, { cls: string; label: string }> = {
      in_progress: { cls: 'bg-emerald-50 text-emerald-700 ring-emerald-200', label: 'Em Produção' },
      planned: { cls: 'bg-blue-50 text-blue-700 ring-blue-200', label: 'Planejada' },
      completed: { cls: 'bg-surface-100 text-surface-600 ring-surface-200', label: 'Concluída' },
      cancelled: { cls: 'bg-red-50 text-red-700 ring-red-200', label: 'Cancelada' },
    };
    const cfg = map[status] || { cls: 'bg-surface-100 text-surface-600 ring-surface-200', label: status };
    return <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${cfg.cls}`}>{cfg.label}</span>;
  };

  const priorityBadge = (priority: string) => {
    const map: Record<string, { cls: string; label: string }> = {
      urgent: { cls: 'bg-red-50 text-red-700 ring-red-200', label: 'Urgente' },
      high: { cls: 'bg-amber-50 text-amber-700 ring-amber-200', label: 'Alta' },
      normal: { cls: 'bg-surface-100 text-surface-600 ring-surface-200', label: 'Normal' },
    };
    const cfg = map[priority] || { cls: 'bg-surface-100 text-surface-600 ring-surface-200', label: priority };
    return <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${cfg.cls}`}>{cfg.label}</span>;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Ordens de Produção</h1>
        <p className="page-subtitle">Gestão completa do ciclo de vida das ordens</p>
      </div>

      {/* Barra de filtros */}
      <div className="card">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
            <input
              type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar ordem, produto ou cliente..."
              className="w-full pl-9 pr-3 py-2 rounded-lg border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 bg-white"
            />
          </div>
          <div className="tab-bar">
            {[['all', 'Todas'], ['in_progress', 'Em Produção'], ['planned', 'Planejadas'], ['completed', 'Concluídas']].map(([val, label]) => (
              <button key={val} onClick={() => setFilterStatus(val)}
                className={filterStatus === val ? 'tab-item-active' : 'tab-item'}>{label}</button>
            ))}
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Ordens', value: orders.length, color: 'text-primary-600' },
          { label: 'Em Produção', value: orders.filter(o => o.status === 'in_progress').length, color: 'text-emerald-600' },
          { label: 'Planejadas', value: orders.filter(o => o.status === 'planned').length, color: 'text-blue-600' },
          { label: 'Concluídas', value: orders.filter(o => o.status === 'completed').length, color: 'text-surface-500' },
        ].map((kpi, i) => (
          <div key={i} className="card text-center">
            <p className="text-xs font-medium text-surface-400 uppercase tracking-wider">{kpi.label}</p>
            <p className={`text-2xl font-bold mt-1 ${kpi.color}`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Tabela */}
      {loading ? (
        <div className="flex justify-center py-16"><div className="spinner w-8 h-8" /></div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr>
                  <th>Ordem</th>
                  <th>Produto</th>
                  <th>Máquina</th>
                  <th>Prioridade</th>
                  <th className="text-right">Planejado</th>
                  <th className="text-right">Produzido</th>
                  <th className="text-right">Progresso</th>
                  <th>Status</th>
                  <th>Cliente</th>
                  <th>Entrega</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((o) => {
                  const progress = o.quantity_planned > 0 ? Math.round(o.quantity_produced / o.quantity_planned * 100) : 0;
                  return (
                    <tr key={o.id}>
                      <td className="font-mono font-semibold text-primary-600 text-sm">{o.order_number}</td>
                      <td className="font-medium text-surface-800">{o.product_name}</td>
                      <td className="font-mono text-xs text-surface-500">{o.machine_code || '—'}</td>
                      <td>{priorityBadge(o.priority)}</td>
                      <td className="text-right tabular-nums">{o.quantity_planned?.toLocaleString('pt-BR')}</td>
                      <td className="text-right tabular-nums font-medium">{o.quantity_produced?.toLocaleString('pt-BR')}</td>
                      <td className="text-right">
                        <div className="flex items-center gap-2 justify-end">
                          <div className="w-16 h-1.5 rounded-full bg-surface-100 overflow-hidden">
                            <div className="h-full rounded-full bg-primary-500 transition-all" style={{ width: `${Math.min(progress, 100)}%` }} />
                          </div>
                          <span className="text-xs tabular-nums font-medium text-surface-500">{progress}%</span>
                        </div>
                      </td>
                      <td>{statusBadge(o.status)}</td>
                      <td className="text-surface-400 text-sm">{o.client || '—'}</td>
                      <td className="text-surface-400 text-xs tabular-nums">{o.due_date ? new Date(o.due_date).toLocaleDateString('pt-BR') : '—'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
