// ── Production ───────────────────────────────────────────────

export type OrderStatus = 'planned' | 'in_progress' | 'completed' | 'cancelled';
export type OrderPriority = 'low' | 'normal' | 'high' | 'urgent';

export interface ProductionOrder {
  id: number;
  order_number: string;
  product_code: string;
  product_name: string;
  quantity_planned: number;
  quantity_produced: number;
  quantity_good: number;
  quantity_rejected: number;
  status: OrderStatus;
  priority: OrderPriority;
  machine_code: string | null;
  mold_code: string | null;
  operator_name: string | null;
  start_date: string | null;
  end_date: string | null;
  due_date: string | null;
  client: string | null;
  notes: string | null;
  created_at: string | null;
}

export interface ProductionOrderCreate {
  order_number: string;
  product_code: string;
  product_name: string;
  quantity_planned: number;
  priority?: string;
  machine_code?: string;
  mold_code?: string;
  due_date?: string;
  client?: string;
  notes?: string;
}

export interface ProductionOrderUpdate {
  quantity_produced?: number;
  quantity_good?: number;
  quantity_rejected?: number;
  status?: string;
  machine_code?: string;
  operator_name?: string;
  notes?: string;
}

export interface Planning {
  id: number;
  machine_code: string;
  product_code: string;
  product_name: string;
  quantity_planned: number;
  date: string;
  shift: string | null;
  mold_code: string | null;
  cycle_time_seconds: number | null;
  cavities: number;
  weight_grams: number | null;
  material: string | null;
  color: string | null;
  sequence: number;
  status: string;
  operator_name: string | null;
}

export interface PlanningCreate {
  machine_code: string;
  product_code: string;
  product_name: string;
  quantity_planned: number;
  date: string;
  shift?: string;
  mold_code?: string;
  cycle_time_seconds?: number;
  cavities?: number;
  weight_grams?: number;
  material?: string;
  color?: string;
  operator_name?: string;
  sequence?: number;
}

export interface ProductionEntry {
  id: number;
  machine_code: string;
  product_code: string;
  product_name: string | null;
  order_number: string | null;
  operator_name: string | null;
  shift: string | null;
  quantity_good: number;
  quantity_rejected: number;
  weight_kg: number | null;
  cycle_time_actual: number | null;
  timestamp: string | null;
}

export interface ProductionEntryCreate {
  machine_code: string;
  product_code: string;
  product_name?: string;
  order_number?: string;
  operator_name?: string;
  shift?: string;
  quantity_good: number;
  quantity_rejected?: number;
  weight_kg?: number;
  cycle_time_actual?: number;
  notes?: string;
}
