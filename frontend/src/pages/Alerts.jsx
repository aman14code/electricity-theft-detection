import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import {
  ShieldAlert, Filter, MapPin, Clock, TrendingUp,
  ChevronRight, AlertCircle,
} from 'lucide-react';

const statusConfig = {
  pending: { class: 'badge-pending', label: 'Pending' },
  investigating: { class: 'badge-investigating', label: 'Investigating' },
  resolved: { class: 'badge-resolved', label: 'Resolved' },
};

const nextStatus = {
  pending: 'investigating',
  investigating: 'resolved',
  resolved: 'pending',
};

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  const fetchAlerts = async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const { data } = await api.get('/alerts', { params });
      setAlerts(data.data);
    } catch (err) {
      console.error('Fetch alerts error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [filter]);

  const toggleStatus = async (alertId, currentStatus) => {
    try {
      await api.patch(`/alerts/${alertId}`, {
        status: nextStatus[currentStatus],
      });
      fetchAlerts();
    } catch (err) {
      console.error('Status update error:', err);
    }
  };

  const getThreatColor = (score) => {
    if (score >= 0.75) return 'text-red-400';
    if (score >= 0.5) return 'text-orange-400';
    if (score >= 0.3) return 'text-amber-400';
    return 'text-green-400';
  };

  const getThreatBg = (score) => {
    if (score >= 0.75) return 'bg-red-500/10 border-red-500/20';
    if (score >= 0.5) return 'bg-orange-500/10 border-orange-500/20';
    if (score >= 0.3) return 'bg-amber-500/10 border-amber-500/20';
    return 'bg-green-500/10 border-green-500/20';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-10 h-10 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ─── Header ──────────────────────────────────────── */}
      <div>
        <h1 className="text-2xl font-bold text-white">Theft Alerts</h1>
        <p className="text-sm text-white/40 mt-1">
          {alerts.length} alerts flagged across your network
        </p>
      </div>

      {/* ─── Filters ─────────────────────────────────────── */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-white/30" />
        {['all', 'pending', 'investigating', 'resolved'].map((f) => (
          <button
            key={f}
            onClick={() => { setLoading(true); setFilter(f); }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all duration-200 capitalize ${
              filter === f
                ? 'bg-brand-500/20 text-brand-400 border border-brand-500/30'
                : 'bg-white/[0.04] text-white/40 border border-transparent hover:text-white/60'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* ─── Alerts table ────────────────────────────────── */}
      {alerts.length > 0 ? (
        <div className="glass-card overflow-hidden">
          {/* Header row */}
          <div className="hidden md:grid grid-cols-12 gap-4 px-6 py-3
                          bg-white/[0.02] border-b border-white/[0.06]
                          text-xs font-semibold text-white/40 uppercase tracking-wider">
            <div className="col-span-4">Meter Location</div>
            <div className="col-span-2">Probability</div>
            <div className="col-span-2">Status</div>
            <div className="col-span-2">Time</div>
            <div className="col-span-2 text-right">Actions</div>
          </div>

          {/* Alert rows */}
          <div className="divide-y divide-white/[0.04]">
            {alerts.map((alert, i) => (
              <div
                key={alert._id}
                className="grid grid-cols-1 md:grid-cols-12 gap-4 px-6 py-4
                           hover:bg-white/[0.02] transition-colors duration-150
                           animate-fade-in"
                style={{ animationDelay: `${i * 30}ms` }}
              >
                {/* Location */}
                <div className="col-span-4 flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center border
                                  ${getThreatBg(alert.theftProbabilityScore)}`}>
                    <ShieldAlert className={`w-4 h-4 ${getThreatColor(alert.theftProbabilityScore)}`} />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-white/80 truncate">
                      {alert.meter?.location || 'Unknown'}
                    </p>
                    <p className="text-xs text-white/30 flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {alert.meter?.consumerType || '—'}
                    </p>
                  </div>
                </div>

                {/* Probability */}
                <div className="col-span-2 flex items-center">
                  <div className="flex items-center gap-2">
                    <div className={`text-lg font-bold font-mono ${getThreatColor(alert.theftProbabilityScore)}`}>
                      {(alert.theftProbabilityScore * 100).toFixed(0)}%
                    </div>
                    <TrendingUp className={`w-4 h-4 ${getThreatColor(alert.theftProbabilityScore)}`} />
                  </div>
                </div>

                {/* Status */}
                <div className="col-span-2 flex items-center">
                  <button
                    onClick={() => toggleStatus(alert._id, alert.status)}
                    className={`${statusConfig[alert.status]?.class} cursor-pointer
                               hover:scale-105 transition-transform duration-150`}
                    title={`Click to change to ${nextStatus[alert.status]}`}
                  >
                    {statusConfig[alert.status]?.label}
                  </button>
                </div>

                {/* Time */}
                <div className="col-span-2 flex items-center text-xs text-white/40">
                  <Clock className="w-3 h-3 mr-1.5" />
                  {new Date(alert.createdAt).toLocaleDateString('en-US', {
                    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
                  })}
                </div>

                {/* Actions */}
                <div className="col-span-2 flex items-center justify-end">
                  <Link
                    to={`/meters/${alert.meter?._id}`}
                    className="flex items-center gap-1 text-xs text-brand-400 hover:text-brand-300
                               transition-colors font-medium"
                  >
                    View Meter <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="glass-card py-20 text-center">
          <AlertCircle className="w-12 h-12 text-white/10 mx-auto mb-4" />
          <p className="text-white/40">No alerts found</p>
          <p className="text-xs text-white/20 mt-1">
            Run anomaly analysis on a meter to generate alerts
          </p>
        </div>
      )}
    </div>
  );
}
