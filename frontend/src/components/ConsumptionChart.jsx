import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;

  return (
    <div className="glass-card px-4 py-3 !border-brand-500/20 !shadow-xl !shadow-brand-500/10">
      <p className="text-xs font-semibold text-white/60 mb-2">{label}</p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          <span className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
          <span className="text-white/50">{entry.name}:</span>
          <span className="font-semibold text-white">{entry.value?.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
};

export default function ConsumptionChart({ data, title = 'Network Consumption', height = 320 }) {
  return (
    <div className="glass-card p-6 animate-fade-in">
      <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-6">
        {title}
      </h3>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="colorConsumption" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorVoltage" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255,255,255,0.04)"
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
            axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: 16, fontSize: 12 }}
            iconType="circle"
            iconSize={8}
          />
          <Area
            type="monotone"
            dataKey="totalConsumption"
            name="Consumption (kWh)"
            stroke="#3b82f6"
            strokeWidth={2.5}
            fill="url(#colorConsumption)"
            dot={false}
            activeDot={{ r: 5, stroke: '#3b82f6', strokeWidth: 2, fill: '#1e293b' }}
          />
          {data?.[0]?.avgVoltage && (
            <Area
              type="monotone"
              dataKey="avgVoltage"
              name="Avg Voltage (V)"
              stroke="#06b6d4"
              strokeWidth={2}
              fill="url(#colorVoltage)"
              dot={false}
              activeDot={{ r: 4, stroke: '#06b6d4', strokeWidth: 2, fill: '#1e293b' }}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
