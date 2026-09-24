import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Gauge,
  ShieldAlert,
  BarChart2,
  Brain,
  LogOut,
  Zap,
  ChevronRight,
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/meters', icon: Gauge, label: 'Meters' },
  { to: '/alerts', icon: ShieldAlert, label: 'Alerts' },
  { to: '/reports', icon: BarChart2, label: 'Reports' },
  { to: '/model-performance', icon: Brain, label: 'ML Models' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-[260px] z-40
                      bg-surface-900/80 backdrop-blur-2xl
                      border-r border-white/[0.06]
                      flex flex-col">
      {/* ─── Logo ───────────────────────────────────────── */}
      <div className="px-6 py-6 border-b border-white/[0.06]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-electric-cyan to-electric-blue
                          flex items-center justify-center shadow-lg shadow-brand-500/30">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold gradient-text leading-tight">PowerGuard</h1>
            <p className="text-[11px] text-white/30 font-medium tracking-wider uppercase">Theft Detection</p>
          </div>
        </div>
      </div>

      {/* ─── Navigation ─────────────────────────────────── */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `group flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium
               transition-all duration-200 ease-out
               ${isActive
                 ? 'bg-brand-500/15 text-brand-400 border border-brand-500/20 shadow-lg shadow-brand-500/10'
                 : 'text-white/50 hover:text-white/80 hover:bg-white/[0.04] border border-transparent'
               }`
            }
          >
            <Icon className="w-[18px] h-[18px] flex-shrink-0" />
            <span className="flex-1">{label}</span>
            <ChevronRight className="w-4 h-4 opacity-0 -translate-x-1
                                     group-hover:opacity-50 group-hover:translate-x-0
                                     transition-all duration-200" />
          </NavLink>
        ))}
      </nav>

      {/* ─── User / Logout ──────────────────────────────── */}
      <div className="px-3 py-4 border-t border-white/[0.06]">
        <div className="px-4 py-3 rounded-xl bg-white/[0.03] mb-2">
          <p className="text-sm font-semibold text-white/80 truncate">
            {user?.name || 'Company'}
          </p>
          <p className="text-xs text-white/30 truncate mt-0.5">
            {user?.email || ''}
          </p>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm
                     text-red-400/70 hover:text-red-400 hover:bg-red-500/10
                     transition-all duration-200"
        >
          <LogOut className="w-[18px] h-[18px]" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
