import { useState, useEffect, useMemo } from 'react';
import api from '../services/api';
import { Recycle, Trash2, Scale, Plus } from 'lucide-react';
import { DonutChart } from '../components/charts';

const TYPE_LABELS: Record<string, string> = { moido: 'Moído', borra: 'Borra', sucata: 'Sucata' };
const DEST_LABELS: Record<string, string> = { reprocesso: 'Reprocesso', descarte: 'Descarte', venda: 'Venda' };

export default function Pmp() {
  const [entries, setEntries] = useState<any[]>([]);
  const [summary, setSummary] = useState<any[]>([]);
  const [tab, setTab] = useState('list');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ type: 'moido', machine_code: '', weight_kg: '', destination: 'reprocesso', material: '', operator_name: '', notes: '' });

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [e, s] = await Promise.all([api.get('/pmp'), api.get('/pmp/summary')]);
      setEntries(e.data);
      setSummary(s.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/pmp', { ...form, weight_kg: parseFloat(form.weight_kg) || 0 });
      setShowForm(false);
      setForm({ type: 'moido', machine_code: '', weight_kg: '', destination: 'reprocesso', material: '', operator_name: '', notes: '' });
      fetchData();
    } catch (err) { console.error(err); }
  };

  const typeBadge = (type: string) => {
    const map: Record<string, string> = {
      moido: 'bg-blue-50 text-blue-700 ring-blue-200',
      borra: 'bg-amber-50 text-amber-700 ring-amber-200',
      sucata: 'bg-red-50 text-red-700 ring-red-200',
    };
    return <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${map[type] || 'bg-surface-100 text-surface-600 ring-surface-200'}`}>{TYPE_LABELS[type] || type}</span>;
  };

  const typeIcons: Record<string, any> = { moido: Recycle, borra: Scale, sucata: Trash2 };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">PMP — Moído / Borra / Sucata</h1>
          <p className="page-subtitle">Controle de perdas de matéria-prima</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Novo Registro
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {['moido', 'borra', 'sucata'].map(type => {
          const s = summary.find(x => x.type === type);
          const Icon = typeIcons[type];
          return (
            <div key={type} className="card">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${type === 'moido' ? 'bg-blue-100' : type === 'borra' ? 'bg-amber-100' : 'bg-red-100'}`}>
                  <Icon className={`w-5 h-5 ${type === 'moido' ? 'text-blue-600' : type === 'borra' ? 'text-amber-600' : 'text-red-600'}`} />
                </div>
                <div>
                  <p className="text-xs text-surface-400 font-medium uppercase">{TYPE_LABELS[type]}</p>
                  <p className="text-xl font-bold text-surface-800">{s?.total_kg?.toFixed(1) || '0'} <span className="text-sm font-normal text-surface-400">kg</span></p>
                  <p className="text-xs text-surface-400">{s?.count || 0} registros</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Donut Chart — Peso por tipo */}
      {!loading && summary.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-sm font-semibold text-surface-800 mb-1">Distribuição por Tipo</h3>
            <p className="text-xs text-surface-400 mb-4">Peso total (kg) por categoria</p>
            <DonutChart
              data={summary.map((s: any) => ({ name: TYPE_LABELS[s.type] || s.type, value: parseFloat(s.total_kg?.toFixed(1)) || 0 }))}
              colors={['#3b82f6', '#f59e0b', '#ef4444']}
              innerValue={`${summary.reduce((s: number, x: any) => s + (x.total_kg || 0), 0).toFixed(1)}`}
              innerLabel="kg total"
            />
          </div>
          <div className="card">
            <h3 className="text-sm font-semibold text-surface-800 mb-1">Destinos</h3>
            <p className="text-xs text-surface-400 mb-4">Distribuição por destino do material</p>
            <DonutChart
              data={(() => {
                const m: Record<string, number> = {};
                entries.forEach((e: any) => { m[DEST_LABELS[e.destination] || e.destination] = (m[DEST_LABELS[e.destination] || e.destination] || 0) + (e.weight_kg || 0); });
                return Object.entries(m).map(([name, value]) => ({ name, value: parseFloat(value.toFixed(1)) }));
              })()}
              colors={['#10b981', '#94a3b8', '#8b5cf6']}
              innerValue={String(entries.length)}
              innerLabel="registros"
            />
          </div>
        </div>
      )}

      {/* Formulário */}
      {showForm && (
        <div className="card border-2 border-primary-200 animate-slide-up">
          <h3 className="text-sm font-semibold text-surface-800 mb-4">Novo Registro PMP</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Tipo</label>
              <select value={form.type} onChange={e => setForm({...form, type: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none">
                <option value="moido">Moído</option>
                <option value="borra">Borra</option>
                <option value="sucata">Sucata</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Máquina</label>
              <input type="text" value={form.machine_code} onChange={e => setForm({...form, machine_code: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" placeholder="INJ-01" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Peso (kg)</label>
              <input type="number" step="0.1" value={form.weight_kg} onChange={e => setForm({...form, weight_kg: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" placeholder="0.0" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Destino</label>
              <select value={form.destination} onChange={e => setForm({...form, destination: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none">
                <option value="reprocesso">Reprocesso</option>
                <option value="descarte">Descarte</option>
                <option value="venda">Venda</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Material</label>
              <input type="text" value={form.material} onChange={e => setForm({...form, material: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" placeholder="PP, PET..." />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Operador</label>
              <input type="text" value={form.operator_name} onChange={e => setForm({...form, operator_name: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" placeholder="Nome" />
            </div>
            <div className="md:col-span-3 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-sm font-medium text-surface-600 hover:bg-surface-100 transition-colors">Cancelar</button>
              <button type="submit" className="btn-primary">Registrar</button>
            </div>
          </form>
        </div>
      )}

      {/* Tabela */}
      {loading ? (
        <div className="flex justify-center py-16"><div className="spinner w-8 h-8" /></div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr><th>Tipo</th><th>Máquina</th><th className="text-right">Peso (kg)</th><th>Destino</th><th>Material</th><th>Operador</th><th>Data</th></tr>
              </thead>
              <tbody>
                {entries.length === 0 ? (
                  <tr><td colSpan={7} className="text-center text-surface-400 py-8">Nenhum registro PMP encontrado</td></tr>
                ) : entries.map(e => (
                  <tr key={e.id}>
                    <td>{typeBadge(e.type)}</td>
                    <td className="font-mono text-sm font-semibold">{e.machine_code}</td>
                    <td className="text-right tabular-nums font-semibold">{e.weight_kg?.toFixed(1)}</td>
                    <td className="text-surface-500 text-sm">{DEST_LABELS[e.destination] || e.destination}</td>
                    <td className="text-surface-500 text-sm">{e.material || '—'}</td>
                    <td className="text-surface-400 text-sm">{e.operator_name || '—'}</td>
                    <td className="text-surface-400 text-xs tabular-nums">{e.created_at ? new Date(e.created_at).toLocaleString('pt-BR') : '—'}</td>
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
