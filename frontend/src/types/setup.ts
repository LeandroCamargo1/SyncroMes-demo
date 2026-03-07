// ── Setup ────────────────────────────────────────────────────

export interface SetupEntry {
  id: number;
  machine_code: string;
  setup_type: string;
  mold_from: string | null;
  mold_to: string | null;
  product_from: string | null;
  product_to: string | null;
  operator_name: string | null;
  shift: string | null;
  start_time: string;
  end_time: string | null;
  duration_minutes: number | null;
  status: string;
  notes: string | null;
  created_at: string | null;
}

export interface SetupEntryCreate {
  machine_code: string;
  setup_type: string;
  mold_from?: string;
  mold_to?: string;
  product_from?: string;
  product_to?: string;
  operator_name?: string;
  shift?: string;
  start_time: string;
  notes?: string;
}

export interface SetupEntryFinish {
  end_time?: string;
  notes?: string;
}
