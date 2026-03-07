import { Activity, Pause, Wrench, Settings, AlertTriangle } from 'lucide-react';
import type { ElementType } from 'react';
import type { MachineCardData } from '../../types';

interface StatusConfig {
  label: string;
  border: string;
  bg: string;
  text: string;
  dot: string;
  icon: ElementType;
  badge: string;
}

const statusConfig: Record<string, StatusConfig> = {
  running: { 
    label: 'Rodando', border: 'border-l-emerald-500', 
    bg: 'bg-emerald-50', text: 'text-emerald-700', 
    dot: 'bg-emerald-500', icon: Activity, 
    badge: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  },
  stopped: { 
    label: 'Parada', border: 'border-l-red-500', 
    bg: 'bg-red-50', text: 'text-red-700', 
    dot: 'bg-red-500', icon: Pause,
    badge: 'bg-red-50 text-red-700 ring-red-200',
  },
  maintenance: { 
    label: 'Manutenção', border: 'border-l-amber-500', 
    bg: 'bg-amber-50', text: 'text-amber-700', 
    dot: 'bg-amber-500', icon: Wrench,
    badge: 'bg-amber-50 text-amber-700 ring-amber-200',
  },
  setup: { 
    label: 'Setup', border: 'border-l-blue-500', 
    bg: 'bg-blue-50', text: 'text-blue-700', 
    dot: 'bg-blue-500', icon: Settings,
    badge: 'bg-blue-50 text-blue-700 ring-blue-200',
  },
};

interface MachineGridProps {
  machines?: MachineCardData[];
}

export default function MachineGrid({ machines = [] }: MachineGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-3">
      {machines.map((m) => {
        const cfg = statusConfig[m.status] || statusConfig.stopped;
        return (
          <div key={m.code} 
            className={`card-hover border-l-[3px] ${cfg.border} p-4 group`}>
            <div className="flex items-center justify-between mb-3">
              <span className="font-mono font-bold text-sm text-surface-900 tracking-tight">{m.code}</span>
              <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-semibold 
                              ring-1 ${cfg.badge} uppercase tracking-wider`}>
                <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} ${m.status === 'running' ? 'animate-pulse' : ''}`} />
                {cfg.label}
              </span>
            </div>

            <div className="mb-3">
              <p className="text-sm text-surface-800 font-medium truncate leading-tight">
                {m.current_product || 'Sem produto'}
              </p>
              <p className="text-xs text-surface-400 truncate mt-0.5">{m.current_operator || '—'}</p>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div className={`${cfg.bg} rounded-lg py-2 px-2 text-center`}>
                <span className="block text-[10px] text-surface-500 font-medium uppercase">OEE</span>
                <span className={`block text-sm font-bold ${cfg.text} tabular-nums`}>{m.oee?.toFixed(0) || 0}%</span>
              </div>
              <div className="bg-surface-50 rounded-lg py-2 px-2 text-center">
                <span className="block text-[10px] text-surface-500 font-medium uppercase">Boas</span>
                <span className="block text-sm font-bold text-surface-800 tabular-nums">{m.produced_today || 0}</span>
              </div>
              <div className="bg-surface-50 rounded-lg py-2 px-2 text-center">
                <span className="block text-[10px] text-surface-500 font-medium uppercase">Refugo</span>
                <span className="block text-sm font-bold text-red-600 tabular-nums">{m.rejected_today || 0}</span>
              </div>
            </div>

            {m.active_downtime_reason && (
              <div className="mt-3 bg-red-50 border border-red-100 rounded-lg px-3 py-2 flex items-start gap-2">
                <AlertTriangle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
                <p className="text-xs text-red-700 font-medium truncate">{m.active_downtime_reason}</p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
