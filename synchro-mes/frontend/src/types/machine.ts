// ── Machine & Mold ───────────────────────────────────────────

export type MachineStatus = 'running' | 'stopped' | 'maintenance' | 'setup';

export interface Machine {
  id: number;
  code: string;
  name: string;
  type: string;
  tonnage: number | null;
  status: MachineStatus;
  current_product: string | null;
  current_mold: string | null;
  current_operator: string | null;
  cycle_time_seconds: number | null;
  cavities: number;
  efficiency: number;
  location: string;
  is_active: boolean;
}

export interface MachineUpdate {
  status?: string;
  current_product?: string;
  current_mold?: string;
  current_operator?: string;
  cycle_time_seconds?: number;
  efficiency?: number;
}

export interface Mold {
  id: number;
  code: string;
  name: string;
  cavities: number;
  cycle_time_ideal: number | null;
  product_code: string | null;
  status: string;
  total_cycles: number;
  max_cycles: number | null;
  weight_grams: number | null;
  material_type: string | null;
}

export interface MoldUpdate {
  name?: string;
  cavities?: number;
  cycle_time_ideal?: number;
  product_code?: string;
  status?: string;
  total_cycles?: number;
  max_cycles?: number;
  weight_grams?: number;
  material_type?: string;
}
