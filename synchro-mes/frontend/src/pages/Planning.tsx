import { useState, useEffect } from 'react';
import api from '../services/api';
import { Calendar, ChevronLeft, ChevronRight, Clock, Layers, Box } from 'lucide-react';

export default function Planning() {
  const [planning, setPlanning] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().split('T')[0]);

  useEffect(() => {
    fetchPlanning();
  }, [selectedDate]);

  const fetchPlanning = async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/production/planning?target_date=${selectedDate}`);
      setPlanning(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const changeDate = (days: number) => {
    const d = new Date(selectedDate);
    d.setDate(d.getDate() + days);
    setSelectedDate(d.toISOString().split('T')[0]);
  };

  // Agrupar por máquina
  const byMachine = planning.reduce<Record<string, any[]>>((acc, p) => {
    if (!acc[p.machine_code]) acc[p.machine_code] = [];
    acc[p.machine_code].push(p);
    return acc;
  }, {});

  const dateDisplay = new Date(selectedDate + 'T12:00:00').toLocaleDateString('pt-BR', {
    weekday: 'short', day: 'numeric', month: 'short'
  });

  const statusStyle = (status: string) => {
    if (status === 'em_andamento') return { cls: 'bg-emerald-50 text-emerald-700 ring-emerald-200', label: 'Em Andamento' };
    if (status === 'concluido') return { cls: 'bg-surface-100 text-surface-600 ring-surface-200', label: 'Concluído' };
    return { cls: 'bg-blue-50 text-blue-700 ring-blue-200', label: 'Pendente' };
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Planejamento</h1>
        <p className="page-subtitle">Programação de produção por máquina</p>
      </div>

      {/* Date navigator */}
      <div className="inline-flex items-center gap-1 bg-white rounded-xl border border-surface-200 p-1 shadow-card">
        <button onClick={() => changeDate(-1)} 
          className="p-2 hover:bg-surface-100 rounded-lg transition-colors">
          <ChevronLeft className="w-4 h-4 text-surface-500" />
        </button>
        <div className="flex items-center gap-2 px-3 min-w-[180px] justify-center">
          <Calendar className="w-4 h-4 text-primary-500" />
          <input type="date" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)}
            className="bg-transparent text-sm font-semibold text-surface-800 outline-none cursor-pointer" />
        </div>
        <button onClick={() => changeDate(1)} 
          className="p-2 hover:bg-surface-100 rounded-lg transition-colors">
          <ChevronRight className="w-4 h-4 text-surface-500" />
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <div className="spinner w-8 h-8" />
        </div>
      ) : Object.keys(byMachine).length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-16 h-16 rounded-2xl bg-surface-100 flex items-center justify-center mb-4">
            <Calendar className="w-8 h-8 text-surface-300" />
          </div>
          <p className="text-surface-900 font-semibold">Nenhum planejamento</p>
          <p className="text-surface-400 text-sm mt-1">Sem programação para {dateDisplay}</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Object.entries(byMachine).sort().map(([machine, items]: [string, any[]]) => (
            <div key={machine} className="card-hover">
              {/* Machine header */}
              <div className="flex items-center justify-between mb-4">
                <span className="font-mono font-bold text-primary-600 text-sm tracking-tight">{machine}</span>
                <span className="text-[10px] font-medium text-surface-400 bg-surface-100 px-2 py-0.5 rounded-md">
                  {items.length} {items.length === 1 ? 'item' : 'itens'}
                </span>
              </div>
              
              <div className="space-y-2">
                {items.map((p) => {
                  const st = statusStyle(p.status);
                  return (
                    <div key={p.id} className="bg-surface-50 rounded-xl p-3 border border-surface-100 
                                              hover:border-surface-200 transition-colors">
                      <div className="flex justify-between items-start gap-2">
                        <span className="font-medium text-sm text-surface-800 leading-tight">{p.product_name}</span>
                        <span className={`shrink-0 inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-semibold 
                                        ring-1 uppercase tracking-wider ${st.cls}`}>
                          {st.label}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 mt-2 text-xs text-surface-400">
                        <span className="flex items-center gap-1">
                          <Box className="w-3 h-3" />{p.quantity_planned.toLocaleString('pt-BR')}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />{p.cycle_time_seconds?.toFixed(1) || '—'}s
                        </span>
                        <span className="flex items-center gap-1">
                          <Layers className="w-3 h-3" />{p.cavities} cav
                        </span>
                      </div>
                      {p.shift && (
                        <span className="inline-block mt-2 text-[10px] px-1.5 py-0.5 rounded bg-surface-100 
                                        text-surface-500 font-medium">
                          Turno {p.shift}
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
