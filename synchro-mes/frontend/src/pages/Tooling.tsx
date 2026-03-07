import { useState, useEffect } from 'react';
import api from '../services/api';
import { Wrench, AlertTriangle, Plus, CheckCircle2, Clock } from 'lucide-react';

export default function Tooling() {
  const [tab, setTab] = useState('molds');
  const [molds, setMolds] = useState<any[]>([]);
  const [maintenance, setMaintenance] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ mold_code: '', maintenance_type: 'preventiva', technician: '', description: '' });

  useEffect(() => { fetchData(); }, [tab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [m, mt, al] = await Promise.all([
        api.get('/tooling/molds'),
        api.get('/tooling/maintenance'),
        api.get('/tooling/alerts'),
      ]);
      setMolds(m.data);
      setMaintenance(mt.data);
      setAlerts(al.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleCreateMaintenance = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/tooling/maintenance', form);
      setShowForm(false);
      setForm({ mold_code: '', maintenance_type: 'preventiva', technician: '', description: '' });
      fetchData();
    } catch (err) { console.error(err); }
  };

  const handleFinishMaintenance = async (id: number) => {
    try {
      await api.patch(`/tooling/maintenance/${id}/finish`, { duration_hours: 0, notes: 'Concluída' });
      fetchData();
    } catch (err) { console.error(err); }
  };

  const maintTypeBadge = (type: string) => {
    const map: Record<string, string> = {
      preventiva: 'bg-blue-50 text-blue-700 ring-blue-200',
      corretiva: 'bg-red-50 text-red-700 ring-red-200',
      limpeza: 'bg-surface-100 text-surface-600 ring-surface-200',
    };
    return <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${map[type] || 'bg-surface-100 text-surface-600 ring-surface-200'}`}>{type}</span>;
  };

  const statusBadge = (status: string) => {
    const map: Record<string, string> = {
      concluida: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
      pendente: 'bg-amber-50 text-amber-700 ring-amber-200',
      em_andamento: 'bg-blue-50 text-blue-700 ring-blue-200',
    };
    const labels: Record<string, string> = { concluida: 'Concluída', pendente: 'Pendente', em_andamento: 'Em Andamento' };
    return <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${map[status] || 'bg-surface-100 text-surface-600 ring-surface-200'}`}>{labels[status] || status}</span>;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">Ferramentaria</h1>
          <p className="page-subtitle">Gestão de moldes, manutenções e alertas</p>
        </div>
        {tab === 'maintenance' && (
          <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" /> Nova Manutenção
          </button>
        )}
      </div>

      {/* Alertas */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          {alerts.map((a, i) => (
            <div key={i} className={`card flex items-center gap-3 border-l-4 ${
              a.severity === 'critical' ? 'border-l-red-500 bg-red-50/50' :
              a.severity === 'warning' ? 'border-l-amber-500 bg-amber-50/50' :
              'border-l-blue-500 bg-blue-50/50'
            }`}>
              <AlertTriangle className={`w-5 h-5 ${a.severity === 'critical' ? 'text-red-500' : a.severity === 'warning' ? 'text-amber-500' : 'text-blue-500'}`} />
              <div className="flex-1">
                {a.type === 'shots_limit' ? (
                  <p className="text-sm font-medium text-surface-800">
                    Molde <span className="font-mono font-bold">{a.mold_code}</span> com <span className="font-bold">{a.percentage}%</span> do limite de batidas
                    ({a.current_shots?.toLocaleString('pt-BR')} / {a.max_shots?.toLocaleString('pt-BR')})
                  </p>
                ) : (
                  <p className="text-sm font-medium text-surface-800">{a.count} manutenção(ões) pendente(s)</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="tab-bar w-fit">
        <button onClick={() => { setTab('molds'); setShowForm(false); }} className={tab === 'molds' ? 'tab-item-active' : 'tab-item'}>
          <Wrench className="w-4 h-4 inline mr-1.5 -mt-0.5" />Moldes
        </button>
        <button onClick={() => { setTab('maintenance'); setShowForm(false); }} className={tab === 'maintenance' ? 'tab-item-active' : 'tab-item'}>
          <Clock className="w-4 h-4 inline mr-1.5 -mt-0.5" />Manutenções
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <div className="card border-2 border-primary-200 animate-slide-up">
          <h3 className="text-sm font-semibold text-surface-800 mb-4">Nova Manutenção</h3>
          <form onSubmit={handleCreateMaintenance} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input type="text" placeholder="Código do Molde (MLD-001)" required value={form.mold_code} onChange={e => setForm({...form, mold_code: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <select value={form.maintenance_type} onChange={e => setForm({...form, maintenance_type: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none">
              <option value="preventiva">Preventiva</option>
              <option value="corretiva">Corretiva</option>
              <option value="limpeza">Limpeza</option>
            </select>
            <input type="text" placeholder="Técnico" value={form.technician} onChange={e => setForm({...form, technician: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <input type="text" placeholder="Descrição" value={form.description} onChange={e => setForm({...form, description: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <div className="md:col-span-2 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-sm text-surface-600 hover:bg-surface-100">Cancelar</button>
              <button type="submit" className="btn-primary">Criar</button>
            </div>
          </form>
        </div>
      )}

      {/* Tables */}
      {loading ? (
        <div className="flex justify-center py-16"><div className="spinner w-8 h-8" /></div>
      ) : tab === 'molds' ? (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr><th>Código</th><th>Descrição</th><th className="text-right">Cavidades</th><th className="text-right">Ciclo (s)</th><th className="text-right">Batidas</th><th>Status</th></tr>
              </thead>
              <tbody>
                {molds.map(m => {
                  const ratio = m.max_shots ? (m.current_shots || 0) / m.max_shots : 0;
                  return (
                    <tr key={m.id}>
                      <td className="font-mono font-semibold text-primary-600 text-sm">{m.code}</td>
                      <td className="text-surface-700">{m.description || '—'}</td>
                      <td className="text-right tabular-nums">{m.cavities}</td>
                      <td className="text-right tabular-nums">{m.cycle_time || '—'}</td>
                      <td className="text-right">
                        <div className="flex items-center gap-2 justify-end">
                          <div className="w-12 h-1.5 rounded-full bg-surface-100 overflow-hidden">
                            <div className={`h-full rounded-full transition-all ${ratio >= 0.9 ? 'bg-red-500' : ratio >= 0.7 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                              style={{ width: `${Math.min(ratio * 100, 100)}%` }} />
                          </div>
                          <span className="text-xs tabular-nums font-medium text-surface-500">
                            {(m.current_shots || 0).toLocaleString('pt-BR')}
                          </span>
                        </div>
                      </td>
                      <td className="text-surface-500 capitalize text-sm">{m.status || '—'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr><th>Molde</th><th>Tipo</th><th>Técnico</th><th>Descrição</th><th className="text-right">Duração</th><th className="text-right">Custo</th><th>Status</th><th></th></tr>
              </thead>
              <tbody>
                {maintenance.length === 0 ? (
                  <tr><td colSpan={8} className="text-center text-surface-400 py-8">Nenhuma manutenção registrada</td></tr>
                ) : maintenance.map(m => (
                  <tr key={m.id}>
                    <td className="font-mono font-semibold text-sm">{m.mold_code}</td>
                    <td>{maintTypeBadge(m.maintenance_type)}</td>
                    <td className="text-surface-500 text-sm">{m.technician || '—'}</td>
                    <td className="text-surface-400 text-sm max-w-xs truncate">{m.description || '—'}</td>
                    <td className="text-right tabular-nums">{m.duration_hours ? `${m.duration_hours}h` : '—'}</td>
                    <td className="text-right tabular-nums">{m.cost ? `R$ ${m.cost.toFixed(2)}` : '—'}</td>
                    <td>{statusBadge(m.status)}</td>
                    <td>
                      {(m.status === 'pendente' || m.status === 'em_andamento') && (
                        <button onClick={() => handleFinishMaintenance(m.id)}
                          className="text-xs font-medium text-primary-600 hover:text-primary-700 transition-colors">
                          Finalizar
                        </button>
                      )}
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
