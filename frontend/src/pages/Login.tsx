import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Factory, Lock, Mail, Eye, EyeOff, ArrowRight, Zap } from 'lucide-react';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/', { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Credenciais inválidas');
    } finally {
      setLoading(false);
    }
  };

  const demoUsers = [
    { email: 'admin@demo-mes.app', label: 'Admin', icon: '👑' },
    { email: 'supervisor@demo-mes.app', label: 'Supervisor', icon: '📋' },
    { email: 'operador@demo-mes.app', label: 'Operador', icon: '🔧' },
    { email: 'qualidade@demo-mes.app', label: 'Qualidade', icon: '🔍' },
    { email: 'pcp@demo-mes.app', label: 'PCP', icon: '📊' },
  ];

  return (
    <div className="min-h-screen flex relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 bg-surface-950">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,_rgba(92,124,250,0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_rgba(139,92,246,0.1),transparent_50%)]" />
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px)`,
          backgroundSize: '32px 32px',
        }} />
      </div>

      {/* Left panel — Branding (hidden on mobile) */}
      <div className="hidden lg:flex lg:w-1/2 relative items-center justify-center p-12">
        <div className="max-w-lg animate-fade-in">
          <div className="flex items-center gap-3 mb-8">
            <div className="bg-gradient-to-br from-primary-500 to-primary-700 p-3 rounded-2xl shadow-glow-primary">
              <Factory className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Synchro MES</h1>
              <p className="text-primary-400 text-xs font-medium tracking-widest uppercase">Industry 4.0</p>
            </div>
          </div>
          
          <h2 className="text-4xl font-extrabold text-white leading-tight mb-4">
            Manufacturing
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-accent-cyan">
              Execution System
            </span>
          </h2>
          <p className="text-surface-400 text-lg leading-relaxed mb-8">
            Monitore sua produção em tempo real, controle paradas, 
            analise OEE e tome decisões baseadas em dados.
          </p>

          {/* Feature pills */}
          <div className="flex flex-wrap gap-3">
            {['OEE em Tempo Real', 'Controle de Qualidade', 'Gestão de Paradas', 'Planejamento'].map((f) => (
              <span key={f} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full 
                bg-white/5 border border-white/10 text-surface-300 text-sm backdrop-blur-sm">
                <Zap className="w-3 h-3 text-primary-400" />{f}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel — Login form */}
      <div className="flex-1 flex items-center justify-center p-6 relative z-10">
        <div className="w-full max-w-md animate-scale-in">
          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="inline-flex items-center gap-2.5">
              <div className="bg-gradient-to-br from-primary-500 to-primary-700 p-2.5 rounded-xl shadow-glow-primary">
                <Factory className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-white">Synchro MES</span>
            </div>
          </div>

          {/* Card */}
          <div className="bg-white/[0.03] backdrop-blur-xl rounded-3xl border border-white/10 
                          shadow-glass-lg p-8">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-white">Entrar</h2>
              <p className="text-surface-400 text-sm mt-1">Acesse o painel de controle</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  E-mail
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500" />
                  <input
                    type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl 
                             text-white placeholder-surface-500 text-sm
                             focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500/50 
                             focus:bg-white/[0.07] outline-none transition-all duration-200"
                    placeholder="usuario@demo-mes.app" required autoFocus
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Senha
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500" />
                  <input
                    type={showPwd ? 'text' : 'password'} value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-11 pr-11 py-3 bg-white/5 border border-white/10 rounded-xl 
                             text-white placeholder-surface-500 text-sm
                             focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500/50
                             focus:bg-white/[0.07] outline-none transition-all duration-200"
                    placeholder="••••••••" required
                  />
                  <button type="button" onClick={() => setShowPwd(!showPwd)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-surface-500 hover:text-surface-300 transition-colors">
                    {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {error && (
                <div className="bg-danger/10 border border-danger/20 text-red-400 text-sm p-3 rounded-xl 
                              flex items-center gap-2 animate-slide-up">
                  <span className="w-1.5 h-1.5 rounded-full bg-danger shrink-0" />
                  {error}
                </div>
              )}

              <button type="submit" disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-3 px-4 
                         bg-gradient-to-r from-primary-600 to-primary-500 text-white font-semibold 
                         rounded-xl shadow-lg shadow-primary-500/25 
                         hover:shadow-xl hover:shadow-primary-500/30 hover:-translate-y-0.5
                         active:scale-[0.98] transition-all duration-200
                         disabled:opacity-50 disabled:pointer-events-none text-sm">
                {loading ? (
                  <div className="spinner w-5 h-5 border-white/30 border-t-white" />
                ) : (
                  <>Entrar <ArrowRight className="w-4 h-4" /></>
                )}
              </button>
            </form>

            {/* Demo credentials */}
            <div className="mt-6 pt-6 border-t border-white/10">
              <p className="text-xs font-medium text-surface-400 mb-3">
                Acesso Demo <span className="text-surface-500">— senha: demo1234</span>
              </p>
              <div className="grid grid-cols-5 gap-2">
                {demoUsers.map((u) => (
                  <button key={u.email} type="button"
                    onClick={() => { setEmail(u.email); setPassword('demo1234'); }}
                    className="flex flex-col items-center gap-1 p-2 rounded-xl 
                             bg-white/5 border border-white/5 
                             hover:bg-white/10 hover:border-white/15 
                             transition-all duration-200 group">
                    <span className="text-base group-hover:scale-110 transition-transform">{u.icon}</span>
                    <span className="text-[10px] font-medium text-surface-400 group-hover:text-surface-300">
                      {u.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <p className="text-center text-surface-600 text-xs mt-6">
            Synchro MES v2.0 — Portfolio Demo
          </p>
        </div>
      </div>
    </div>
  );
}
