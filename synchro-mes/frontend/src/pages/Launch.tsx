import { useState, useEffect } from 'react';
import api from '../services/api';
import { Play, Square, Gauge, Timer, Plus, ChevronDown } from 'lucide-react';

export default function Launch() {
  const [machines, setMachines] = useState<any[]>([]);
  const [selectedMachine, setSelectedMachine] = useState<string | null>(null);
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ product_code: '', operator_name: '', shift: 'A', quantity_good: '', quantity_rejected: '', cycle_time_actual: '' });

  useEffect(() => { fetchMachines(); }, []);
  useEffect(() => { if (selectedMachine) fetchEntries(); }, [selectedMachine]);

  const fetchMachines = async () => {
    try {
      const { data } = await api.get('/machines');
      setMachines(data);
      if (data.length > 0) setSelectedMachine(data[0].code);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const fetchEntries = async () => {
    try {
      const { data } = await api.get(`/production/entries?machine_code=${selectedMachine}&limit=20`);
      setEntries(data);
    } catch (err) { console.error(err); }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/production/entries', {
        machine_code: selectedMachine,
        product_code: form.product_code,
        operator_name: form.operator_name,
        shift: form.shift,
        quantity_good: parseInt(form.quantity_good) || 0,
        quantity_rejected: parseInt(form.quantity_rejected) || 0,
        cycle_time_actual: parseFloat(form.cycle_time_actual) || 0,
      });
      setShowForm(false);
      setForm({ product_code: '', operator_name: '', shift: 'A', quantity_good: '', quantity_rejected: '', cycle_time_actual: '' });
      fetchEntries();
    } catch (err) { console.error(err); }
  };

  const machine = machines.find(m => m.code === selectedMachine);

  const statusColors: Record<string, string> = {
    running: 'bg-emerald-500',
    stopped: 'bg-red-500',
    idle: 'bg-surface-400',
    maintenance: 'bg-amber-500',
    setup: 'bg-blue-500',
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">Lançamento de Produção</h1>
          <p className="page-subtitle">Registre produção por máquina em tempo real</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Novo Lançamento
        </button>
      </div>

      {/* Machine Selector */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-10 gap-2">
        {machines.map(m => (
          <button key={m.code} onClick={() => setSelectedMachine(m.code)}
            className={`card text-center p-3 transition-all cursor-pointer border-2 ${
              m.code === selectedMachine ? 'border-primary-500 shadow-glow-primary' : 'border-transparent hover:border-surface-200'
            }`}>
            <div className={`w-2.5 h-2.5 rounded-full mx-auto mb-1.5 ${statusColors[m.status] || 'bg-surface-400'}`} />
            <p className="font-mono text-xs font-bold text-surface-800">{m.code}</p>
            <p className="text-[10px] text-surface-400 mt-0.5 uppercase">{m.status}</p>
          </button>
        ))}
      </div>

      {/* Machine KPIs */}
      {machine && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card text-center">
            <Gauge className="w-5 h-5 mx-auto text-primary-500 mb-1" />
            <p className="text-xs text-surface-400">Eficiência</p>
            <p className="text-2xl font-bold text-primary-600">{machine.efficiency?.toFixed(1) || '—'}%</p>
          </div>
          <div className="card text-center">
            <Timer className="w-5 h-5 mx-auto text-blue-500 mb-1" />
            <p className="text-xs text-surface-400">Ciclo Atual</p>
            <p className="text-2xl font-bold text-blue-600">{machine.cycle_time_seconds?.toFixed(1) || '—'}s</p>
          </div>
          <div className="card text-center">
            <Play className="w-5 h-5 mx-auto text-emerald-500 mb-1" />
            <p className="text-xs text-surface-400">Produto</p>
            <p className="text-lg font-bold text-emerald-600">{machine.current_product || '—'}</p>
          </div>
          <div className="card text-center">
            <Square className="w-5 h-5 mx-auto text-amber-500 mb-1" />
            <p className="text-xs text-surface-400">Operador</p>
            <p className="text-sm font-semibold text-surface-700 truncate">{machine.current_operator || '—'}</p>
          </div>
        </div>
      )}

      {/* Formulário de Lançamento */}
      {showForm && (
        <div className="card border-2 border-primary-200 animate-slide-up">
          <h3 className="text-sm font-semibold text-surface-800 mb-4">Novo Lançamento — {selectedMachine}</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Produto</label>
              <input type="text" value={form.product_code} onChange={e => setForm({...form, product_code: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" placeholder="Ex: TFT-28" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Operador</label>
              <input type="text" value={form.operator_name} onChange={e => setForm({...form, operator_name: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" placeholder="Nome" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Turno</label>
              <select value={form.shift} onChange={e => setForm({...form, shift: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none">
                <option value="A">Turno A</option>
                <option value="B">Turno B</option>
                <option value="C">Turno C</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Peças Boas</label>
              <input type="number" value={form.quantity_good} onChange={e => setForm({...form, quantity_good: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" placeholder="0" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Refugo</label>
              <input type="number" value={form.quantity_rejected} onChange={e => setForm({...form, quantity_rejected: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" placeholder="0" />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Ciclo Real (s)</label>
              <input type="number" step="0.1" value={form.cycle_time_actual} onChange={e => setForm({...form, cycle_time_actual: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" placeholder="0.0" />
            </div>
            <div className="md:col-span-3 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-sm font-medium text-surface-600 hover:bg-surface-100 transition-colors">Cancelar</button>
              <button type="submit" className="btn-primary">Registrar</button>
            </div>
          </form>
        </div>
      )}

      {/* Últimos Lançamentos */}
      <div className="card p-0 overflow-hidden">
        <div className="px-4 py-3 border-b border-surface-100">
          <h3 className="text-sm font-semibold text-surface-800">Últimos Lançamentos — {selectedMachine}</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="table-modern">
            <thead>
              <tr>
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
              {entries.length === 0 ? (
                <tr><td colSpan={7} className="text-center text-surface-400 py-8">Nenhum lançamento encontrado</td></tr>
              ) : entries.map((e) => (
                <tr key={e.id}>
                  <td className="font-medium text-surface-800">{e.product_code}</td>
                  <td className="text-surface-500">{e.operator_name || '—'}</td>
                  <td><span className="inline-flex items-center px-1.5 py-0.5 rounded bg-surface-100 text-xs font-medium text-surface-600">{e.shift || '—'}</span></td>
                  <td className="text-right tabular-nums text-emerald-600 font-semibold">{e.quantity_good}</td>
                  <td className="text-right tabular-nums text-red-600 font-medium">{e.quantity_rejected}</td>
                  <td className="text-right tabular-nums text-surface-500">{e.cycle_time_actual?.toFixed(1) || '—'}s</td>
                  <td className="text-surface-400 text-xs tabular-nums">{e.timestamp ? new Date(e.timestamp).toLocaleString('pt-BR') : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
