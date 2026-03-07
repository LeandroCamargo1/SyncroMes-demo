interface GaugeColorConfig {
  stroke: string;
  glow: string;
  label: string;
  text: string;
  bg: string;
  ring: string;
}

function getColor(v: number): GaugeColorConfig {
  if (v >= 85) return { stroke: '#10b981', glow: 'rgba(16,185,129,0.3)', label: 'World Class', text: 'text-emerald-600', bg: 'bg-emerald-50', ring: 'ring-emerald-200' };
  if (v >= 75) return { stroke: '#5c7cfa', glow: 'rgba(92,124,250,0.3)', label: 'Bom', text: 'text-primary-600', bg: 'bg-primary-50', ring: 'ring-primary-200' };
  if (v >= 60) return { stroke: '#f59e0b', glow: 'rgba(245,158,11,0.3)', label: 'Regular', text: 'text-amber-600', bg: 'bg-amber-50', ring: 'ring-amber-200' };
  return { stroke: '#ef4444', glow: 'rgba(239,68,68,0.3)', label: 'Crítico', text: 'text-red-600', bg: 'bg-red-50', ring: 'ring-red-200' };
}

interface OeeGaugeProps {
  value?: number;
}

export default function OeeGauge({ value = 0 }: OeeGaugeProps) {
  const percentage = Math.min(Math.max(value, 0), 100);
  const config = getColor(percentage);
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const arc = circumference * 0.75;
  const offset = arc - (percentage / 100) * arc;

  return (
    <div className="flex flex-col items-center py-4">
      <div className="relative w-52 h-52">
        <div className="absolute inset-4 rounded-full blur-2xl opacity-30 transition-all duration-1000"
          style={{ backgroundColor: config.stroke }} />
        
        <svg viewBox="0 0 160 160" className="w-full h-full -rotate-[135deg] drop-shadow-sm">
          <circle cx="80" cy="80" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="10"
            strokeDasharray={`${arc} ${circumference - arc}`} strokeLinecap="round" />
          <circle cx="80" cy="80" r={radius} fill="none" stroke={config.stroke} strokeWidth="10"
            strokeDasharray={`${arc} ${circumference - arc}`}
            strokeDashoffset={offset}
            strokeLinecap="round" 
            className="transition-all duration-1000 ease-out"
            style={{ filter: `drop-shadow(0 0 6px ${config.glow})` }} />
        </svg>
        
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-extrabold text-surface-900 tracking-tight tabular-nums">
            {percentage.toFixed(1)}
            <span className="text-xl text-surface-400 font-semibold">%</span>
          </span>
          <span className="text-xs text-surface-400 font-medium mt-0.5 uppercase tracking-wider">OEE</span>
        </div>
      </div>
      
      <div className={`mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg ${config.bg} ring-1 ${config.ring}`}>
        <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: config.stroke }} />
        <span className={`text-xs font-semibold ${config.text}`}>{config.label}</span>
      </div>
    </div>
  );
}
