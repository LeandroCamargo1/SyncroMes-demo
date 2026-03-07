// ── Dashboard ────────────────────────────────────────────────

export interface MachineCardData {
  code: string;
  name: string;
  status: string;
  current_product: string | null;
  current_operator: string | null;
  oee: number;
  efficiency: number;
  cycle_time: number | null;
  produced_today: number;
  rejected_today: number;
  downtime_minutes_today: number;
  active_downtime_reason: string | null;
}

export interface DashboardSummary {
  total_machines: number;
  machines_running: number;
  machines_stopped: number;
  machines_maintenance: number;
  oee_average: number;
  total_produced_today: number;
  total_rejected_today: number;
  scrap_rate: number;
  active_orders: number;
  planned_orders: number;
  top_downtime_reason: string | null;
  machines: MachineCardData[];
}
