import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import type { ElementType } from 'react';
import {
  LayoutDashboard, Package, ShieldCheck, AlertOctagon,
  CalendarDays, Factory, X, ChevronRight, ClipboardList,
  PlayCircle, BarChart3, Recycle, History, FileText,
  Database, Users, Settings, Wrench, Megaphone,
} from 'lucide-react';

interface NavItem {
  to: string;
  label: string;
  icon: ElementType;
  perm: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const navSections: NavSection[] = [
  {
    title: 'Principal',
    items: [
      { to: '/', label: 'Dashboard', icon: LayoutDashboard, perm: 'dashboard' },
      { to: '/planning', label: 'Planejamento', icon: CalendarDays, perm: 'planejamento' },
      { to: '/orders', label: 'Ordens', icon: ClipboardList, perm: 'producao' },
      { to: '/launch', label: 'Lançamento', icon: PlayCircle, perm: 'producao' },
    ],
  },
  {
    title: 'Análise',
    items: [
      { to: '/analysis', label: 'Análise', icon: BarChart3, perm: 'dashboard' },
      { to: '/production', label: 'Produção', icon: Package, perm: 'producao' },
      { to: '/downtimes', label: 'Paradas', icon: AlertOctagon, perm: 'paradas' },
      { to: '/pmp', label: 'PMP', icon: Recycle, perm: 'producao' },
    ],
  },
  {
    title: 'Qualidade',
    items: [
      { to: '/quality', label: 'Qualidade', icon: ShieldCheck, perm: 'qualidade' },
      { to: '/tooling', label: 'Ferramentaria', icon: Wrench, perm: 'producao' },
      { to: '/setup', label: 'Setup Máquinas', icon: Settings, perm: 'producao' },
    ],
  },
  {
    title: 'Gestão',
    items: [
      { to: '/pcp', label: 'PCP', icon: Megaphone, perm: 'planejamento' },
      { to: '/leadership', label: 'Liderança', icon: Users, perm: 'producao' },
      { to: '/reports', label: 'Relatórios', icon: FileText, perm: 'relatorios' },
      { to: '/history', label: 'Histórico', icon: History, perm: 'admin' },
      { to: '/admin', label: 'Admin Dados', icon: Database, perm: 'admin' },
    ],
  },
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { hasPermission } = useAuth();

  return (
    <aside className={`
      fixed inset-y-0 left-0 z-40 w-[260px] 
      bg-surface-950 
      transform transition-transform duration-300 ease-out
      ${isOpen ? 'translate-x-0' : '-translate-x-full'} 
      md:relative md:translate-x-0 md:z-auto
      flex flex-col
    `}>
      <div className="absolute inset-0 bg-gradient-to-b from-primary-900/10 via-transparent to-primary-900/5 pointer-events-none" />

      <div className="h-16 flex items-center justify-between px-5 relative z-10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-primary-500 to-primary-700 p-2 rounded-xl shadow-glow-primary">
            <Factory className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="text-base font-bold text-white tracking-tight">Synchro</span>
            <span className="text-base font-bold text-primary-400 tracking-tight ml-1">MES</span>
          </div>
        </div>
        <button onClick={onClose} className="md:hidden p-1.5 hover:bg-white/10 rounded-lg transition-colors">
          <X className="w-4 h-4 text-surface-400" />
        </button>
      </div>

      <div className="mx-5 h-px bg-gradient-to-r from-transparent via-surface-700 to-transparent" />

      <nav className="mt-4 px-3 flex-1 relative z-10 overflow-y-auto space-y-4">
        {navSections.map((section) => {
          const visibleItems = section.items.filter(n => hasPermission(n.perm));
          if (visibleItems.length === 0) return null;
          return (
            <div key={section.title}>
              <p className="px-3 mb-2 text-[10px] font-semibold text-surface-500 uppercase tracking-[0.15em]">
                {section.title}
              </p>
              <div className="space-y-0.5">
                {visibleItems.map((item) => (
                  <NavLink key={item.to} to={item.to} end={item.to === '/'}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium 
                      transition-all duration-200 group relative
                      ${isActive
                        ? 'bg-primary-500/15 text-primary-400 shadow-inner-glow'
                        : 'text-surface-400 hover:bg-white/5 hover:text-surface-200'
                      }`
                    }>
                    {({ isActive }) => (
                      <>
                        {isActive && (
                          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-primary-500 rounded-r-full" />
                        )}
                        <item.icon className={`w-[18px] h-[18px] transition-colors ${isActive ? 'text-primary-400' : 'text-surface-500 group-hover:text-surface-300'}`} />
                        <span className="flex-1">{item.label}</span>
                        <ChevronRight className={`w-3.5 h-3.5 transition-all duration-200 
                          ${isActive ? 'opacity-100 text-primary-500' : 'opacity-0 group-hover:opacity-50'}`} />
                      </>
                    )}
                  </NavLink>
                ))}
              </div>
            </div>
          );
        })}
      </nav>

      <div className="p-4 relative z-10 shrink-0">
        <div className="bg-white/5 rounded-xl p-3 border border-white/5">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs text-surface-400">Sistema Online</span>
          </div>
          <p className="text-[10px] text-surface-600 mt-1.5">Synchro MES v2.0</p>
        </div>
      </div>
    </aside>
  );
}
