import { useState, useEffect } from 'react';
import api from '../services/api';
import { AlertOctagon, History, Timer } from 'lucide-react';

export default function Downtimes() {
  const [active, setActive] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [tab, setTab] = useState('active');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [tab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (tab === 'active') {
        const { data } = await api.get('/downtimes/active');
        setActive(data);
      } else {
        const { data } = await api.get('/downtimes/history?limit=50');
        setHistory(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const categoryStyle = (cat: string) => {
    const map: Record<string, { bg: string; text: string; ring: string; dot: string }> = {
      mecanica: { bg: 'bg-red-50', text: 'text-red-700', ring: 'ring-red-200', dot: 'bg-red-500' },
      eletrica: { bg: 'bg-orange-50', text: 'text-orange-700', ring: 'ring-orange-200', dot: 'bg-orange-500' },
      setup: { bg: 'bg-blue-50', text: 'text-blue-700', ring: 'ring-blue-200', dot: 'bg-blue-500' },
      processo: { bg: 'bg-purple-50', text: 'text-purple-700', ring: 'ring-purple-200', dot: 'bg-purple-500' },
      qualidade: { bg: 'bg-amber-50', text: 'text-amber-700', ring: 'ring-amber-200', dot: 'bg-amber-500' },
      falta_material: { bg: 'bg-surface-100', text: 'text-surface-600', ring: 'ring-surface-200', dot: 'bg-surface-500' },
      programada: { bg: 'bg-emerald-50', text: 'text-emerald-700', ring: 'ring-emerald-200', dot: 'bg-emerald-500' },
    };
    return map[cat] || map.falta_material;
  };

  const elapsedMinutes = (startTime: string) => {
    const diff = (Date.now() - new Date(startTime).getTime()) / 60000;
    return Math.round(diff);
  };

  const formatDuration = (mins: number) => {
    if (mins < 60) return `${mins}min`;
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    return `${h}h${m > 0 ? `${m}min` : ''}`;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Paradas</h1>
        <p className="page-subtitle">Monitoramento de paradas de máquina</p>
      </div>

      {/* Tabs */}
      <div className="tab-bar w-fit">
        <button onClick={() => setTab('active')}
          className={tab === 'active' ? 'tab-item-active' : 'tab-item'}>
          <AlertOctagon className="w-4 h-4 inline mr-1.5 -mt-0.5" />
          Ativas
          {active.length > 0 && (
            <span className="ml-1.5 inline-flex items-center justify-center w-5 h-5 rounded-full bg-red-500 text-white text-[10px] font-bold">
              {active.length}
            </span>
          )}
        </button>
        <button onClick={() => setTab('history')}
          className={tab === 'history' ? 'tab-item-active' : 'tab-item'}>
          <History className="w-4 h-4 inline mr-1.5 -mt-0.5" />Histórico
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <div className="spinner w-8 h-8" />
        </div>
      ) : tab === 'active' ? (
        active.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-16 h-16 rounded-2xl bg-emerald-50 flex items-center justify-center mb-4">
              <AlertOctagon className="w-8 h-8 text-emerald-400" />
            </div>
            <p className="text-surface-900 font-semibold">Nenhuma parada ativa</p>
            <p className="text-surface-400 text-sm mt-1">Todas as máquinas estão operando normalmente</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {active.map((d) => {
              const style = categoryStyle(d.category);
              const elapsed = elapsedMinutes(d.start_time);
              const isLong = elapsed > 60;
              return (
                <div key={d.id} className={`card-hover border-l-[3px] ${isLong ? 'border-l-red-500' : 'border-l-amber-400'}`}>
                  <div className="flex items-start justify-between mb-3">
                    <span className="font-mono font-bold text-lg text-surface-900">{d.machine_code}</span>
                    <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-sm font-bold 
                                    ${isLong ? 'bg-red-50 text-red-700' : 'bg-amber-50 text-amber-700'}`}>
                      <Timer className="w-3.5 h-3.5" />
                      {formatDuration(elapsed)}
                    </span>
                  </div>
                  
                  <p className="text-surface-800 font-medium text-sm mb-3">{d.reason}</p>
                  
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-semibold 
                                    ring-1 uppercase tracking-wider ${style.bg} ${style.text} ${style.ring}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
                      {d.category}
                    </span>
                    {d.operator_name && (
                      <span className="text-xs text-surface-400">
                        Op: <span className="text-surface-600">{d.operator_name}</span>
                      </span>
                    )}
                    {d.shift && (
                      <span className="text-xs px-1.5 py-0.5 rounded bg-surface-100 text-surface-500 font-medium">
                        Turno {d.shift}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr>
                  <th>Máquina</th>
                  <th>Motivo</th>
                  <th>Categoria</th>
                  <th className="text-right">Duração</th>
                  <th>Operador</th>
                  <th>Início</th>
                  <th>Fim</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h) => {
                  const style = categoryStyle(h.category);
                  return (
                    <tr key={h.id}>
                      <td className="font-mono font-semibold text-sm">{h.machine_code}</td>
                      <td className="font-medium text-surface-800 max-w-[200px] truncate">{h.reason}</td>
                      <td>
                        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-semibold 
                                        ring-1 uppercase tracking-wider ${style.bg} ${style.text} ${style.ring}`}>
                          {h.category}
                        </span>
                      </td>
                      <td className="text-right tabular-nums font-semibold text-surface-800">
                        {formatDuration(Math.round(h.duration_minutes))}
                      </td>
                      <td className="text-surface-400">{h.operator_name || '—'}</td>
                      <td className="text-xs text-surface-400 tabular-nums">{new Date(h.start_time).toLocaleString('pt-BR')}</td>
                      <td className="text-xs text-surface-400 tabular-nums">{new Date(h.end_time).toLocaleString('pt-BR')}</td>
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
