import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import { useToast } from '../context/ToastContext';
import {
  ShieldAlert, Filter, MapPin, Clock, TrendingUp,
  ChevronRight, AlertCircle, FileText, CheckCircle, XCircle
} from 'lucide-react';

const statusConfig = {
  pending: { class: 'bg-amber-500/10 text-amber-400 border border-amber-500/20', label: 'Pending' },
  investigating: { class: 'bg-blue-500/10 text-blue-400 border border-blue-500/20', label: 'Investigating' },
  resolved: { class: 'bg-green-500/10 text-green-400 border border-green-500/20', label: 'Resolved' },
};

const nextStatus = {
  pending: 'investigating',
  investigating: 'resolved',
  resolved: 'pending',
};

export default function Alerts() {
  const toast = useToast();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');

  const fetchAlerts = async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const { data } = await api.get('/alerts', { params });
      
      // Auto-sort by risk score descending (per PRD spec)
      const sorted = data.data.sort((a, b) => b.theftProbabilityScore - a.theftProbabilityScore);
      setAlerts(sorted);
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
      toast.success(`Alert marked as ${nextStatus[currentStatus]}`);
      fetchAlerts();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update alert');
    }
  };

  const getThreatColor = (score) => {
    if (score >= 0.70) return 'text-red-400';
    if (score >= 0.30) return 'text-amber-400';
    return 'text-green-400';
  };

  const getThreatBg = (score) => {
    if (score >= 0.70) return 'bg-red-500/10 border-red-500/20';
    if (score >= 0.30) return 'bg-amber-500/10 border-amber-500/20';
    return 'bg-green-500/10 border-green-500/20';
  };

  const getTopReason = (breakdown) => {
    if (!breakdown) return "Anomaly detected by AI";
    
    // Find the highest scoring breakdown measure
    let maxKey = "";
    let maxVal = 0;
    
    for (const [key, value] of Object.entries(breakdown)) {
      if (typeof value === 'number' && value > maxVal && key !== '$init') {
        maxVal = value;
        maxKey = key;
      }
    }
    
    if (maxVal === 0) return "General AI Anomaly";
    
    const readable = {
      consumption_drop: "Sudden Drop in Peak Usage",
      voltage_anomaly: "Severe Voltage Fluctuations",
      current_anomaly: "Suspicious Current Levels",
      power_factor_anomaly: "Low Power Factor",
      frequency_deviation: "Frequency Instability",
      tamper_detected: "Hardware Tamper Flag",
      pattern_irregularity: "Day/Night Pattern Inversion",
      flat_line_detection: "Flat-lined Consumption"
    };
    
    return readable[maxKey] || maxKey.replace(/_/g, ' ');
  };

  // Filter by Risk Threshold
  const filteredAlerts = alerts.filter(alert => {
    if (riskFilter === 'high') return alert.theftProbabilityScore >= 0.70;
    if (riskFilter === 'medium') return alert.theftProbabilityScore >= 0.30 && alert.theftProbabilityScore < 0.70;
    return true;
  });

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
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <ShieldAlert className="text-red-400" />
            Theft Alert Queue
          </h1>
          <p className="text-sm text-white/40 mt-1">
            {filteredAlerts.length} high-risk consumers prioritized by AI
          </p>
        </div>
        <div className="flex gap-2">
          <button className="btn-ghost flex items-center gap-2 text-xs">
            <FileText className="w-4 h-4" /> Export PDF
          </button>
          <button className="btn-primary text-xs">
            Bulk Assign Tickets
          </button>
        </div>
      </div>

      {/* ─── Filters ─────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 glass-card p-3 rounded-xl">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold text-white/40 uppercase px-2">Status:</span>
          {['all', 'pending', 'investigating', 'resolved'].map((f) => (
            <button
              key={f}
              onClick={() => { setLoading(true); setFilter(f); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 capitalize ${
                filter === f
                  ? 'bg-brand-500/20 text-brand-400 border border-brand-500/30'
                  : 'bg-white/[0.04] text-white/40 border border-transparent hover:text-white/60'
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold text-white/40 uppercase px-2">Risk Level:</span>
          <select 
            className="input-field py-1.5 text-xs w-32"
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
          >
            <option value="all">All Risks</option>
            <option value="high">High (&gt;70%)</option>
            <option value="medium">Medium (30-70%)</option>
          </select>
        </div>
      </div>

      {/* ─── Alerts table ────────────────────────────────── */}
      {filteredAlerts.length > 0 ? (
        <div className="glass-card overflow-hidden">
          {/* Header row */}
          <div className="hidden lg:grid grid-cols-12 gap-4 px-6 py-3
                          bg-white/[0.02] border-b border-white/[0.06]
                          text-xs font-semibold text-white/40 uppercase tracking-wider">
            <div className="col-span-3">Consumer & Location</div>
            <div className="col-span-2">Area / Feeder</div>
            <div className="col-span-1 text-center">Risk</div>
            <div className="col-span-2">Top Reason (AI)</div>
            <div className="col-span-1">Status</div>
            <div className="col-span-1">Alert Date</div>
            <div className="col-span-2 text-right">Actions</div>
          </div>

          {/* Alert rows */}
          <div className="divide-y divide-white/[0.04]">
            {filteredAlerts.map((alert, i) => (
              <div
                key={alert._id}
                className="grid grid-cols-1 lg:grid-cols-12 gap-4 px-6 py-4
                           hover:bg-white/[0.02] transition-colors duration-150
                           animate-fade-in items-center"
                style={{ animationDelay: `${i * 30}ms` }}
              >
                {/* Consumer & Location */}
                <div className="col-span-3 flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-lg flex flex-shrink-0 items-center justify-center border
                                  ${getThreatBg(alert.theftProbabilityScore)}`}>
                    <ShieldAlert className={`w-4 h-4 ${getThreatColor(alert.theftProbabilityScore)}`} />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-white/90 truncate">
                      {alert.meter?.consumerName || 'Unknown Consumer'}
                    </p>
                    <p className="text-xs text-brand-400 font-mono truncate">
                      ID: {alert.meter?.location || 'N/A'}
                    </p>
                  </div>
                </div>

                {/* Area / Feeder */}
                <div className="col-span-2">
                  <p className="text-xs font-medium text-white/70">
                    {alert.meter?.areaCode || 'General Area'}
                  </p>
                  <p className="text-xs text-white/30 flex items-center gap-1 mt-0.5">
                    <MapPin className="w-3 h-3" />
                    {alert.meter?.substation || 'Main Substation'}
                  </p>
                </div>

                {/* Risk Score */}
                <div className="col-span-1 flex justify-center">
                  <div className={`text-sm font-bold font-mono px-2 py-1 rounded border bg-black/20 ${getThreatColor(alert.theftProbabilityScore)} ${getThreatBg(alert.theftProbabilityScore)}`}>
                    {(alert.theftProbabilityScore * 100).toFixed(0)}%
                  </div>
                </div>

                {/* Top Reason (AI) */}
                <div className="col-span-2">
                  <p className="text-xs text-white/60 leading-tight">
                    {getTopReason(alert.anomalyBreakdown)}
                  </p>
                </div>

                {/* Status */}
                <div className="col-span-1">
                  <button
                    onClick={() => toggleStatus(alert._id, alert.status)}
                    className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider cursor-pointer hover:scale-105 transition-transform duration-150 ${statusConfig[alert.status]?.class}`}
                    title={`Click to change to ${nextStatus[alert.status]}`}
                  >
                    {statusConfig[alert.status]?.label}
                  </button>
                </div>

                {/* Time */}
                <div className="col-span-1 text-[11px] text-white/40">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(alert.createdAt).toLocaleDateString('en-GB')}
                  </div>
                </div>

                {/* Actions */}
                <div className="col-span-2 flex items-center justify-end gap-2">
                  <button className="w-7 h-7 rounded bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/40 hover:text-green-400 transition-colors" title="Mark as False Alarm">
                    <CheckCircle className="w-4 h-4" />
                  </button>
                  <Link
                    to={`/meters/${alert.meter?._id}`}
                    className="flex items-center gap-1 px-3 py-1.5 rounded bg-brand-500/20 text-brand-400 hover:bg-brand-500/30
                               transition-colors text-xs font-semibold"
                  >
                    Details <ChevronRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="glass-card py-20 text-center">
          <AlertCircle className="w-12 h-12 text-white/10 mx-auto mb-4" />
          <p className="text-white/40">No alerts found matching your filters</p>
          <p className="text-xs text-white/20 mt-1">
            Run bulk analysis or adjust filters to see high-risk consumers
          </p>
        </div>
      )}
    </div>
  );
}
