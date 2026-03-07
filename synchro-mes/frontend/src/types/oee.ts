// ── OEE ──────────────────────────────────────────────────────

export type OeeTrend = 'up' | 'down' | 'stable';

export interface OeeHistory {
  id: number;
  machine_code: string;
  date: string;
  shift: string | null;
  availability: number;
  performance: number;
  quality_rate: number;
  oee: number;
  planned_time_minutes: number;
  running_time_minutes: number;
  downtime_minutes: number;
  total_produced: number;
  good_produced: number;
  rejected: number;
}

export interface OeeSummary {
  machine_code: string;
  oee: number;
  availability: number;
  performance: number;
  quality_rate: number;
  trend: OeeTrend;
  period: string;
}
