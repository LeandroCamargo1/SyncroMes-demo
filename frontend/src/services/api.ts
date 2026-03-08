import axios from 'axios';

// Detecta se está em ambiente estático (GitHub Pages) — sem backend
export const isStaticDeploy = window.location.hostname.includes('github.io');

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Interceptor: em deploy estático, retorna dados vazios sem fazer request
if (isStaticDeploy) {
  api.interceptors.request.use(() => {
    return Promise.reject({ __static: true, message: 'API indisponível em modo demo' });
  });

  api.interceptors.response.use(undefined, (error) => {
    if (error?.__static) return Promise.reject(error);
    return Promise.reject(error);
  });
} else {
  // Interceptor: adiciona Authorization Bearer em todas as requests
  api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Interceptor: redireciona para login em 401
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401 && window.location.pathname !== '/login') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    },
  );
}

export default api;
