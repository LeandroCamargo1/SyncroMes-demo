import { useState, useEffect } from 'react';
import api from '../services/api';
import { History as HistoryIcon, Filter, Search, Clock } from 'lucide-react';

export default function HistoryPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterAction, setFilterAction] = useState('');

  useEffect(() => { fetchLogs(); }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/history');
      setLogs(data);
    } catch (err) {
      console.error(err);
      // If unauthorized, show empty
      setLogs([]);
    }
    finally { setLoading(false); }
  };

  const filtered = logs.filter(l => {
    const matchSearch = !search ||
      l.action?.toLowerCase().includes(search.toLowerCase()) ||
      l.user_email?.toLowerCase().includes(search.toLowerCase()) ||
      l.entity_type?.toLowerCase().includes(search.toLowerCase());
    const matchAction = !filterAction || l.action === filterAction;
    return matchSearch && matchAction;
  });

  const uniqueActions = [...new Set(logs.map(l => l.action).filter(Boolean))];

  const actionBadge = (action: string) => {
    const map: Record<string, string> = {
      create: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
      update: 'bg-blue-50 text-blue-700 ring-blue-200',
      delete: 'bg-red-50 text-red-700 ring-red-200',
      login: 'bg-violet-50 text-violet-700 ring-violet-200',
    };
    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${map[action] || 'bg-surface-100 text-surface-600 ring-surface-200'}`}>
        {action}
      </span>
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Histórico</h1>
        <p className="page-subtitle">Log de auditoria e rastreabilidade do sistema</p>
      </div>

      {/* Filtros */}
      <div className="card">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
            <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar por ação, usuário ou entidade..."
              className="w-full pl-9 pr-3 py-2 rounded-lg border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 bg-white" />
          </div>
          {uniqueActions.length > 0 && (
            <select value={filterAction} onChange={(e) => setFilterAction(e.target.value)}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none bg-white">
              <option value="">Todas as ações</option>
              {uniqueActions.map(a => <option key={a} value={a}>{a}</option>)}
            </select>
          )}
        </div>
      </div>

      {/* Timeline */}
      {loading ? (
        <div className="flex justify-center py-16"><div className="spinner w-8 h-8" /></div>
      ) : filtered.length === 0 ? (
        <div className="card text-center py-12">
          <Clock className="w-12 h-12 mx-auto text-surface-300 mb-3" />
          <h3 className="text-base font-semibold text-surface-800">Nenhum registro encontrado</h3>
          <p className="text-sm text-surface-400 mt-1">O histórico aparecerá conforme as operações forem realizadas</p>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr>
                  <th>Data/Hora</th>
                  <th>Ação</th>
                  <th>Usuário</th>
                  <th>Entidade</th>
                  <th>Detalhes</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((l) => (
                  <tr key={l.id}>
                    <td className="text-surface-400 text-xs tabular-nums whitespace-nowrap">
                      {l.created_at ? new Date(l.created_at).toLocaleString('pt-BR') : '—'}
                    </td>
                    <td>{actionBadge(l.action)}</td>
                    <td className="text-sm text-surface-600">{l.user_email || '—'}</td>
                    <td className="text-sm font-medium text-surface-700">{l.entity_type || '—'}</td>
                    <td className="text-surface-400 text-sm max-w-xs truncate">{l.details || '—'}</td>
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
