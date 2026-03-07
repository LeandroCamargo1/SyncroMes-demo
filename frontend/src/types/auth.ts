// ── Auth & User ──────────────────────────────────────────────

export type UserRole = 'admin' | 'supervisor' | 'operador' | 'qualidade' | 'pcp';

export interface CustomClaims {
  role?: string;
  permissions?: string[];
  [key: string]: unknown;
}

export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  sector: string;
  is_active: boolean;
  avatar_initials: string | null;
  custom_claims: CustomClaims;
  created_at: string | null;
  last_login: string | null;
}

export interface UserCreate {
  email: string;
  name: string;
  password: string;
  role?: UserRole;
  sector?: string;
}

export interface UserUpdate {
  name?: string;
  role?: string;
  sector?: string;
  is_active?: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}
