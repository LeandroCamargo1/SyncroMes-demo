import { useState, useEffect, useMemo } from 'react';
import api from '../services/api';
import { BarChart3, TrendingUp, Activity, AlertTriangle, Layers, GitCompare, Eye } from 'lucide-react';

const TABS = [
  { key: 'overview', label: 'Visão Geral', icon: Eye },
  { key: 'production', label: 'Produção', icon: BarChart3 },
  { key: 'efficiency', label: 'Eficiência', icon: TrendingUp },
  { key: 'losses', label: 'Perdas', icon: AlertTriangle },
  { key: 'downtimes', label: 'Paradas', icon: Activity },
  { key: 'comparative', label: 'Comparativa', icon: GitCompare },
  { key: 'orders', label: 'Ordens', icon: Layers },
];

interface MachineStatItem {
  code: string;
  avgOee: number;
  produced: number;
}

export default function Analysis() {
  const [tab, setTab] = useState('overview');
  const [oeeData, setOeeData] = useState<any[]>([]);
  const [entries, setEntries] = useState<any[]>([]);
  const [downtimes, setDowntimes] = useState<any[]>([]);
  const [losses, setLosses] = useState<any[]>([]);
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [oee, prod, dt, loss, ord] = await Promise.all([
        api.get('/oee/history?days=30'),
        api.get('/production/entries?limit=200'),
        api.get('/downtimes/history?limit=200'),
        api.get('/losses').catch(() => ({ data: [] })),
        api.get('/production/orders'),
      ]);
      setOeeData(oee.data);
      setEntries(prod.data);
      setDowntimes(dt.data);
      setLosses(loss.data);
      setOrders(ord.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  // Computed KPIs
  const kpis = useMemo(() => {
    const totalGood = entries.reduce((s, e) => s + (e.quantity_good || 0), 0);
    const totalRej = entries.reduce((s, e) => s + (e.quantity_rejected || 0), 0);
    const totalProd = totalGood + totalRej;
    const avgOee = oeeData.length > 0 ? oeeData.reduce((s, d) => s + (d.oee || 0), 0) / oeeData.length : 0;
    const avgAvail = oeeData.length > 0 ? oeeData.reduce((s, d) => s + (d.availability || 0), 0) / oeeData.length : 0;
    const avgPerf = oeeData.length > 0 ? oeeData.reduce((s, d) => s + (d.performance || 0), 0) / oeeData.length : 0;
    const avgQual = oeeData.length > 0 ? oeeData.reduce((s, d) => s + (d.quality_rate || 0), 0) / oeeData.length : 0;
    const totalDownMin = downtimes.reduce((s, d) => s + (d.duration_minutes || 0), 0);
    const totalLossQty = losses.reduce((s, l) => s + (l.quantity || 0), 0);
    return { totalGood, totalRej, totalProd, avgOee, avgAvail, avgPerf, avgQual, totalDownMin, totalLossQty };
  }, [entries, oeeData, downtimes, losses]);

  // Group by machine for comparative
  const machineStats = useMemo((): MachineStatItem[] => {
    const map: Record<string, { oee: number[]; produced: number }> = {};
    oeeData.forEach(d => {
      if (!map[d.machine_code]) map[d.machine_code] = { oee: [], produced: 0 };
      map[d.machine_code].oee.push(d.oee || 0);
      map[d.machine_code].produced += d.total_produced || 0;
    });
    return Object.entries(map).map(([code, data]) => ({
      code, avgOee: data.oee.reduce((a: number, b: number) => a + b, 0) / data.oee.length, produced: data.produced,
    })).sort((a, b) => b.avgOee - a.avgOee);
  }, [oeeData]);

  // Group losses by category
  const lossByCategory = useMemo((): [string, number][] => {
    const map: Record<string, number> = {};
    losses.forEach(l => { map[l.category] = (map[l.category] || 0) + l.quantity; });
    return Object.entries(map).sort((a, b) => b[1] - a[1]);
  }, [losses]);

  // Group downtimes by category
  const downByCategory = useMemo((): [string, number][] => {
    const map: Record<string, number> = {};
    downtimes.forEach(d => { map[d.category] = (map[d.category] || 0) + (d.duration_minutes || 0); });
    return Object.entries(map).sort((a, b) => b[1] - a[1]);
  }, [downtimes]);

  if (loading) return <div className="flex justify-center py-16"><div className="spinner w-8 h-8" /></div>;

  const KpiCard = ({ label, value, unit, color = 'text-primary-600' }: { label: string; value: string | number; unit: string; color?: string }) => (
    <div className="card text-center">
      <p className="text-xs font-medium text-surface-400 uppercase tracking-wider">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>{value}<span className="text-sm font-normal text-surface-400 ml-1">{unit}</span></p>
    </div>
  );

  const BarViz = ({ data, maxVal, formatValue, colorFn }: { data: [string, number][]; maxVal: number; formatValue?: (v: number) => string; colorFn?: (i: number) => string }) => (
    <div className="space-y-3">
      {data.map(([label, value], i: number) => (
        <div key={label}>
          <div className="flex justify-between text-sm mb-1">
            <span className="font-medium text-surface-700 capitalize">{label}</span>
            <span className="tabular-nums text-surface-500">{formatValue ? formatValue(value as number) : value}</span>
          </div>
          <div className="h-2 rounded-full bg-surface-100 overflow-hidden">
            <div className={`h-full rounded-full transition-all ${colorFn ? colorFn(i) : 'bg-primary-500'}`}
              style={{ width: `${Math.min((value / (maxVal || 1)) * 100, 100)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Análise</h1>
        <p className="page-subtitle">Indicadores avançados e análise de desempenho</p>
      </div>

      {/* Tabs */}
      <div className="tab-bar flex-wrap">
        {TABS.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={tab === t.key ? 'tab-item-active' : 'tab-item'}>
            <t.icon className="w-3.5 h-3.5 inline mr-1 -mt-0.5" />{t.label}
          </button>
        ))}
      </div>

      {/* Visão Geral */}
      {tab === 'overview' && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard label="OEE Médio" value={kpis.avgOee.toFixed(1)} unit="%" color="text-primary-600" />
            <KpiCard label="Disponibilidade" value={kpis.avgAvail.toFixed(1)} unit="%" color="text-emerald-600" />
            <KpiCard label="Performance" value={kpis.avgPerf.toFixed(1)} unit="%" color="text-blue-600" />
            <KpiCard label="Qualidade" value={kpis.avgQual.toFixed(1)} unit="%" color="text-violet-600" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <KpiCard label="Total Produzido" value={kpis.totalProd.toLocaleString('pt-BR')} unit="pçs" />
            <KpiCard label="Total Perdas" value={kpis.totalLossQty.toLocaleString('pt-BR')} unit="pçs" color="text-red-600" />
            <KpiCard label="Tempo Parado" value={Math.round(kpis.totalDownMin).toLocaleString('pt-BR')} unit="min" color="text-amber-600" />
          </div>
        </>
      )}

      {/* Produção */}
      {tab === 'production' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-sm font-semibold text-surface-800 mb-4">Resumo de Produção</h3>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <KpiCard label="Peças Boas" value={kpis.totalGood.toLocaleString('pt-BR')} unit="" color="text-emerald-600" />
              <KpiCard label="Refugo" value={kpis.totalRej.toLocaleString('pt-BR')} unit="" color="text-red-600" />
            </div>
            <KpiCard label="Taxa Aprovação" value={kpis.totalProd > 0 ? (kpis.totalGood / kpis.totalProd * 100).toFixed(1) : '0'} unit="%" color="text-emerald-600" />
          </div>
          <div className="card">
            <h3 className="text-sm font-semibold text-surface-800 mb-4">Top Máquinas por Produção</h3>
            <BarViz data={machineStats.slice(0, 8).map(m => [m.code, m.produced])}
              maxVal={Math.max(...machineStats.map(m => m.produced), 1)}
              formatValue={v => v.toLocaleString('pt-BR')}
              colorFn={() => 'bg-emerald-500'} />
          </div>
        </div>
      )}

      {/* Eficiência */}
      {tab === 'efficiency' && (
        <div className="card">
          <h3 className="text-sm font-semibold text-surface-800 mb-4">OEE por Máquina (média 30 dias)</h3>
          <div className="space-y-4">
            {machineStats.map(m => (
              <div key={m.code}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-mono font-semibold text-surface-700">{m.code}</span>
                  <span className={`tabular-nums font-semibold ${m.avgOee >= 75 ? 'text-emerald-600' : m.avgOee >= 60 ? 'text-amber-600' : 'text-red-600'}`}>
                    {m.avgOee.toFixed(1)}%
                  </span>
                </div>
                <div className="h-3 rounded-full bg-surface-100 overflow-hidden">
                  <div className={`h-full rounded-full transition-all ${m.avgOee >= 75 ? 'bg-emerald-500' : m.avgOee >= 60 ? 'bg-amber-500' : 'bg-red-500'}`}
                    style={{ width: `${m.avgOee}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Perdas */}
      {tab === 'losses' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-sm font-semibold text-surface-800 mb-4">Perdas por Categoria</h3>
            {lossByCategory.length === 0 ? (
              <p className="text-surface-400 text-center py-8">Nenhuma perda registrada</p>
            ) : (
              <BarViz data={lossByCategory} maxVal={Math.max(...lossByCategory.map(l => l[1]), 1)}
                formatValue={v => `${v} pçs`}
                colorFn={(i) => ['bg-red-500', 'bg-amber-500', 'bg-orange-500', 'bg-yellow-500', 'bg-rose-500'][i % 5]} />
            )}
          </div>
          <div className="card p-0 overflow-hidden">
            <div className="px-4 py-3 border-b border-surface-100">
              <h3 className="text-sm font-semibold text-surface-800">Últimas Perdas</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="table-modern">
                <thead><tr><th>Máquina</th><th>Categoria</th><th className="text-right">Qtd</th><th>Motivo</th></tr></thead>
                <tbody>
                  {losses.slice(0, 10).map(l => (
                    <tr key={l.id}>
                      <td className="font-mono text-sm">{l.machine_code}</td>
                      <td><span className="text-xs font-medium uppercase text-surface-500">{l.category}</span></td>
                      <td className="text-right tabular-nums text-red-600 font-semibold">{l.quantity}</td>
                      <td className="text-surface-400 text-sm">{l.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Paradas */}
      {tab === 'downtimes' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-sm font-semibold text-surface-800 mb-4">Tempo Parado por Categoria</h3>
            {downByCategory.length === 0 ? (
              <p className="text-surface-400 text-center py-8">Sem paradas registradas</p>
            ) : (
              <BarViz data={downByCategory} maxVal={Math.max(...downByCategory.map(d => d[1]), 1)}
                formatValue={v => `${Math.round(v)} min`}
                colorFn={(i) => ['bg-red-500', 'bg-amber-500', 'bg-blue-500', 'bg-purple-500', 'bg-pink-500', 'bg-orange-500', 'bg-teal-500'][i % 7]} />
            )}
          </div>
          <div className="card">
            <h3 className="text-sm font-semibold text-surface-800 mb-4">KPIs de Paradas</h3>
            <div className="grid grid-cols-2 gap-4">
              <KpiCard label="Total Paradas" value={downtimes.length} unit="" color="text-red-600" />
              <KpiCard label="Tempo Total" value={Math.round(kpis.totalDownMin)} unit="min" color="text-amber-600" />
              <KpiCard label="Média Duração" value={downtimes.length > 0 ? (kpis.totalDownMin / downtimes.length).toFixed(0) : '0'} unit="min" />
              <KpiCard label="Categorias" value={downByCategory.length} unit="" />
            </div>
          </div>
        </div>
      )}

      {/* Comparativa */}
      {tab === 'comparative' && (
        <div className="card p-0 overflow-hidden">
          <div className="px-4 py-3 border-b border-surface-100">
            <h3 className="text-sm font-semibold text-surface-800">Comparativo entre Máquinas</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr><th>Máquina</th><th className="text-right">OEE Médio</th><th className="text-right">Total Produzido</th><th>Classificação</th></tr>
              </thead>
              <tbody>
                {machineStats.map((m, i) => (
                  <tr key={m.code}>
                    <td className="font-mono font-semibold">{m.code}</td>
                    <td className={`text-right tabular-nums font-semibold ${m.avgOee >= 75 ? 'text-emerald-600' : m.avgOee >= 60 ? 'text-amber-600' : 'text-red-600'}`}>
                      {m.avgOee.toFixed(1)}%
                    </td>
                    <td className="text-right tabular-nums">{m.produced.toLocaleString('pt-BR')}</td>
                    <td>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 uppercase tracking-wider ${
                        i === 0 ? 'bg-emerald-50 text-emerald-700 ring-emerald-200' :
                        i < 3 ? 'bg-blue-50 text-blue-700 ring-blue-200' :
                        'bg-surface-100 text-surface-600 ring-surface-200'
                      }`}>
                        #{i + 1}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Ordens */}
      {tab === 'orders' && (
        <div className="card p-0 overflow-hidden">
          <div className="px-4 py-3 border-b border-surface-100">
            <h3 className="text-sm font-semibold text-surface-800">Análise de Ordens</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="table-modern">
              <thead>
                <tr><th>Ordem</th><th>Produto</th><th className="text-right">Planejado</th><th className="text-right">Produzido</th><th className="text-right">Progresso</th><th className="text-right">Refugo</th></tr>
              </thead>
              <tbody>
                {orders.map(o => {
                  const progress = o.quantity_planned > 0 ? (o.quantity_produced / o.quantity_planned * 100) : 0;
                  return (
                    <tr key={o.id}>
                      <td className="font-mono font-semibold text-primary-600 text-sm">{o.order_number}</td>
                      <td className="font-medium text-surface-800">{o.product_name}</td>
                      <td className="text-right tabular-nums">{o.quantity_planned?.toLocaleString('pt-BR')}</td>
                      <td className="text-right tabular-nums font-medium">{o.quantity_produced?.toLocaleString('pt-BR')}</td>
                      <td className="text-right">
                        <div className="flex items-center gap-2 justify-end">
                          <div className="w-12 h-1.5 rounded-full bg-surface-100 overflow-hidden">
                            <div className="h-full rounded-full bg-primary-500" style={{ width: `${Math.min(progress, 100)}%` }} />
                          </div>
                          <span className="text-xs tabular-nums font-medium">{progress.toFixed(0)}%</span>
                        </div>
                      </td>
                      <td className="text-right tabular-nums text-red-600">{o.quantity_rejected?.toLocaleString('pt-BR')}</td>
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
