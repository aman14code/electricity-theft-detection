export default function MetricCard({ title, value, subtitle, icon: Icon, color = 'brand', trend }) {
  const colorMap = {
    brand: {
      bg: 'from-brand-500/20 to-brand-600/10',
      icon: 'from-brand-500 to-brand-600',
      shadow: 'shadow-brand-500/20',
      text: 'text-brand-400',
    },
    cyan: {
      bg: 'from-electric-cyan/20 to-electric-cyan/5',
      icon: 'from-cyan-500 to-cyan-600',
      shadow: 'shadow-cyan-500/20',
      text: 'text-cyan-400',
    },
    red: {
      bg: 'from-red-500/20 to-red-600/10',
      icon: 'from-red-500 to-red-600',
      shadow: 'shadow-red-500/20',
      text: 'text-red-400',
    },
    green: {
      bg: 'from-green-500/20 to-green-600/10',
      icon: 'from-green-500 to-green-600',
      shadow: 'shadow-green-500/20',
      text: 'text-green-400',
    },
    amber: {
      bg: 'from-amber-500/20 to-amber-600/10',
      icon: 'from-amber-500 to-amber-600',
      shadow: 'shadow-amber-500/20',
      text: 'text-amber-400',
    },
    purple: {
      bg: 'from-purple-500/20 to-purple-600/10',
      icon: 'from-purple-500 to-purple-600',
      shadow: 'shadow-purple-500/20',
      text: 'text-purple-400',
    },
  };

  const c = colorMap[color] || colorMap.brand;

  return (
    <div className="glass-card-hover p-5 animate-slide-up">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-white/40 mb-2">
            {title}
          </p>
          <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
          {subtitle && (
            <p className="text-xs text-white/40 mt-1.5">{subtitle}</p>
          )}
          {trend !== undefined && (
            <div className={`flex items-center gap-1 mt-2 text-xs font-medium
                            ${trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              <span>{trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%</span>
              <span className="text-white/30">vs last week</span>
            </div>
          )}
        </div>
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${c.icon}
                         flex items-center justify-center shadow-lg ${c.shadow}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>

      {/* Subtle glow bar at bottom */}
      <div className={`mt-4 h-1 rounded-full bg-gradient-to-r ${c.bg} opacity-60`} />
    </div>
  );
}
