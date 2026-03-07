import { createContext, useContext, useState, type ReactNode } from 'react';
import type { User, Token } from '../types';

// ── DEV MODE: usuário admin sem login ────────────────────────
const DEV_USER: User = {
  id: 1,
  email: 'admin@synchro.dev',
  name: 'Admin Dev',
  role: 'admin',
  is_active: true,
  custom_claims: {
    role: 'admin',
    permissions: [
      'dashboard', 'production', 'quality', 'downtimes', 'planning',
      'orders', 'launch', 'analysis', 'pmp', 'history', 'reports',
      'admin', 'leadership', 'setup', 'tooling', 'pcp', 'machines',
    ],
  },
  sector: 'producao',
  avatar_initials: 'AD',
  created_at: new Date().toISOString(),
  last_login: new Date().toISOString(),
};

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<Token>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user] = useState<User | null>(DEV_USER);
  const loading = false;

  const login = async (_email: string, _password: string): Promise<Token> => {
    return { access_token: 'dev-token', token_type: 'bearer', user: DEV_USER };
  };

  const logout = () => {};

  const hasPermission = (_permission: string): boolean => true;

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth deve ser usado dentro de AuthProvider');
  return ctx;
}
