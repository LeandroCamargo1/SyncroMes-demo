// ── Loss ─────────────────────────────────────────────────────

export interface LossEntry {
  id: number;
  machine_code: string;
  product_code: string;
  order_number: string | null;
  operator_name: string | null;
  shift: string | null;
  quantity: number;
  weight_kg: number | null;
  reason: string;
  category: string;
  material: string | null;
  is_manual: boolean;
  notes: string | null;
  timestamp: string | null;
}

export interface LossEntryCreate {
  machine_code: string;
  product_code: string;
  order_number?: string;
  operator_name?: string;
  shift?: string;
  quantity: number;
  weight_kg?: number;
  reason: string;
  category: string;
  material?: string;
  is_manual?: boolean;
  notes?: string;
}
