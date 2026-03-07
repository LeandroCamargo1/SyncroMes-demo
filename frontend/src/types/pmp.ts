// ── PMP (Moído / Borra / Sucata) ─────────────────────────────

export type PmpType = 'moido' | 'borra' | 'sucata';

export interface PmpEntry {
  id: number;
  type: PmpType;
  machine_code: string | null;
  product_code: string | null;
  material: string | null;
  weight_kg: number;
  operator_name: string | null;
  shift: string | null;
  destination: string | null;
  notes: string | null;
  timestamp: string | null;
}

export interface PmpEntryCreate {
  type: PmpType;
  machine_code?: string;
  product_code?: string;
  material?: string;
  weight_kg: number;
  operator_name?: string;
  shift?: string;
  destination?: string;
  notes?: string;
}
