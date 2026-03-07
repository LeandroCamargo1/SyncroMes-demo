import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import api from '../services/api';

interface UseApiOptions {
  autoFetch?: boolean;
  params?: Record<string, unknown>;
}

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: (overrideParams?: Record<string, unknown>) => Promise<T>;
  setData: React.Dispatch<React.SetStateAction<T | null>>;
}

export function useApi<T = unknown>(url: string, options: UseApiOptions = {}): UseApiReturn<T> {
  const { autoFetch = true, params = {} } = options;
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(autoFetch);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async (overrideParams?: Record<string, unknown>): Promise<T> => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<T>(url, { params: overrideParams || params });
      setData(res.data);
      return res.data;
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? (err.response?.data?.detail as string) || err.message
        : (err as Error).message;
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, JSON.stringify(params)]);

  useEffect(() => {
    if (autoFetch) { fetch(); }
  }, [autoFetch, fetch]);

  return { data, loading, error, refetch: fetch, setData };
}

export function usePolling(callback: () => void, intervalMs = 30000): void {
  const savedCallback = useRef(callback);
  useEffect(() => { savedCallback.current = callback; }, [callback]);

  useEffect(() => {
    const tick = () => savedCallback.current();
    tick();
    const id = setInterval(tick, intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
}

export function useDebounce<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}
