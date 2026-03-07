// ── Downtime ─────────────────────────────────────────────────

export interface ActiveDowntime {
  id: number;
  machine_code: string;
  reason: string;
  category: string;
  subcategory: string | null;
  operator_name: string | null;
  shift: string | null;
  start_time: string;
  is_planned: boolean;
  notes: string | null;
}

export interface ActiveDowntimeCreate {
  machine_code: string;
  reason: string;
  category: string;
  subcategory?: string;
  operator_name?: string;
  shift?: string;
  is_planned?: boolean;
  notes?: string;
}

export interface DowntimeHistory {
  id: number;
  machine_code: string;
  reason: string;
  category: string;
  subcategory: string | null;
  operator_name: string | null;
  shift: string | null;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  is_planned: boolean;
  notes: string | null;
  resolved_by: string | null;
}
