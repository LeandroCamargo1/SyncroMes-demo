import type { Token, User } from '../types';
import api from './api';

export const authService = {
  async login(email: string, password: string): Promise<Token> {
    const { data } = await api.post<Token>('/auth/login', { email, password });
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
  },

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getStoredUser(): User | null {
    const raw = localStorage.getItem('user');
    return raw ? (JSON.parse(raw) as User) : null;
  },

  getToken(): string | null {
    return localStorage.getItem('token');
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  },

  async getProfile(): Promise<User> {
    const { data } = await api.get<User>('/auth/me');
    return data;
  },
};
