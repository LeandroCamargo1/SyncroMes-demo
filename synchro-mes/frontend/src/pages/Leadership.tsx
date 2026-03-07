import { useState, useEffect } from 'react';
import api from '../services/api';
import { Users, Calendar, UserX, Plus, ClipboardList } from 'lucide-react';

export default function Leadership() {
  const [tab, setTab] = useState('schedule');
  const [schedule, setSchedule] = useState<any[]>([]);
  const [absences, setAbsences] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ operator_registration: '', operator_name: '', date: '', shift: 'A', machine_code: '', position: 'operador' });
  const [absForm, setAbsForm] = useState({ operator_registration: '', operator_name: '', date: '', shift: 'A', reason: 'falta', hours_absent: '', justified: false, notes: '' });

  useEffect(() => { fetchData(); }, [tab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [sched, abs, summ] = await Promise.all([
        api.get('/leadership/schedule'),
        api.get('/leadership/absenteeism'),
        api.get('/leadership/summary'),
      ]);
      setSchedule(sched.data);
      setAbsences(abs.data);
      setSummary(summ.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleCreateSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/leadership/schedule', form);
      setShowForm(false);
      fetchData();
    } catch (err) { console.error(err); }
  };

  const handleCreateAbsence = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/leadership/absenteeism', { ...absForm, hours_absent: parseFloat(absForm.hours_absent) || 0 });
      setShowForm(false);
      fetchData();
    } catch (err) { console.error(err); }
  };

  const reasonLabels: Record<string, string> = { falta: 'Falta', atestado: 'Atestado', atraso: 'Atraso', ferias: 'Férias', folga: 'Folga' };
  const reasonBadge = (reason: string) => {
    const map: Record<string, string> = {
      falta: 'bg-red-50 text-red-700 ring-red-200',
      atestado: 'bg-amber-50 text-amber-700 ring-amber-200',
      atraso: 'bg-orange-50 text-orange-700 ring-orange-200',
      ferias: 'bg-blue-50 text-blue-700 ring-blue-200',
      folga: 'bg-surface-100 text-surface-600 ring-surface-200',
    };
    return <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${map[reason] || 'bg-surface-100 text-surface-600 ring-surface-200'}`}>{reasonLabels[reason] || reason}</span>;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">Liderança</h1>
          <p className="page-subtitle">Escala de operadores e controle de absenteísmo</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Novo Registro
        </button>
      </div>

      {/* KPI */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card text-center">
          <Calendar className="w-5 h-5 mx-auto text-primary-500 mb-1" />
          <p className="text-xs text-surface-400">Escalas</p>
          <p className="text-2xl font-bold text-primary-600">{summary.total_scheduled || 0}</p>
        </div>
        <div className="card text-center">
          <UserX className="w-5 h-5 mx-auto text-red-500 mb-1" />
          <p className="text-xs text-surface-400">Ausências</p>
          <p className="text-2xl font-bold text-red-600">{summary.total_absences || 0}</p>
        </div>
        <div className="card text-center">
          <ClipboardList className="w-5 h-5 mx-auto text-emerald-500 mb-1" />
          <p className="text-xs text-surface-400">Justificadas</p>
          <p className="text-2xl font-bold text-emerald-600">{summary.justified_absences || 0}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="tab-bar w-fit">
        <button onClick={() => { setTab('schedule'); setShowForm(false); }} className={tab === 'schedule' ? 'tab-item-active' : 'tab-item'}>
          <Users className="w-4 h-4 inline mr-1.5 -mt-0.5" />Escala
        </button>
        <button onClick={() => { setTab('absenteeism'); setShowForm(false); }} className={tab === 'absenteeism' ? 'tab-item-active' : 'tab-item'}>
          <UserX className="w-4 h-4 inline mr-1.5 -mt-0.5" />Absenteísmo
        </button>
      </div>

      {/* Forms */}
      {showForm && tab === 'schedule' && (
        <div className="card border-2 border-primary-200 animate-slide-up">
          <h3 className="text-sm font-semibold text-surface-800 mb-4">Nova Escala</h3>
          <form onSubmit={handleCreateSchedule} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input type="text" placeholder="Matrícula" required value={form.operator_registration} onChange={e => setForm({...form, operator_registration: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <input type="text" placeholder="Nome" required value={form.operator_name} onChange={e => setForm({...form, operator_name: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <input type="date" required value={form.date} onChange={e => setForm({...form, date: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <select value={form.shift} onChange={e => setForm({...form, shift: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none">
              <option value="A">Turno A</option><option value="B">Turno B</option><option value="C">Turno C</option>
            </select>
            <input type="text" placeholder="Máquina (INJ-01)" value={form.machine_code} onChange={e => setForm({...form, machine_code: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <select value={form.position} onChange={e => setForm({...form, position: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none">
              <option value="operador">Operador</option><option value="lider">Líder</option><option value="auxiliar">Auxiliar</option>
            </select>
            <div className="md:col-span-3 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-sm text-surface-600 hover:bg-surface-100">Cancelar</button>
              <button type="submit" className="btn-primary">Criar</button>
            </div>
          </form>
        </div>
      )}

      {showForm && tab === 'absenteeism' && (
        <div className="card border-2 border-primary-200 animate-slide-up">
          <h3 className="text-sm font-semibold text-surface-800 mb-4">Nova Ausência</h3>
          <form onSubmit={handleCreateAbsence} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input type="text" placeholder="Matrícula" required value={absForm.operator_registration} onChange={e => setAbsForm({...absForm, operator_registration: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <input type="text" placeholder="Nome" required value={absForm.operator_name} onChange={e => setAbsForm({...absForm, operator_name: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <input type="date" required value={absForm.date} onChange={e => setAbsForm({...absForm, date: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <select value={absForm.reason} onChange={e => setAbsForm({...absForm, reason: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none">
              <option value="falta">Falta</option><option value="atestado">Atestado</option><option value="atraso">Atraso</option>
              <option value="ferias">Férias</option><option value="folga">Folga</option>
            </select>
            <input type="number" step="0.5" placeholder="Horas" value={absForm.hours_absent} onChange={e => setAbsForm({...absForm, hours_absent: e.target.value})}
              className="px-3 py-2 rounded-lg border border-surface-200 text-sm focus:ring-2 focus:ring-primary-500/30 focus:outline-none" />
            <label className="flex items-center gap-2 text-sm text-surface-600">
              <input type="checkbox" checked={absForm.justified} onChange={e => setAbsForm({...absForm, justified: e.target.checked})} className="rounded border-surface-300" />
              Justificada
            </label>
            <div className="md:col-span-3 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-sm text-surface-600 hover:bg-surface-100">Cancelar</button>
              <button type="submit" className="btn-primary">Registrar</button>
            </div>
          </form>
        </div>
      )}

      {/* Table */}
      {loading ? (
        <div className="flex justify-center py-16"><div className="spinner w-8 h-8" /></div>
      ) : tab === 'schedule' ? (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr><th>Matrícula</th><th>Nome</th><th>Data</th><th>Turno</th><th>Máquina</th><th>Posição</th></tr>
              </thead>
              <tbody>
                {schedule.length === 0 ? (
                  <tr><td colSpan={6} className="text-center text-surface-400 py-8">Nenhuma escala registrada</td></tr>
                ) : schedule.map(s => (
                  <tr key={s.id}>
                    <td className="font-mono text-sm font-semibold">{s.operator_registration}</td>
                    <td className="font-medium text-surface-700">{s.operator_name}</td>
                    <td className="text-surface-500 tabular-nums text-sm">{s.date}</td>
                    <td><span className="inline-flex items-center px-1.5 py-0.5 rounded bg-surface-100 text-xs font-medium text-surface-600">{s.shift}</span></td>
                    <td className="font-mono text-xs text-surface-500">{s.machine_code || '—'}</td>
                    <td className="text-surface-500 capitalize text-sm">{s.position}</td>
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
                <tr><th>Matrícula</th><th>Nome</th><th>Data</th><th>Turno</th><th>Motivo</th><th className="text-right">Horas</th><th>Justificada</th></tr>
              </thead>
              <tbody>
                {absences.length === 0 ? (
                  <tr><td colSpan={7} className="text-center text-surface-400 py-8">Nenhuma ausência registrada</td></tr>
                ) : absences.map((a) => (
                  <tr key={a.id}>
                    <td className="font-mono text-sm font-semibold">{a.operator_registration}</td>
                    <td className="font-medium text-surface-700">{a.operator_name}</td>
                    <td className="text-surface-500 tabular-nums text-sm">{a.date}</td>
                    <td><span className="inline-flex items-center px-1.5 py-0.5 rounded bg-surface-100 text-xs font-medium text-surface-600">{a.shift}</span></td>
                    <td>{reasonBadge(a.reason)}</td>
                    <td className="text-right tabular-nums">{a.hours_absent}h</td>
                    <td>{a.justified ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 bg-emerald-50 text-emerald-700 ring-emerald-200 uppercase">Sim</span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 bg-red-50 text-red-700 ring-red-200 uppercase">Não</span>
                    )}</td>
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
