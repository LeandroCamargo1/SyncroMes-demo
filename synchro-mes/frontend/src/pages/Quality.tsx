import { useState, useEffect } from 'react';
import api from '../services/api';
import { ShieldCheck, AlertTriangle, CheckCircle2, XCircle, Filter } from 'lucide-react';

export default function Quality() {
  const [measurements, setMeasurements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchData();
  }, [filter]);

  const fetchData = async () => {
    setLoading(true);
    try {
      let url = '/quality/measurements?limit=50';
      if (filter === 'approved') url += '&approved=true';
      if (filter === 'rejected') url += '&approved=false';
      const { data } = await api.get(url);
      setMeasurements(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filters = [
    { key: 'all', label: 'Todas', icon: Filter },
    { key: 'approved', label: 'Aprovadas', icon: CheckCircle2 },
    { key: 'rejected', label: 'Reprovadas', icon: XCircle },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Qualidade</h1>
        <p className="page-subtitle">Medições e inspeções de qualidade</p>
      </div>

      {/* Filter pills */}
      <div className="tab-bar w-fit">
        {filters.map((f) => (
          <button key={f.key} onClick={() => setFilter(f.key)}
            className={filter === f.key ? 'tab-item-active' : 'tab-item'}>
            <f.icon className="w-3.5 h-3.5 inline mr-1.5 -mt-0.5" />{f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <div className="spinner w-8 h-8" />
        </div>
      ) : measurements.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <ShieldCheck className="w-12 h-12 text-surface-300 mb-3" />
          <p className="text-surface-500 font-medium">Nenhuma medição encontrada</p>
          <p className="text-surface-400 text-sm mt-1">Tente alterar o filtro</p>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr>
                  <th>Máquina</th>
                  <th>Produto</th>
                  <th>Dimensão</th>
                  <th className="text-right">Nominal</th>
                  <th className="text-right">Medido</th>
                  <th className="text-right">Tol. Inf.</th>
                  <th className="text-right">Tol. Sup.</th>
                  <th>Resultado</th>
                  <th>Inspetor</th>
                </tr>
              </thead>
              <tbody>
                {measurements.map((m) => (
                  <tr key={m.id}>
                    <td className="font-mono font-semibold text-sm">{m.machine_code}</td>
                    <td className="font-medium text-surface-800">{m.product_code}</td>
                    <td className="text-surface-500">{m.dimension_name || '—'}</td>
                    <td className="text-right tabular-nums text-surface-500">{m.nominal_value?.toFixed(2) || '—'}</td>
                    <td className="text-right tabular-nums font-semibold text-surface-800">{m.measured_value?.toFixed(2) || '—'}</td>
                    <td className="text-right tabular-nums text-surface-400">{m.tolerance_lower?.toFixed(2) || '—'}</td>
                    <td className="text-right tabular-nums text-surface-400">{m.tolerance_upper?.toFixed(2) || '—'}</td>
                    <td>
                      {m.is_approved ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold 
                                        ring-1 bg-emerald-50 text-emerald-700 ring-emerald-200 uppercase tracking-wider">
                          <CheckCircle2 className="w-3 h-3" />OK
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold 
                                        ring-1 bg-red-50 text-red-700 ring-red-200 uppercase tracking-wider">
                          <XCircle className="w-3 h-3" />NOK
                        </span>
                      )}
                    </td>
                    <td className="text-surface-400 text-sm">{m.inspector || '—'}</td>
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
