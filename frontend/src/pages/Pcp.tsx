import { useState, useEffect } from 'react';
import api from '../services/api';
import { Megaphone, ListOrdered, Plus, Bell, AlertTriangle, Info, Zap } from 'lucide-react';

export default function Pcp() {
  const [tab, setTab] = useState('queue');
  const [queue, setQueue] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ message: '', priority: 3, type: 'info', target_machine: '' });

  useEffect(() => { fetchData(); }, [tab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [q, m] = await Promise.all([
        api.get('/pcp/queue'),
        api.get('/pcp/messages'),
      ]);
      setQueue(q.data);
      setMessages(m.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleCreateMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/pcp/messages', { ...form, priority: Number(form.priority), target_machine: form.target_machine || null });
      setShowForm(false);
      setForm({ message: '', priority: 3, type: 'info', target_machine: '' });
      fetchData();
    } catch (err) { console.error(err); }
  };

  const handleDeactivate = async (id: number) => {
    try {
      await api.patch(`/pcp/messages/${id}/deactivate`);
      fetchData();
    } catch (err) { console.error(err); }
  };

  const typeIcons: Record<string, any> = { info: Info, warning: AlertTriangle, urgent: Zap };
  const typeColors: Record<string, string> = {
    info: 'bg-blue-50 text-blue-700 ring-blue-200 border-l-blue-500',
    warning: 'bg-amber-50 text-amber-700 ring-amber-200 border-l-amber-500',
    urgent: 'bg-red-50 text-red-700 ring-red-200 border-l-red-500',
  };

  const priorityBadge = (p: number) => {
    const map: Record<number, string> = {
      1: 'bg-red-50 text-red-700 ring-red-200',
      2: 'bg-amber-50 text-amber-700 ring-amber-200',
      3: 'bg-surface-100 text-surface-600 ring-surface-200',
    };
    const cfg = map[p] || map[3];
    return <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${cfg}`}>{p}</span>;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">PCP</h1>
          <p className="page-subtitle">Planejamento e Controle da Produção</p>
        </div>
        {tab === 'messages' && (
          <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" /> Nova Mensagem
          </button>
        )}
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card text-center">
          <ListOrdered className="w-5 h-5 mx-auto text-primary-500 mb-1" />
          <p className="text-xs text-surface-400">Ordens na Fila</p>
          <p className="text-2xl font-bold text-primary-600">{queue.length}</p>
        </div>
        <div className="card text-center">
          <Bell className="w-5 h-5 mx-auto text-amber-500 mb-1" />
          <p className="text-xs text-surface-400">Mensagens Ativas</p>
          <p className="text-2xl font-bold text-amber-600">{messages.filter(m => m.is_active).length}</p>
        </div>
        <div className="card text-center">
          <Zap className="w-5 h-5 mx-auto text-red-500 mb-1" />
          <p className="text-xs text-surface-400">Urgentes</p>
          <p className="text-2xl font-bold text-red-600">{messages.filter(m => m.type === 'urgent' && m.is_active).length}</p>
        </div>
        <div className="card text-center">
          <Megaphone className="w-5 h-5 mx-auto text-blue-500 mb-1" />
          <p className="text-xs text-surface-400">Total Mensagens</p>
          <p className="text-2xl font-bold text-blue-600">{messages.length}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="tab-bar w-fit">
        <button onClick={() => { setTab('queue'); setShowForm(false); }} className={tab === 'queue' ? 'tab-item-active' : 'tab-item'}>
          <ListOrdered className="w-4 h-4 inline mr-1.5 -mt-0.5" />Fila de Produção
        </button>
        <button onClick={() => { setTab('messages'); setShowForm(false); }} className={tab === 'messages' ? 'tab-item-active' : 'tab-item'}>
          <Megaphone className="w-4 h-4 inline mr-1.5 -mt-0.5" />Mensagens
        </button>
      </div>

      {/* Message Form */}
      {showForm && (
        <div className="card border-2 border-primary-200 animate-slide-up">
          <h3 className="text-sm font-semibold text-surface-800 mb-4">Nova Mensagem PCP</h3>
          <form onSubmit={handleCreateMessage} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-xs font-medium text-surface-500 mb-1">Mensagem</label>
              <input type="text" required value={form.message} onChange={e => setForm({...form, message: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" placeholder="Texto da mensagem..." />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Tipo</label>
              <select value={form.type} onChange={e => setForm({...form, type: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none">
                <option value="info">Informação</option>
                <option value="warning">Aviso</option>
                <option value="urgent">Urgente</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Prioridade (1-5)</label>
              <input type="number" min="1" max="5" value={form.priority} onChange={e => setForm({...form, priority: Number(e.target.value)})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 mb-1">Máquina Alvo (opcional)</label>
              <input type="text" value={form.target_machine} onChange={e => setForm({...form, target_machine: e.target.value})}
                className="w-full px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" placeholder="INJ-01" />
            </div>
            <div className="md:col-span-2 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-sm text-surface-600 hover:bg-surface-100">Cancelar</button>
              <button type="submit" className="btn-primary">Enviar</button>
            </div>
          </form>
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="flex justify-center py-16"><div className="spinner w-8 h-8" /></div>
      ) : tab === 'queue' ? (
        <div className="card p-0 overflow-hidden">
          <div className="px-4 py-3 border-b border-surface-100">
            <h3 className="text-sm font-semibold text-surface-800">Fila de Produção (ordenada por prioridade)</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr><th>#</th><th>Ordem</th><th>Produto</th><th>Máquina</th><th>Prioridade</th><th className="text-right">Planejado</th><th className="text-right">Produzido</th><th>Status</th></tr>
              </thead>
              <tbody>
                {queue.length === 0 ? (
                  <tr><td colSpan={8} className="text-center text-surface-400 py-8">Fila vazia</td></tr>
                ) : queue.map((o, i) => (
                  <tr key={o.id}>
                    <td className="font-mono text-xs text-surface-400">{i + 1}</td>
                    <td className="font-mono font-semibold text-primary-600 text-sm">{o.order_number}</td>
                    <td className="font-medium text-surface-800">{o.product_code}</td>
                    <td className="font-mono text-xs text-surface-500">{o.machine_code || '—'}</td>
                    <td>{priorityBadge(o.priority)}</td>
                    <td className="text-right tabular-nums">{o.quantity_planned?.toLocaleString('pt-BR')}</td>
                    <td className="text-right tabular-nums font-medium">{o.quantity_produced?.toLocaleString('pt-BR')}</td>
                    <td>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${
                        o.status === 'em_producao' ? 'bg-emerald-50 text-emerald-700 ring-emerald-200' :
                        'bg-blue-50 text-blue-700 ring-blue-200'
                      }`}>{o.status === 'em_producao' ? 'Em Produção' : 'Planejada'}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {messages.length === 0 ? (
            <div className="card text-center py-12">
              <Megaphone className="w-12 h-12 mx-auto text-surface-300 mb-3" />
              <h3 className="text-base font-semibold text-surface-800">Nenhuma mensagem</h3>
            </div>
          ) : messages.map(m => {
            const Icon = typeIcons[m.type] || Info;
            const colors = typeColors[m.type] || typeColors.info;
            return (
              <div key={m.id} className={`card flex items-start gap-3 border-l-4 ${colors} ${!m.is_active ? 'opacity-50' : ''}`}>
                <Icon className="w-5 h-5 mt-0.5 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-surface-800">{m.message}</p>
                  <div className="flex items-center gap-3 mt-1.5 text-xs text-surface-400">
                    <span>Prioridade: {m.priority}</span>
                    {m.target_machine && <span>Máquina: <span className="font-mono">{m.target_machine}</span></span>}
                    <span>{m.created_at ? new Date(m.created_at).toLocaleString('pt-BR') : ''}</span>
                  </div>
                </div>
                {m.is_active && (
                  <button onClick={() => handleDeactivate(m.id)}
                    className="text-xs font-medium text-surface-400 hover:text-red-600 transition-colors shrink-0">
                    Desativar
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
