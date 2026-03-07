/**
 * Recharts-based chart components — Siemens Opcenter MES style
 * Palette based on the SynchroMES design system (primary, surface, accent colors)
 */
import {
  ResponsiveContainer,
  LineChart, Line,
  BarChart, Bar,
  PieChart, Pie, Cell,
  ComposedChart,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ReferenceLine,
  Area, AreaChart,
} from 'recharts';

// ── Color palette matching tailwind config ──
const COLORS = {
  primary: '#5c7cfa',
  emerald: '#10b981',
  amber: '#f59e0b',
  red: '#ef4444',
  blue: '#3b82f6',
  violet: '#8b5cf6',
  rose: '#f43f5e',
  cyan: '#22d3ee',
  teal: '#2dd4bf',
  orange: '#f97316',
  surface300: '#cbd5e1',
  surface400: '#94a3b8',
  surface100: '#f1f5f9',
  surface200: '#e2e8f0',
};

const PIE_PALETTE = [COLORS.primary, COLORS.emerald, COLORS.amber, COLORS.red, COLORS.blue, COLORS.violet, COLORS.rose, COLORS.cyan, COLORS.teal, COLORS.orange];

const GRID_STYLE = { strokeDasharray: '3 3', stroke: '#e2e8f0' };
const AXIS_STYLE = { fontSize: 11, fill: '#94a3b8', fontFamily: 'Inter, system-ui, sans-serif' };
const TOOLTIP_STYLE = {
  contentStyle: {
    background: '#fff',
    border: '1px solid #e2e8f0',
    borderRadius: 10,
    boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
    fontSize: 12,
    fontFamily: 'Inter, system-ui, sans-serif',
  },
};

// ─────────────────────────────────────────
// 1. OEE Trend Line — A/P/Q breakdown
// ─────────────────────────────────────────
interface OeeTrendProps {
  data: { date: string; oee: number; availability: number; performance: number; quality_rate: number }[];
  height?: number;
}

export function OeeTrendChart({ data, height = 260 }: OeeTrendProps) {
  if (!data || data.length === 0) return <EmptyChart height={height} />;

  const formatted = data.map(d => ({
    ...d,
    date: shortDate(d.date),
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={formatted} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid {...GRID_STYLE} />
        <XAxis dataKey="date" tick={AXIS_STYLE} />
        <YAxis domain={[0, 100]} tick={AXIS_STYLE} tickFormatter={v => `${v}%`} />
        <Tooltip {...TOOLTIP_STYLE} formatter={(v: number) => `${v.toFixed(1)}%`} />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
        <ReferenceLine y={85} stroke={COLORS.emerald} strokeDasharray="6 4" strokeWidth={1} label={{ value: 'World Class', fill: COLORS.emerald, fontSize: 10, position: 'right' }} />
        <Line type="monotone" dataKey="oee" name="OEE" stroke={COLORS.primary} strokeWidth={2.5} dot={{ r: 3 }} activeDot={{ r: 5 }} />
        <Line type="monotone" dataKey="availability" name="Disponibilidade" stroke={COLORS.emerald} strokeWidth={1.5} dot={false} strokeDasharray="5 3" />
        <Line type="monotone" dataKey="performance" name="Performance" stroke={COLORS.blue} strokeWidth={1.5} dot={false} strokeDasharray="5 3" />
        <Line type="monotone" dataKey="quality_rate" name="Qualidade" stroke={COLORS.violet} strokeWidth={1.5} dot={false} strokeDasharray="5 3" />
      </LineChart>
    </ResponsiveContainer>
  );
}

// ─────────────────────────────────────────
// 2. Production Bar Chart — per machine
// ─────────────────────────────────────────
interface ProdBarProps {
  data: { name: string; produced: number; rejected?: number }[];
  height?: number;
}

export function ProductionBarChart({ data, height = 260 }: ProdBarProps) {
  if (!data || data.length === 0) return <EmptyChart height={height} />;
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }} barGap={2}>
        <CartesianGrid {...GRID_STYLE} />
        <XAxis dataKey="name" tick={{ ...AXIS_STYLE, fontSize: 10 }} />
        <YAxis tick={AXIS_STYLE} />
        <Tooltip {...TOOLTIP_STYLE} />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
        <Bar dataKey="produced" name="Produzido" fill={COLORS.emerald} radius={[4, 4, 0, 0]} />
        {data.some(d => d.rejected != null) && (
          <Bar dataKey="rejected" name="Refugo" fill={COLORS.red} radius={[4, 4, 0, 0]} />
        )}
      </BarChart>
    </ResponsiveContainer>
  );
}

// ─────────────────────────────────────────
// 3. Donut Chart — generic
// ─────────────────────────────────────────
interface DonutProps {
  data: { name: string; value: number }[];
  height?: number;
  colors?: string[];
  innerLabel?: string;
  innerValue?: string;
}

export function DonutChart({ data, height = 220, colors, innerLabel, innerValue }: DonutProps) {
  if (!data || data.length === 0 || data.every(d => d.value === 0)) return <EmptyChart height={height} />;
  const palette = colors || PIE_PALETTE;
  return (
    <div className="relative" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius="55%"
            outerRadius="80%"
            paddingAngle={3}
            dataKey="value"
            stroke="none"
          >
            {data.map((_, i) => (
              <Cell key={i} fill={palette[i % palette.length]} />
            ))}
          </Pie>
          <Tooltip {...TOOLTIP_STYLE} formatter={(v: number, name: string) => [v.toLocaleString('pt-BR'), name]} />
          <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} layout="horizontal" align="center" verticalAlign="bottom" />
        </PieChart>
      </ResponsiveContainer>
      {innerValue && (
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none" style={{ marginBottom: 24 }}>
          <span className="text-2xl font-bold text-surface-900">{innerValue}</span>
          {innerLabel && <span className="text-[10px] text-surface-400 uppercase tracking-wider">{innerLabel}</span>}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────
// 4. Pareto Chart — bar + cumulative line
// ─────────────────────────────────────────
interface ParetoProps {
  data: { name: string; value: number }[];
  height?: number;
  unit?: string;
  barColor?: string;
}

export function ParetoChart({ data, height = 280, unit = '', barColor = COLORS.red }: ParetoProps) {
  if (!data || data.length === 0) return <EmptyChart height={height} />;

  const total = data.reduce((s, d) => s + d.value, 0);
  let cumul = 0;
  const withCumul = data.map(d => {
    cumul += d.value;
    return { ...d, cumulative: total > 0 ? (cumul / total) * 100 : 0 };
  });

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={withCumul} margin={{ top: 5, right: 30, left: -10, bottom: 0 }}>
        <CartesianGrid {...GRID_STYLE} />
        <XAxis dataKey="name" tick={{ ...AXIS_STYLE, fontSize: 10 }} />
        <YAxis yAxisId="left" tick={AXIS_STYLE} tickFormatter={v => `${v}${unit}`} />
        <YAxis yAxisId="right" orientation="right" domain={[0, 100]} tick={AXIS_STYLE} tickFormatter={v => `${v}%`} />
        <Tooltip {...TOOLTIP_STYLE} formatter={(v: number, name: string) => [
          name === 'Acumulado' ? `${v.toFixed(1)}%` : `${v.toLocaleString('pt-BR')}${unit}`,
          name,
        ]} />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
        <ReferenceLine yAxisId="right" y={80} stroke={COLORS.amber} strokeDasharray="6 4" />
        <Bar yAxisId="left" dataKey="value" name="Valor" fill={barColor} radius={[4, 4, 0, 0]} />
        <Line yAxisId="right" type="monotone" dataKey="cumulative" name="Acumulado" stroke={COLORS.primary} strokeWidth={2} dot={{ r: 3 }} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

// ─────────────────────────────────────────
// 5. SPC Chart — measured values + limits
// ─────────────────────────────────────────
interface SpcProps {
  data: { index: number; measured: number; nominal: number; ucl: number; lcl: number }[];
  height?: number;
}

export function SpcChart({ data, height = 260 }: SpcProps) {
  if (!data || data.length === 0) return <EmptyChart height={height} />;
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid {...GRID_STYLE} />
        <XAxis dataKey="index" tick={AXIS_STYLE} label={{ value: 'Amostra', position: 'insideBottom', offset: -2, style: { fontSize: 10, fill: '#94a3b8' } }} />
        <YAxis tick={AXIS_STYLE} domain={['auto', 'auto']} />
        <Tooltip {...TOOLTIP_STYLE} />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
        <ReferenceLine y={data[0]?.ucl} stroke={COLORS.red} strokeDasharray="6 4" label={{ value: 'LSC', fill: COLORS.red, fontSize: 10, position: 'right' }} />
        <ReferenceLine y={data[0]?.lcl} stroke={COLORS.red} strokeDasharray="6 4" label={{ value: 'LIC', fill: COLORS.red, fontSize: 10, position: 'right' }} />
        <ReferenceLine y={data[0]?.nominal} stroke={COLORS.emerald} strokeDasharray="3 3" label={{ value: 'Nominal', fill: COLORS.emerald, fontSize: 10, position: 'right' }} />
        <Line type="monotone" dataKey="measured" name="Medido" stroke={COLORS.primary} strokeWidth={2} dot={{ r: 3, fill: COLORS.primary }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

// ─────────────────────────────────────────
// 6. Stacked Area — production trend
// ─────────────────────────────────────────
interface AreaTrendProps {
  data: { date: string; good: number; rejected: number }[];
  height?: number;
}

export function ProductionAreaChart({ data, height = 260 }: AreaTrendProps) {
  if (!data || data.length === 0) return <EmptyChart height={height} />;

  const formatted = data.map(d => ({ ...d, date: shortDate(d.date) }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={formatted} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid {...GRID_STYLE} />
        <XAxis dataKey="date" tick={AXIS_STYLE} />
        <YAxis tick={AXIS_STYLE} />
        <Tooltip {...TOOLTIP_STYLE} />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
        <Area type="monotone" dataKey="good" name="Boas" stackId="1" stroke={COLORS.emerald} fill={COLORS.emerald} fillOpacity={0.3} />
        <Area type="monotone" dataKey="rejected" name="Refugo" stackId="1" stroke={COLORS.red} fill={COLORS.red} fillOpacity={0.3} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

// ─────────────────────────────────────────
// 7. Horizontal Bar — OEE per machine ranking
// ─────────────────────────────────────────
interface HBarProps {
  data: { name: string; value: number }[];
  height?: number;
  target?: number;
}

export function HorizontalBarChart({ data, height = 280, target }: HBarProps) {
  if (!data || data.length === 0) return <EmptyChart height={height} />;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 0 }}>
        <CartesianGrid {...GRID_STYLE} horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tick={AXIS_STYLE} tickFormatter={v => `${v}%`} />
        <YAxis type="category" dataKey="name" tick={{ ...AXIS_STYLE, fontSize: 11, fontFamily: 'JetBrains Mono, monospace' }} width={60} />
        <Tooltip {...TOOLTIP_STYLE} formatter={(v: number) => `${v.toFixed(1)}%`} />
        {target && <ReferenceLine x={target} stroke={COLORS.emerald} strokeDasharray="6 4" label={{ value: `Meta ${target}%`, fill: COLORS.emerald, fontSize: 10, position: 'top' }} />}
        <Bar dataKey="value" name="OEE" radius={[0, 4, 4, 0]}>
          {data.map((d, i) => (
            <Cell key={i} fill={d.value >= 85 ? COLORS.emerald : d.value >= 75 ? COLORS.primary : d.value >= 60 ? COLORS.amber : COLORS.red} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

// ─────────────────────────────────────────
// 8. Mini Sparkline — for DashboardTV
// ─────────────────────────────────────────
interface SparklineProps {
  data: number[];
  color?: string;
  width?: number;
  height?: number;
}

export function Sparkline({ data, color = COLORS.primary, width = 80, height = 28 }: SparklineProps) {
  if (!data || data.length === 0) return null;
  const mapped = data.map((v, i) => ({ i, v }));
  return (
    <ResponsiveContainer width={width} height={height}>
      <LineChart data={mapped}>
        <Line type="monotone" dataKey="v" stroke={color} strokeWidth={1.5} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

// ─────────────────────────────────────────
// 9. Grouped Bar — Output vs Target
// ─────────────────────────────────────────
interface GroupedBarProps {
  data: { name: string; planned: number; produced: number }[];
  height?: number;
}

export function OutputVsTargetChart({ data, height = 260 }: GroupedBarProps) {
  if (!data || data.length === 0) return <EmptyChart height={height} />;
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }} barGap={2}>
        <CartesianGrid {...GRID_STYLE} />
        <XAxis dataKey="name" tick={{ ...AXIS_STYLE, fontSize: 10 }} />
        <YAxis tick={AXIS_STYLE} />
        <Tooltip {...TOOLTIP_STYLE} formatter={(v: number) => v.toLocaleString('pt-BR')} />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
        <Bar dataKey="planned" name="Planejado" fill={COLORS.surface300} radius={[4, 4, 0, 0]} />
        <Bar dataKey="produced" name="Produzido" fill={COLORS.emerald} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── Helpers ──
function shortDate(d: string) {
  if (!d) return '';
  const dt = new Date(d);
  if (isNaN(dt.getTime())) return d;
  return `${String(dt.getDate()).padStart(2, '0')}/${String(dt.getMonth() + 1).padStart(2, '0')}`;
}

function EmptyChart({ height }: { height: number }) {
  return (
    <div className="flex items-center justify-center text-surface-400 text-sm" style={{ height }}>
      Sem dados para exibir
    </div>
  );
}
