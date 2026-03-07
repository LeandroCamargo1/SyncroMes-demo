import type { ReactNode, ElementType } from 'react';

// ── LoadingSpinner ───────────────────────────────────────────

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function LoadingSpinner({ size = 'md', className = '' }: LoadingSpinnerProps) {
  const sizes = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' };
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div className={`spinner ${sizes[size]}`} />
    </div>
  );
}

// ── PageLoading ──────────────────────────────────────────────

export function PageLoading() {
  return (
    <div className="flex items-center justify-center h-64">
      <LoadingSpinner size="lg" />
    </div>
  );
}

// ── EmptyState ───────────────────────────────────────────────

interface EmptyStateProps {
  icon?: ElementType;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center animate-fade-in">
      {Icon && (
        <div className="w-16 h-16 rounded-2xl bg-surface-100 flex items-center justify-center mb-4">
          <Icon className="w-8 h-8 text-surface-300" />
        </div>
      )}
      <h3 className="text-base font-semibold text-surface-900">{title}</h3>
      {description && <p className="mt-1 text-sm text-surface-400 max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

// ── StatusBadge ──────────────────────────────────────────────

interface StatusConfig {
  cls: string;
  label: string;
}

const statusMap: Record<string, StatusConfig> = {
  running:     { cls: 'bg-emerald-50 text-emerald-700 ring-emerald-200', label: 'Produzindo' },
  idle:        { cls: 'bg-surface-100 text-surface-600 ring-surface-200', label: 'Parada' },
  setup:       { cls: 'bg-amber-50 text-amber-700 ring-amber-200', label: 'Setup' },
  maintenance: { cls: 'bg-red-50 text-red-700 ring-red-200', label: 'Manutenção' },
  offline:     { cls: 'bg-surface-100 text-surface-500 ring-surface-200', label: 'Offline' },
  approved:    { cls: 'bg-emerald-50 text-emerald-700 ring-emerald-200', label: 'Aprovado' },
  rejected:    { cls: 'bg-red-50 text-red-700 ring-red-200', label: 'Rejeitado' },
  pending:     { cls: 'bg-amber-50 text-amber-700 ring-amber-200', label: 'Pendente' },
  completed:   { cls: 'bg-surface-100 text-surface-600 ring-surface-200', label: 'Concluído' },
  in_progress: { cls: 'bg-blue-50 text-blue-700 ring-blue-200', label: 'Em Andamento' },
  planned:     { cls: 'bg-indigo-50 text-indigo-700 ring-indigo-200', label: 'Planejado' },
};

interface StatusBadgeProps {
  status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const cfg = statusMap[status] || { cls: 'bg-surface-100 text-surface-600 ring-surface-200', label: status };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold 
                      uppercase tracking-wider ring-1 ${cfg.cls}`}>
      {cfg.label}
    </span>
  );
}
