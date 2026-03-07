// ── Common (Log, Product, Operator) ──────────────────────────

export interface SystemLog {
  id: number;
  action: string;
  user_email: string | null;
  user_name: string | null;
  details: Record<string, unknown>;
  module: string | null;
  timestamp: string | null;
}

export interface Product {
  id: number;
  code: string;
  name: string;
  description: string | null;
  weight_grams: number | null;
  material: string | null;
  color: string | null;
  mold_code: string | null;
  cycle_time_ideal: number | null;
  cavities: number;
  category: string | null;
  client: string | null;
  is_active: boolean;
}

export interface Operator {
  id: number;
  registration: string;
  name: string;
  shift: string | null;
  sector: string;
  role: string;
  skills: string[];
  is_active: boolean;
  phone: string | null;
}

// ── Notification ─────────────────────────────────────────────

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  target_role: string | null;
  target_user: string | null;
  is_read: boolean;
  created_at: string | null;
}

// ── WebSocket Messages ───────────────────────────────────────

export interface WsMessage<T = unknown> {
  type: string;
  data?: T;
  [key: string]: unknown;
}
