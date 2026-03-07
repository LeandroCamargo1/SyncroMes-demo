// ── Tooling / Mold Maintenance ───────────────────────────────

export interface MoldMaintenance {
  id: number;
  mold_code: string;
  maintenance_type: string;
  description: string | null;
  technician: string | null;
  start_time: string;
  end_time: string | null;
  duration_hours: number | null;
  cost: number | null;
  parts_replaced: string | null;
  status: string;
  notes: string | null;
  created_at: string | null;
}

export interface MoldMaintenanceCreate {
  mold_code: string;
  maintenance_type: string;
  description?: string;
  technician?: string;
  start_time: string;
  notes?: string;
}

export interface MoldMaintenanceFinish {
  end_time?: string;
  cost?: number;
  parts_replaced?: string;
  notes?: string;
}
