// ── PCP ──────────────────────────────────────────────────────

export interface PcpMessage {
  id: number;
  message: string;
  priority: number;
  type: string;
  target_machine: string | null;
  is_active: boolean;
  created_by: string | null;
  expires_at: string | null;
  created_at: string | null;
}

export interface PcpMessageCreate {
  message: string;
  priority?: number;
  type?: string;
  target_machine?: string;
  created_by?: string;
  expires_at?: string;
}
