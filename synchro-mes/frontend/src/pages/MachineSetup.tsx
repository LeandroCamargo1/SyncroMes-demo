import { useState, useEffect } from 'react';
import api from '../services/api';
import { Settings, Timer, Plus, Play, CheckCircle2 } from 'lucide-react';

export default function MachineSetup() {
  const [setups, setSetups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ machine_code: '', setup_type: 'troca_molde', mold_from: '', mold_to: '', product_from: '', product_to: '', operator_name: '' });

  useEffect(() => { fetchSetups(); }, []);

  const fetchSetups = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/setup');
      setSetups(data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/setup', { ...form, start_time: new Date().toISOString() });
      setShowForm(false);
      setForm({ machine_code: '', setup_type: 'troca_molde', mold_from: '', mold_to: '', product_from: '', product_to: '', operator_name: '' });
      fetchSetups();
    } catch (err) { console.error(err); }
  };

  const handleFinish = async (id: number) => {
    try {
      await api.patch(`/setup/${id}/finish`, { end_time: new Date().toISOString() });
      fetchSetups();
    } catch (err) { console.error(err); }
  };

  const setupTypeLabels: Record<string, string> = { troca_molde: 'Troca Molde', troca_cor: 'Troca Cor', troca_material: 'Troca Material', ajuste: 'Ajuste' };
  const setupTypeBadge = (type: string) => {
    const map: Record<string, string> = {
      troca_molde: 'bg-blue-50 text-blue-700 ring-blue-200',
      troca_cor: 'bg-violet-50 text-violet-700 ring-violet-200',
      troca_material: 'bg-amber-50 text-amber-700 ring-amber-200',
      ajuste: 'bg-surface-100 text-surface-600 ring-surface-200',
    };
    return <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${map[type] || 'bg-surface-100 text-surface-600 ring-surface-200'}`}>{setupTypeLabels[type] || type}</span>;
  };

  // KPIs
  const activeSetups = setups.filter(s => s.status === 'em_andamento');
  const completedSetups = setups.filter(s => s.status === 'concluido');
  const avgDuration = completedSetups.length > 0
    ? (completedSetups.reduce((s, e) => s + (e.duration_minutes || 0), 0) / completedSetups.length).toFixed(0)
    : '—';

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">Setup de Máquinas</h1>
          <p className="page-subtitle">Registro e acompanhamento de trocas e ajustes</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Iniciar Setup
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="card text-center">
          <Play className="w-5 h-5 mx-auto text-amber-500 mb-1" />
          <p className="text-xs text-surface-400">Em Andamento</p>
          <p className="text-2xl font-bold text-amber-600">{activeSetups.length}</p>
        </div>
        <div className="card text-center">
          <CheckCircle2 className="w-5 h-5 mx-auto text-emerald-500 mb-1" />
          <p className="text-xs text-surface-400">Concluídos</p>
          <p className="text-2xl font-bold text-emerald-600">{completedSetups.length}</p>
        </div>
        <div className="card text-center">
          <Timer className="w-5 h-5 mx-auto text-blue-500 mb-1" />
          <p className="text-xs text-surface-400">Média Duração</p>
          <p className="text-2xl font-bold text-blue-600">{avgDuration} <span className="text-sm font-normal text-surface-400">min</span></p>
        </div>
        <div className="card text-center">
          <Settings className="w-5 h-5 mx-auto text-primary-500 mb-1" />
          <p className="text-xs text-surface-400">Total Registros</p>
          <p className="text-2xl font-bold text-primary-600">{setups.length}</p>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="card border-2 border-primary-200 animate-slide-up">
          <h3 className="text-sm font-semibold text-surface-800 mb-4">Iniciar Setup</h3>
          <form onSubmit={handleStart} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input type="text" placeholder="Máquina (INJ-01)" required value={form.machine_code} onChange={e => setForm({...form, machine_code: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <select value={form.setup_type} onChange={e => setForm({...form, setup_type: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none">
              <option value="troca_molde">Troca de Molde</option>
              <option value="troca_cor">Troca de Cor</option>
              <option value="troca_material">Troca de Material</option>
              <option value="ajuste">Ajuste</option>
            </select>
            <input type="text" placeholder="Operador" value={form.operator_name} onChange={e => setForm({...form, operator_name: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <input type="text" placeholder="Molde DE" value={form.mold_from} onChange={e => setForm({...form, mold_from: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <input type="text" placeholder="Molde PARA" value={form.mold_to} onChange={e => setForm({...form, mold_to: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <input type="text" placeholder="Produto DE → PARA" value={form.product_from} onChange={e => setForm({...form, product_from: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <div className="md:col-span-3 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-sm text-surface-600 hover:bg-surface-100">Cancelar</button>
              <button type="submit" className="btn-primary">Iniciar</button>
            </div>
          </form>
        </div>
      )}

      {/* Table */}
      {loading ? (
        <div className="flex justify-center py-16"><div className="spinner w-8 h-8" /></div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr>
                  <th>Máquina</th><th>Tipo</th><th>Molde</th><th>Operador</th>
                  <th className="text-right">Duração</th><th>Status</th><th>Início</th><th></th>
                </tr>
              </thead>
              <tbody>
                {setups.length === 0 ? (
                  <tr><td colSpan={8} className="text-center text-surface-400 py-8">Nenhum setup registrado</td></tr>
                ) : setups.map(s => (
                  <tr key={s.id}>
                    <td className="font-mono font-semibold text-sm">{s.machine_code}</td>
                    <td>{setupTypeBadge(s.setup_type)}</td>
                    <td className="text-surface-500 text-sm">{s.mold_from || '—'} → {s.mold_to || '—'}</td>
                    <td className="text-surface-500 text-sm">{s.operator_name || '—'}</td>
                    <td className="text-right tabular-nums font-medium">{s.duration_minutes ? `${s.duration_minutes} min` : '—'}</td>
                    <td>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${
                        s.status === 'em_andamento' ? 'bg-amber-50 text-amber-700 ring-amber-200 animate-pulse' :
                        s.status === 'concluido' ? 'bg-emerald-50 text-emerald-700 ring-emerald-200' :
                        'bg-surface-100 text-surface-600 ring-surface-200'
                      }`}>{s.status === 'em_andamento' ? 'Em Andamento' : s.status === 'concluido' ? 'Concluído' : s.status}</span>
                    </td>
                    <td className="text-surface-400 text-xs tabular-nums">{s.start_time ? new Date(s.start_time).toLocaleString('pt-BR') : '—'}</td>
                    <td>
                      {s.status === 'em_andamento' && (
                        <button onClick={() => handleFinish(s.id)}
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
