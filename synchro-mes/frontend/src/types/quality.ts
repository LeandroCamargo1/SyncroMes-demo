// ── Quality ──────────────────────────────────────────────────

export interface QualityMeasurement {
  id: number;
  machine_code: string;
  product_code: string;
  order_number: string | null;
  inspector: string | null;
  dimension_name: string | null;
  nominal_value: number | null;
  measured_value: number | null;
  tolerance_upper: number | null;
  tolerance_lower: number | null;
  unit: string;
  is_approved: boolean;
  defect_type: string | null;
  defect_severity: string | null;
  timestamp: string | null;
}

export interface QualityMeasurementCreate {
  machine_code: string;
  product_code: string;
  order_number?: string;
  operator_name?: string;
  inspector?: string;
  dimension_name?: string;
  nominal_value?: number;
  measured_value?: number;
  tolerance_upper?: number;
  tolerance_lower?: number;
  unit?: string;
  is_approved?: boolean;
  defect_type?: string;
  defect_severity?: string;
  sample_size?: number;
  notes?: string;
}

export interface QualityLot {
  id: number;
  lot_number: string;
  machine_code: string;
  product_code: string;
  order_number: string | null;
  quantity: number;
  weight_kg: number | null;
  reason: string;
  status: string;
  approved_qty: number;
  rejected_qty: number;
  returned_to_production: boolean;
  operator_name: string | null;
  inspector: string | null;
  shift: string | null;
  notes: string | null;
  conclusion_notes: string | null;
  created_at: string | null;
  concluded_at: string | null;
}

export interface QualityLotCreate {
  machine_code: string;
  product_code: string;
  order_number?: string;
  quantity: number;
  weight_kg?: number;
  reason: string;
  operator_name?: string;
  shift?: string;
  notes?: string;
}

export interface QualityLotUpdate {
  status?: string;
  approved_qty?: number;
  rejected_qty?: number;
  inspector?: string;
  conclusion_notes?: string;
  returned_to_production?: boolean;
}
