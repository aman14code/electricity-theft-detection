import { useState, useEffect } from 'react';
import api from '../api/axios';
import MetricCard from '../components/MetricCard';
import { 
  Gauge, ShieldAlert, CheckCircle2, IndianRupee, 
  Activity, AlertTriangle, Users, MapPin, 
  TrendingDown, TrendingUp 
} from 'lucide-react';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, Legend
} from 'recharts';

// Define brand colors to match the premium theme
const COLORS = ['#ef4444', '#f59e0b', '#10b981', '#06b6d4', '#6366f1'];

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // Mock data for the 4 requested charts to display UI while backend is being built
  const dailyDetectionData = [
    { day: 'Mon', detections: 12 }, { day: 'Tue', detections: 19 },
    { day: 'Wed', detections: 15 }, { day: 'Thu', detections: 22 },
    { day: 'Fri', detections: 30 }, { day: 'Sat', detections: 25 },
    { day: 'Sun', detections: 18 }
  ];

  const areaTheftData = [
    { area: 'Sector 62', cases: 45 }, { area: 'Vasundhara', cases: 32 },
    { area: 'Indirapuram', cases: 58 }, { area: 'Vaishali', cases: 24 },
    { area: 'Kaushambi', cases: 15 }
  ];

  const riskDistributionData = [
    { name: 'High Risk (>70%)', value: 45 },
    { name: 'Medium Risk (30-70%)', value: 85 },
    { name: 'Low Risk (<30%)', value: 310 }
  ];

  const monthlyRecoveryData = [
    { month: 'Jan', amount: 120000 }, { month: 'Feb', amount: 180000 },
    { month: 'Mar', amount: 150000 }, { month: 'Apr', amount: 220000 },
    { month: 'May', amount: 310000 }, { month: 'Jun', amount: 280000 }
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes] = await Promise.all([
          api.get('/dashboard/stats')
        ]);
        setStats(statsRes.data.data);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-white/40">Loading Phase 1 Dashboard…</p>
        </div>
      </div>
    );
  }

  // Derive new metrics from available stats or use placeholders
  const totalMeters = stats?.totalMeters || 12450;
  const activeMeters = stats?.activeMeters || 12380;
  const inactiveMeters = totalMeters - activeMeters;
  const totalTheftCases = (stats?.activeAlerts || 0) + (stats?.resolvedAlerts || 0) + 142; // Example baseline
  const theftPercentage = ((totalTheftCases / totalMeters) * 100).toFixed(1);
  const pendingInspections = stats?.activeAlerts || 45;
  const estimatedRevenueLoss = (totalTheftCases * 4500).toLocaleString('en-IN'); // Assume ~₹4,500 loss per case

  return (
    <div className="space-y-6">
      {/* ─── Header ──────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Activity className="text-brand-400" /> Executive Dashboard
          </h1>
          <p className="text-sm text-white/40 mt-1">
            Real-time KPIs and Analytics for DISCOM Operations
          </p>
        </div>
        <div className="flex gap-2 text-xs">
          <div className="px-3 py-1.5 rounded-lg bg-green-500/10 text-green-400 border border-green-500/20 flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" /> Live Sync
          </div>
        </div>
      </div>

      {/* ─── 1. Live Statistics Cards (6 Cards) ──────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <MetricCard
          title="Total Monitored"
          value={totalMeters.toLocaleString()}
          subtitle="Smart meters online"
          icon={Gauge}
          color="brand"
        />
        <MetricCard
          title="Active vs Inactive"
          value={`${activeMeters}`}
          subtitle={`${inactiveMeters} meters offline`}
          icon={Activity}
          color="cyan"
        />
        <MetricCard
          title="Suspected Theft"
          value={totalTheftCases}
          subtitle={`${theftPercentage}% of network`}
          icon={ShieldAlert}
          color="red"
        />
        <MetricCard
          title="Risk Distribution"
          value="45 H"
          subtitle="85 M | 310 L"
          icon={AlertTriangle}
          color="orange"
        />
        <MetricCard
          title="Pending Inspections"
          value={pendingInspections}
          subtitle="Awaiting field officers"
          icon={Users}
          color="amber"
        />
        <MetricCard
          title="Est. Revenue Loss"
          value={`₹${estimatedRevenueLoss}`}
          subtitle="Current billing cycle"
          icon={IndianRupee}
          color="brand"
        />
      </div>

      {/* ─── 2. Visual Charts (4 Charts) ─────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chart A: Daily Detection Rate */}
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white/90 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-brand-400" />
              Daily Detection Rate
            </h3>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dailyDetectionData}>
                <defs>
                  <linearGradient id="colorDetections" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="day" stroke="#ffffff40" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#ffffff40" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#ffffff20', borderRadius: '8px', color: '#fff' }}
                  itemStyle={{ color: '#ef4444' }}
                />
                <Area type="monotone" dataKey="detections" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#colorDetections)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart B: Theft Cases by Area */}
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white/90 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-cyan-400" />
              Theft Cases by Area / Feeder
            </h3>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={areaTheftData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="area" stroke="#ffffff40" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#ffffff40" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#ffffff20', borderRadius: '8px', color: '#fff' }}
                  cursor={{ fill: '#ffffff05' }}
                />
                <Bar dataKey="cases" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart C: Risk Score Distribution */}
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white/90 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-orange-400" />
              Risk Score Distribution
            </h3>
          </div>
          <div className="h-64 flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {riskDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#ffffff20', borderRadius: '8px', color: '#fff' }}
                />
                <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px', color: '#ffffff80' }}/>
              </PieChart>
            </ResponsiveContainer>
            {/* Center Text */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none pb-8">
              <span className="text-2xl font-bold text-white">440</span>
              <span className="text-[10px] text-white/40 uppercase tracking-widest">Total Flags</span>
            </div>
          </div>
        </div>

        {/* Chart D: Monthly Revenue Recovery */}
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white/90 flex items-center gap-2">
              <IndianRupee className="w-4 h-4 text-green-400" />
              Monthly Revenue Recovery
            </h3>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyRecoveryData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="month" stroke="#ffffff40" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis 
                  stroke="#ffffff40" 
                  fontSize={12} 
                  tickLine={false} 
                  axisLine={false}
                  tickFormatter={(val) => `₹${val/1000}k`}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#ffffff20', borderRadius: '8px', color: '#fff' }}
                  formatter={(value) => [`₹${value.toLocaleString()}`, "Recovered"]}
                />
                <Line type="monotone" dataKey="amount" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}
