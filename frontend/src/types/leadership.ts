// ── Leadership (Escala & Absenteísmo) ────────────────────────

export interface OperatorSchedule {
  id: number;
  operator_registration: string;
  operator_name: string;
  date: string;
  shift: string;
  machine_code: string | null;
  position: string;
  notes: string | null;
  created_at: string | null;
}

export interface OperatorScheduleCreate {
  operator_registration: string;
  operator_name: string;
  date: string;
  shift: string;
  machine_code?: string;
  position?: string;
  notes?: string;
}

export interface Absenteeism {
  id: number;
  operator_registration: string;
  operator_name: string;
  date: string;
  shift: string | null;
  reason: string;
  hours_absent: number;
  justified: boolean;
  notes: string | null;
  created_at: string | null;
}

export interface AbsenteeismCreate {
  operator_registration: string;
  operator_name: string;
  date: string;
  shift?: string;
  reason: string;
  hours_absent?: number;
  justified?: boolean;
  notes?: string;
}
