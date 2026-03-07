import { useState, useEffect } from 'react';
import api from '../services/api';
import { Package, Users, Settings2, Plus, Wrench } from 'lucide-react';

const TABS = [
  { key: 'products', label: 'Produtos', icon: Package },
  { key: 'operators', label: 'Operadores', icon: Users },
  { key: 'machines', label: 'Máquinas', icon: Settings2 },
  { key: 'molds', label: 'Moldes', icon: Wrench },
] as const;

type TabKey = typeof TABS[number]['key'];

const DATA_ENDPOINTS: Record<TabKey, string> = {
  products: '/admin/products',
  operators: '/admin/operators',
  machines: '/admin/machines-admin',
  molds: '/admin/molds-admin',
};

const CREATE_ENDPOINTS: Partial<Record<TabKey, string>> = {
  products: '/admin/products',
  operators: '/admin/operators',
};

export default function AdminData() {
  const [tab, setTab] = useState<TabKey>('products');
  const [data, setData] = useState<Array<Record<string, any>>>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<Record<string, unknown>>({});

  useEffect(() => { fetchData(); }, [tab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const { data: result } = await api.get(DATA_ENDPOINTS[tab]);
      setData(result);
    } catch (err) {
      console.error(err);
      setData([]);
    }
    finally { setLoading(false); }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const endpoint = CREATE_ENDPOINTS[tab];
      if (endpoint) {
        await api.post(endpoint, form);
        setShowForm(false);
        setForm({});
        fetchData();
      }
    } catch (err) { console.error(err); }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">Admin — Dados Mestres</h1>
          <p className="page-subtitle">Gestão de produtos, operadores, máquinas e moldes</p>
        </div>
        {(tab === 'products' || tab === 'operators') && (
          <button onClick={() => { setShowForm(!showForm); setForm({}); }} className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" /> Novo
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="tab-bar w-fit">
        {TABS.map(t => (
          <button key={t.key} onClick={() => { setTab(t.key); setShowForm(false); }}
            className={tab === t.key ? 'tab-item-active' : 'tab-item'}>
            <t.icon className="w-4 h-4 inline mr-1.5 -mt-0.5" />{t.label}
          </button>
        ))}
      </div>

      {/* Form */}
      {showForm && tab === 'products' && (
        <div className="card border-2 border-primary-200 animate-slide-up">
          <h3 className="text-sm font-semibold text-surface-800 mb-4">Novo Produto</h3>
          <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input type="text" placeholder="Código (ex: TFT-28)" required value={(form.code as string) || ''} onChange={e => setForm({...form, code: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <input type="text" placeholder="Descrição" value={(form.description as string) || ''} onChange={e => setForm({...form, description: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <input type="number" step="0.1" placeholder="Peso (g)" value={(form.weight as number) || ''} onChange={e => setForm({...form, weight: parseFloat(e.target.value)})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <div className="md:col-span-3 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-sm font-medium text-surface-600 hover:bg-surface-100">Cancelar</button>
              <button type="submit" className="btn-primary">Criar</button>
            </div>
          </form>
        </div>
      )}

      {showForm && tab === 'operators' && (
        <div className="card border-2 border-primary-200 animate-slide-up">
          <h3 className="text-sm font-semibold text-surface-800 mb-4">Novo Operador</h3>
          <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input type="text" placeholder="Matrícula (ex: OP-016)" required value={(form.registration as string) || ''} onChange={e => setForm({...form, registration: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <input type="text" placeholder="Nome completo" required value={(form.name as string) || ''} onChange={e => setForm({...form, name: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <select value={(form.shift as string) || 'A'} onChange={e => setForm({...form, shift: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none">
              <option value="A">Turno A</option>
              <option value="B">Turno B</option>
              <option value="C">Turno C</option>
            </select>
            <div className="md:col-span-3 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-sm font-medium text-surface-600 hover:bg-surface-100">Cancelar</button>
              <button type="submit" className="btn-primary">Criar</button>
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
                {tab === 'products' && <tr><th>Código</th><th>Descrição</th><th className="text-right">Peso (g)</th><th className="text-right">Ciclo (s)</th></tr>}
                {tab === 'operators' && <tr><th>Matrícula</th><th>Nome</th><th>Turno</th><th>Status</th></tr>}
                {tab === 'machines' && <tr><th>Código</th><th>Nome</th><th>Tipo</th><th>Tonelagem</th><th>Status</th></tr>}
                {tab === 'molds' && <tr><th>Código</th><th>Descrição</th><th className="text-right">Cavidades</th><th className="text-right">Batidas</th><th>Status</th></tr>}
              </thead>
              <tbody>
                {data.length === 0 ? (
                  <tr><td colSpan={5} className="text-center text-surface-400 py-8">Nenhum registro encontrado</td></tr>
                ) : (
                  <>
                    {tab === 'products' && data.map(d => (
                      <tr key={d.id}>
                        <td className="font-mono font-semibold text-primary-600 text-sm">{d.code}</td>
                        <td className="text-surface-700">{d.description || d.name || '—'}</td>
                        <td className="text-right tabular-nums">{d.weight_grams || d.weight || '—'}</td>
                        <td className="text-right tabular-nums">{d.cycle_time_ideal || d.cycle_time || '—'}</td>
                      </tr>
                    ))}
                    {tab === 'operators' && data.map(d => (
                      <tr key={d.id}>
                        <td className="font-mono font-semibold text-sm">{d.registration}</td>
                        <td className="text-surface-700 font-medium">{d.name}</td>
                        <td><span className="inline-flex items-center px-1.5 py-0.5 rounded bg-surface-100 text-xs font-medium text-surface-600">{d.shift}</span></td>
                        <td>{d.active !== false ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 bg-emerald-50 text-emerald-700 ring-emerald-200 uppercase">Ativo</span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 bg-surface-100 text-surface-500 ring-surface-200 uppercase">Inativo</span>
                        )}</td>
                      </tr>
                    ))}
                    {tab === 'machines' && data.map(d => (
                      <tr key={d.id}>
                        <td className="font-mono font-semibold text-sm">{d.code}</td>
                        <td className="text-surface-700">{d.name}</td>
                        <td className="text-surface-500 text-sm uppercase">{d.type}</td>
                        <td className="tabular-nums">{d.tonnage || '—'}t</td>
                        <td>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${
                            d.status === 'running' ? 'bg-emerald-50 text-emerald-700 ring-emerald-200' :
                            d.status === 'maintenance' ? 'bg-red-50 text-red-700 ring-red-200' :
                            'bg-surface-100 text-surface-600 ring-surface-200'
                          }`}>{d.status}</span>
                        </td>
                      </tr>
                    ))}
                    {tab === 'molds' && data.map(d => (
                      <tr key={d.id}>
                        <td className="font-mono font-semibold text-sm">{d.code}</td>
                        <td className="text-surface-700">{d.description || d.name || '—'}</td>
                        <td className="text-right tabular-nums">{d.cavities}</td>
                        <td className="text-right tabular-nums">{d.current_shots?.toLocaleString('pt-BR') || '—'} / {d.max_shots?.toLocaleString('pt-BR') || '—'}</td>
                        <td className="text-surface-500 text-sm capitalize">{d.status || '—'}</td>
                      </tr>
                    ))}
                  </>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
