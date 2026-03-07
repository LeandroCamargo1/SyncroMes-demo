import { useState, useEffect } from 'react';
import api from '../services/api';
import { FileText, Download, BarChart3, TrendingUp, ShieldCheck } from 'lucide-react';
import { DonutChart, ParetoChart } from '../components/charts';

const REPORT_TYPES = [
  { key: 'production', label: 'Produção', icon: BarChart3, description: 'Relatório por máquina, produto e período' },
  { key: 'oee', label: 'OEE', icon: TrendingUp, description: 'Disponibilidade, Performance e Qualidade' },
  { key: 'quality', label: 'Qualidade', icon: ShieldCheck, description: 'Medições, aprovações e defeitos' },
  { key: 'downtimes', label: 'Paradas', icon: FileText, description: 'Paradas por categoria e duração' },
];

export default function Reports() {
  const [selectedReport, setSelectedReport] = useState('production');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const generateReport = async (type: string) => {
    setSelectedReport(type);
    setLoading(true);
    try {
      let reportData: any = {};
      if (type === 'production') {
        const [orders, entries] = await Promise.all([
          api.get('/production/orders'),
          api.get('/production/entries?limit=100'),
        ]);
        const totalGood = entries.data.reduce((s: number, e: any) => s + (e.quantity_good || 0), 0);
        const totalRej = entries.data.reduce((s: number, e: any) => s + (e.quantity_rejected || 0), 0);
        reportData = {
          orders: orders.data.length,
          completed: orders.data.filter((o: any) => o.status === 'completed').length,
          inProgress: orders.data.filter((o: any) => o.status === 'in_progress').length,
          totalGood, totalRej,
          approvalRate: totalGood + totalRej > 0 ? (totalGood / (totalGood + totalRej) * 100).toFixed(1) : '0',
          entries: entries.data.length,
        };
      } else if (type === 'oee') {
        const { data: oeeData } = await api.get('/oee/factory');
        reportData = oeeData;
      } else if (type === 'quality') {
        const { data: qualData } = await api.get('/quality-lots/reports');
        reportData = qualData;
      } else if (type === 'downtimes') {
        const { data: dtData } = await api.get('/downtimes/history?limit=200');
        const totalMin = dtData.reduce((s: number, d: any) => s + (d.duration_minutes || 0), 0);
        const categories: Record<string, number> = {};
        dtData.forEach((d: any) => { categories[d.category] = (categories[d.category] || 0) + (d.duration_minutes || 0); });
        reportData = {
          total: dtData.length,
          totalMinutes: Math.round(totalMin),
          avgDuration: dtData.length > 0 ? (totalMin / dtData.length).toFixed(0) : 0,
          categories: Object.entries(categories).sort((a, b) => b[1] - a[1]),
        };
      }
      setData(reportData);
    } catch (err) { console.error(err); setData(null); }
    finally { setLoading(false); }
  };

  useEffect(() => { generateReport('production'); }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Relatórios</h1>
        <p className="page-subtitle">Gere e exporte relatórios gerenciais</p>
      </div>

      {/* Report Type Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {REPORT_TYPES.map(rt => (
          <button key={rt.key} onClick={() => generateReport(rt.key)}
            className={`card text-left transition-all cursor-pointer border-2 ${
              selectedReport === rt.key ? 'border-primary-500 shadow-glow-primary' : 'border-transparent hover:border-surface-200'
            }`}>
            <rt.icon className={`w-6 h-6 mb-2 ${selectedReport === rt.key ? 'text-primary-500' : 'text-surface-400'}`} />
            <p className="font-semibold text-sm text-surface-800">{rt.label}</p>
            <p className="text-xs text-surface-400 mt-0.5">{rt.description}</p>
          </button>
        ))}
      </div>

      {/* Report Content */}
      {loading ? (
        <div className="flex justify-center py-16"><div className="spinner w-8 h-8" /></div>
      ) : data && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-base font-semibold text-surface-800">
              Relatório de {REPORT_TYPES.find(r => r.key === selectedReport)?.label}
            </h3>
          </div>

          {/* Produção */}
          {selectedReport === 'production' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Total Ordens</p>
                  <p className="text-2xl font-bold text-primary-600 mt-1">{data.orders}</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Em Produção</p>
                  <p className="text-2xl font-bold text-emerald-600 mt-1">{data.inProgress}</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Concluídas</p>
                  <p className="text-2xl font-bold text-blue-600 mt-1">{data.completed}</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Peças Boas</p>
                  <p className="text-2xl font-bold text-emerald-600 mt-1">{data.totalGood?.toLocaleString('pt-BR')}</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Refugo</p>
                  <p className="text-2xl font-bold text-red-600 mt-1">{data.totalRej?.toLocaleString('pt-BR')}</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Taxa Aprovação</p>
                  <p className="text-2xl font-bold text-primary-600 mt-1">{data.approvalRate}%</p>
                </div>
              </div>
              <div className="flex justify-center">
                <div className="w-full max-w-xs">
                  <h4 className="text-sm font-semibold text-surface-700 mb-2 text-center">Boas vs Refugo</h4>
                  <DonutChart
                    data={[{ name: 'Boas', value: data.totalGood || 0 }, { name: 'Refugo', value: data.totalRej || 0 }]}
                    colors={['#10b981', '#ef4444']}
                    innerValue={`${data.approvalRate}%`}
                    innerLabel="Aprovação"
                    height={180}
                  />
                </div>
              </div>
            </div>
          )}

          {/* OEE */}
          {selectedReport === 'oee' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">OEE</p>
                  <p className="text-2xl font-bold text-primary-600 mt-1">{data.oee?.toFixed(1) || '—'}%</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Disponibilidade</p>
                  <p className="text-2xl font-bold text-emerald-600 mt-1">{data.availability?.toFixed(1) || '—'}%</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Performance</p>
                  <p className="text-2xl font-bold text-blue-600 mt-1">{data.performance?.toFixed(1) || '—'}%</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Qualidade</p>
                  <p className="text-2xl font-bold text-violet-600 mt-1">{data.quality?.toFixed(1) || '—'}%</p>
                </div>
              </div>
              <div className="flex justify-center">
                <div className="w-full max-w-xs">
                  <h4 className="text-sm font-semibold text-surface-700 mb-2 text-center">Composição OEE</h4>
                  <DonutChart
                    data={[
                      { name: 'Disponibilidade', value: data.availability || 0 },
                      { name: 'Performance', value: data.performance || 0 },
                      { name: 'Qualidade', value: data.quality || 0 },
                    ]}
                    colors={['#10b981', '#3b82f6', '#8b5cf6']}
                    innerValue={`${data.oee?.toFixed(1) || '—'}%`}
                    innerLabel="OEE"
                    height={200}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Quality */}
          {selectedReport === 'quality' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Total Medições</p>
                  <p className="text-2xl font-bold text-primary-600 mt-1">{data.total_measurements}</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Aprovados</p>
                  <p className="text-2xl font-bold text-emerald-600 mt-1">{data.approved}</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Rejeitados</p>
                  <p className="text-2xl font-bold text-red-600 mt-1">{data.rejected}</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Taxa Aprovação</p>
                  <p className="text-2xl font-bold text-emerald-600 mt-1">{data.approval_rate}%</p>
                </div>
              </div>
              <div className="flex justify-center">
                <div className="w-full max-w-xs">
                  <h4 className="text-sm font-semibold text-surface-700 mb-2 text-center">Aprovação</h4>
                  <DonutChart
                    data={[
                      { name: 'Aprovados', value: data.approved || 0 },
                      { name: 'Rejeitados', value: data.rejected || 0 },
                    ]}
                    colors={['#10b981', '#ef4444']}
                    innerValue={`${data.approval_rate || 0}%`}
                    innerLabel="Aprovação"
                    height={180}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Downtimes */}
          {selectedReport === 'downtimes' && (
            <div className="space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Total Paradas</p>
                  <p className="text-2xl font-bold text-red-600 mt-1">{data.total}</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Tempo Total</p>
                  <p className="text-2xl font-bold text-amber-600 mt-1">{data.totalMinutes} min</p>
                </div>
                <div className="bg-surface-50 rounded-xl p-4 text-center">
                  <p className="text-xs text-surface-400 uppercase font-medium">Média Duração</p>
                  <p className="text-2xl font-bold text-surface-600 mt-1">{data.avgDuration} min</p>
                </div>
              </div>
              {data.categories?.length > 0 && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-semibold text-surface-700 mb-3">Pareto de Paradas</h4>
                    <ParetoChart
                      data={data.categories.map(([cat, mins]: [string, number]) => ({ name: cat, value: Math.round(mins) }))}
                      unit=" min"
                      barColor="#f59e0b"
                    />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-surface-700 mb-3">Distribuição por Categoria</h4>
                    <DonutChart
                      data={data.categories.map(([cat, mins]: [string, number]) => ({ name: cat, value: Math.round(mins) }))}
                      innerValue={`${data.totalMinutes}`}
                      innerLabel="min total"
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
