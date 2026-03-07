import { useAuth } from '../../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { Menu, LogOut, Bell, Search } from 'lucide-react';

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/production': 'Produção',
  '/quality': 'Qualidade',
  '/downtimes': 'Paradas',
  '/planning': 'Planejamento',
  '/orders': 'Ordens de Produção',
  '/launch': 'Lançamento',
  '/analysis': 'Análise',
  '/pmp': 'PMP — Moído / Borra / Sucata',
  '/history': 'Histórico',
  '/reports': 'Relatórios',
  '/admin': 'Admin — Dados Mestres',
  '/leadership': 'Liderança',
  '/setup': 'Setup de Máquinas',
  '/tooling': 'Ferramentaria',
  '/pcp': 'PCP',
};

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const currentPage = pageTitles[location.pathname] || 'Synchro MES';

  return (
    <header className="h-16 bg-white/80 backdrop-blur-md border-b border-surface-200/60 
                       flex items-center justify-between px-4 md:px-8 sticky top-0 z-20">
      {/* Left */}
      <div className="flex items-center gap-4">
        <button onClick={onMenuClick} 
          className="md:hidden p-2 hover:bg-surface-100 rounded-xl transition-colors">
          <Menu className="w-5 h-5 text-surface-600" />
        </button>
        <div>
          <h1 className="text-lg font-semibold text-surface-900 tracking-tight">{currentPage}</h1>
          <p className="text-xs text-surface-400 hidden sm:block">
            {new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })}
          </p>
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-2">
        <button className="p-2.5 hover:bg-surface-100 rounded-xl text-surface-400 
                          hover:text-surface-600 transition-colors hidden sm:flex">
          <Search className="w-[18px] h-[18px]" />
        </button>

        <button className="p-2.5 hover:bg-surface-100 rounded-xl text-surface-400 
                          hover:text-surface-600 transition-colors relative">
          <Bell className="w-[18px] h-[18px]" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-danger rounded-full ring-2 ring-white" />
        </button>

        <div className="w-px h-8 bg-surface-200 mx-1 hidden sm:block" />

        <div className="flex items-center gap-2.5 pl-1">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 
                         text-white flex items-center justify-center text-xs font-bold
                         shadow-md shadow-primary-500/20">
            {user?.avatar_initials || 'US'}
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-semibold text-surface-900 leading-tight">{user?.name || 'Usuário'}</p>
            <p className="text-[11px] text-surface-400 capitalize">{user?.role || ''}</p>
          </div>
          <button onClick={handleLogout} 
            className="p-2 hover:bg-red-50 rounded-xl text-surface-400 hover:text-danger 
                      transition-all duration-200 ml-1" 
            title="Sair">
            <LogOut className="w-[18px] h-[18px]" />
          </button>
        </div>
      </div>
    </header>
  );
}
