import { useState, useEffect } from 'react';
import api from '../api/axios';
import MetricCard from '../components/MetricCard';
import ConsumptionChart from '../components/ConsumptionChart';
import { Gauge, ShieldAlert, CheckCircle2, Activity, TrendingDown } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [consumption, setConsumption] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, consumptionRes] = await Promise.all([
          api.get('/dashboard/stats'),
          api.get('/dashboard/consumption'),
        ]);
        setStats(statsRes.data.data);
        setConsumption(consumptionRes.data.data);
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
          <p className="text-sm text-white/40">Loading dashboard…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* ─── Header ──────────────────────────────────────── */}
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-sm text-white/40 mt-1">
          Real-time overview of your power grid monitoring network
        </p>
      </div>

      {/* ─── Metric cards ────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricCard
          title="Total Meters"
          value={stats?.totalMeters || 0}
          subtitle={`${stats?.activeMeters || 0} active`}
          icon={Gauge}
          color="brand"
        />
        <MetricCard
          title="Active Alerts"
          value={stats?.activeAlerts || 0}
          subtitle="Pending + investigating"
          icon={ShieldAlert}
          color="red"
        />
        <MetricCard
          title="Resolved"
          value={stats?.resolvedAlerts || 0}
          subtitle="Successfully closed"
          icon={CheckCircle2}
          color="green"
        />
        <MetricCard
          title="Avg Threat Score"
          value={`${((stats?.avgTheftProbability || 0) * 100).toFixed(0)}%`}
          subtitle="Across active alerts"
          icon={Activity}
          color={stats?.avgTheftProbability >= 0.5 ? 'red' : stats?.avgTheftProbability >= 0.3 ? 'amber' : 'cyan'}
        />
      </div>

      {/* ─── Consumption chart ───────────────────────────── */}
      <ConsumptionChart
        data={consumption}
        title="Network Consumption — Last 7 Days"
        height={350}
      />

      {/* ─── Quick actions ───────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600
                            flex items-center justify-center">
              <TrendingDown className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Anomaly Detection</h3>
              <p className="text-xs text-white/40">8 detection measures active</p>
            </div>
          </div>
          <div className="space-y-2">
            {[
              { name: 'Consumption Drop', desc: 'Zero kWh during peak hours' },
              { name: 'Tamper Detection', desc: 'Hardware tamper flags' },
              { name: 'Current Bypass', desc: 'Low current + normal voltage' },
              { name: 'Voltage Anomaly', desc: 'Outside 190–250V range' },
            ].map((m, i) => (
              <div key={i} className="flex items-center gap-3 px-3 py-2 rounded-lg bg-white/[0.02]">
                <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
                <div>
                  <p className="text-xs font-medium text-white/70">{m.name}</p>
                  <p className="text-[10px] text-white/30">{m.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-electric-cyan to-electric-blue
                            flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">System Status</h3>
              <p className="text-xs text-white/40">All services operational</p>
            </div>
          </div>
          <div className="space-y-3">
            {[
              { service: 'Backend API', status: 'Online', color: 'bg-green-400' },
              { service: 'ML Service', status: 'Online', color: 'bg-green-400' },
              { service: 'MongoDB', status: 'Connected', color: 'bg-green-400' },
              { service: 'Real-time Monitor', status: 'Active', color: 'bg-green-400' },
            ].map((s, i) => (
              <div key={i} className="flex items-center justify-between px-3 py-2 rounded-lg bg-white/[0.02]">
                <span className="text-xs text-white/60">{s.service}</span>
                <div className="flex items-center gap-2">
                  <div className={`w-1.5 h-1.5 rounded-full ${s.color} animate-pulse`} />
                  <span className="text-xs text-green-400 font-medium">{s.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
