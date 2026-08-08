import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import { useToast } from '../context/ToastContext';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts';
import {
  BarChart2, ScanSearch, Loader2, ShieldAlert, CheckCircle2,
  Download, RefreshCw, ChevronRight, Zap, AlertTriangle,
} from 'lucide-react';

// ─── Risk level helpers ──────────────────────────────────
const RISK = {
  critical: { label: 'Critical', color: '#ef4444', bg: 'bg-red-500/15 border-red-500/30 text-red-400' },
  high:     { label: 'High',     color: '#f97316', bg: 'bg-orange-500/15 border-orange-500/30 text-orange-400' },
  medium:   { label: 'Medium',   color: '#f59e0b', bg: 'bg-amber-500/15 border-amber-500/30 text-amber-400' },
  low:      { label: 'Low',      color: '#22c55e', bg: 'bg-green-500/15 border-green-500/30 text-green-400' },
};

function getRisk(prob) {
  if (prob >= 0.75) return RISK.critical;
  if (prob >= 0.50) return RISK.high;
  if (prob >= 0.30) return RISK.medium;
  return RISK.low;
}

function getBarColor(prob) {
  if (prob >= 0.75) return '#ef4444';
  if (prob >= 0.50) return '#f97316';
  if (prob >= 0.30) return '#f59e0b';
  return '#22c55e';
}

// ─── Custom chart tooltip ────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const prob = payload[0]?.value ?? 0;
  const risk = getRisk(prob);
  return (
    <div className="glass-card px-4 py-3 !border-brand-500/20 !shadow-xl">
      <p className="text-xs font-semibold text-white/50 mb-1 truncate max-w-[160px]">{label}</p>
      <p className={`text-lg font-bold font-mono ${risk.color === '#22c55e' ? 'text-green-400' :
        risk.color === '#f59e0b' ? 'text-amber-400' :
        risk.color === '#f97316' ? 'text-orange-400' : 'text-red-400'}`}>
        {(prob * 100).toFixed(1)}%
      </p>
      <p className="text-xs text-white/30">{risk.label} risk</p>
    </div>
  );
};

// ─── CSV export helper ───────────────────────────────────
function exportCSV(results) {
  const rows = [
    ['Meter Location', 'Consumer Type', 'Theft Probability', 'Risk Level', 'Anomaly Detected'],
    ...results
      .filter((r) => r?.mlResult)
      .map((r) => [
        `"${r.meter.location}"`,
        r.meter.consumerType,
        (r.mlResult.theft_probability * 100).toFixed(1) + '%',
        r.mlResult.risk_level,
        r.anomalyDetected ? 'Yes' : 'No',
      ]),
  ];
  const csv = rows.map((r) => r.join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `powerguard_report_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function Reports() {
  const toast = useToast();
  const [meters, setMeters] = useState([]);
  const [bulkResult, setBulkResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [alerts, setAlerts] = useState([]);

  // Fetch meters list for chart (no analysis yet)
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [metersRes, alertsRes] = await Promise.all([
        api.get('/meters'),
        api.get('/alerts'),
      ]);
      setMeters(metersRes.data.data);
      setAlerts(alertsRes.data.data);
    } catch {
      toast.error('Failed to load report data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleBulkAnalyze = async () => {
    setAnalyzing(true);
    toast.info('Running analysis on all meters…');
    try {
      const { data } = await api.post('/analyze/bulk');
      setBulkResult(data);
      toast.success(`Analysis complete — ${data.summary.anomalies} anomalies detected`);
      fetchData(); // refresh alerts count
    } catch (err) {
      toast.error(err.response?.data?.message || 'Bulk analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  // ── Build chart data ──────────────────────────────────
  const chartData = bulkResult
    ? bulkResult.results
        .filter((r) => r?.mlResult)
        .map((r) => ({
          name: r.meter.location.replace(/ — .*/, '').replace(' ⚠️ SUSPICIOUS', ''),
          fullName: r.meter.location,
          prob: r.mlResult.theft_probability,
        }))
        .sort((a, b) => b.prob - a.prob)
    : [];

  // ── Alert severity breakdown from all-time alerts ────
  const alertSummary = {
    critical: alerts.filter((a) => a.theftProbabilityScore >= 0.75).length,
    high:     alerts.filter((a) => a.theftProbabilityScore >= 0.5 && a.theftProbabilityScore < 0.75).length,
    medium:   alerts.filter((a) => a.theftProbabilityScore >= 0.3 && a.theftProbabilityScore < 0.5).length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-10 h-10 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* ─── Header ──────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Reports & Analytics</h1>
          <p className="text-sm text-white/40 mt-1">
            {meters.length} meters across your network — {alerts.filter((a) => a.status !== 'resolved').length} active alerts
          </p>
        </div>
        <div className="flex items-center gap-3">
          {bulkResult && (
            <button
              onClick={() => exportCSV(bulkResult.results)}
              className="btn-ghost flex items-center gap-2"
            >
              <Download className="w-4 h-4" /> Export CSV
            </button>
          )}
          <button
            id="bulk-analyze-btn"
            onClick={handleBulkAnalyze}
            disabled={analyzing || meters.length === 0}
            className="btn-primary flex items-center gap-2"
          >
            {analyzing ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing all meters…</>
            ) : (
              <><ScanSearch className="w-4 h-4" /> Analyze All Meters</>
            )}
          </button>
        </div>
      </div>

      {/* ─── Summary KPI cards ────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {[
          {
            label: 'Total Meters', value: meters.length,
            icon: Zap, color: 'from-brand-500/20 to-brand-600/10', border: 'border-brand-500/20', iconColor: 'text-brand-400',
          },
          {
            label: 'Active Alerts', value: alerts.filter((a) => a.status !== 'resolved').length,
            icon: ShieldAlert, color: 'from-red-500/20 to-red-600/10', border: 'border-red-500/20', iconColor: 'text-red-400',
          },
          {
            label: 'Critical Risk', value: alertSummary.critical,
            icon: AlertTriangle, color: 'from-orange-500/20 to-red-600/10', border: 'border-orange-500/20', iconColor: 'text-orange-400',
          },
          {
            label: 'Resolved Cases', value: alerts.filter((a) => a.status === 'resolved').length,
            icon: CheckCircle2, color: 'from-green-500/20 to-green-600/10', border: 'border-green-500/20', iconColor: 'text-green-400',
          },
        ].map((card) => (
          <div key={card.label} className="glass-card p-5">
            <div className="flex items-start justify-between mb-4">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${card.color} flex items-center justify-center border ${card.border}`}>
                <card.icon className={`w-5 h-5 ${card.iconColor}`} />
              </div>
            </div>
            <p className="text-3xl font-bold text-white font-mono">{card.value}</p>
            <p className="text-xs text-white/40 mt-1">{card.label}</p>
          </div>
        ))}
      </div>

      {/* ─── Bulk Analysis Result ─────────────────────────── */}
      {bulkResult && (
        <div className="glass-card p-6 animate-slide-up">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500/20 to-electric-purple/20
                              flex items-center justify-center border border-brand-500/20">
                <BarChart2 className="w-5 h-5 text-brand-400" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Latest Bulk Analysis</h3>
                <p className="text-xs text-white/40">
                  {bulkResult.summary.analyzed} meters analyzed · {bulkResult.summary.anomalies} anomalies found
                </p>
              </div>
            </div>
            <button
              onClick={handleBulkAnalyze}
              disabled={analyzing}
              className="text-white/30 hover:text-white/60 transition-colors"
              title="Re-run analysis"
            >
              <RefreshCw className={`w-4 h-4 ${analyzing ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {/* Chart */}
          {chartData.length > 0 && (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis
                  dataKey="name"
                  tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 10 }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
                  tickLine={false}
                  angle={-30}
                  textAnchor="end"
                  interval={0}
                />
                <YAxis
                  tickFormatter={(v) => `${Math.round(v * 100)}%`}
                  tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  domain={[0, 1]}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="prob" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry, i) => (
                    <Cell key={i} fill={getBarColor(entry.prob)} opacity={0.85} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      )}

      {/* ─── Per-Meter Scorecards ─────────────────────────── */}
      {bulkResult && (
        <div className="space-y-3">
          <h2 className="text-xs font-semibold text-white/40 uppercase tracking-wider">
            Per-Meter Risk Scorecard
          </h2>
          <div className="glass-card overflow-hidden">
            {/* Table header */}
            <div className="hidden md:grid grid-cols-12 gap-4 px-6 py-3
                            bg-white/[0.02] border-b border-white/[0.06]
                            text-xs font-semibold text-white/40 uppercase tracking-wider">
              <div className="col-span-5">Meter</div>
              <div className="col-span-2">Probability</div>
              <div className="col-span-2">Risk Level</div>
              <div className="col-span-2">Status</div>
              <div className="col-span-1 text-right">View</div>
            </div>
            <div className="divide-y divide-white/[0.04]">
              {bulkResult.results
                .filter((r) => r?.mlResult)
                .sort((a, b) => b.mlResult.theft_probability - a.mlResult.theft_probability)
                .map((r, i) => {
                  const risk = getRisk(r.mlResult.theft_probability);
                  const pct = Math.round(r.mlResult.theft_probability * 100);
                  return (
                    <div
                      key={i}
                      className="grid grid-cols-1 md:grid-cols-12 gap-4 px-6 py-4
                                 hover:bg-white/[0.02] transition-colors duration-150 animate-fade-in"
                      style={{ animationDelay: `${i * 30}ms` }}
                    >
                      {/* Meter name */}
                      <div className="col-span-5 flex items-center gap-3 min-w-0">
                        <div className={`w-2 h-2 rounded-full flex-shrink-0`}
                          style={{ background: getBarColor(r.mlResult.theft_probability) }} />
                        <span className="text-sm text-white/80 truncate">{r.meter.location}</span>
                      </div>

                      {/* Probability bar */}
                      <div className="col-span-2 flex items-center gap-2">
                        <span className="font-bold font-mono text-sm"
                          style={{ color: getBarColor(r.mlResult.theft_probability) }}>
                          {pct}%
                        </span>
                        <div className="flex-1 h-1.5 bg-white/[0.06] rounded-full overflow-hidden max-w-[60px]">
                          <div
                            className="h-full rounded-full transition-all duration-700"
                            style={{
                              width: `${pct}%`,
                              background: getBarColor(r.mlResult.theft_probability),
                            }}
                          />
                        </div>
                      </div>

                      {/* Risk badge */}
                      <div className="col-span-2 flex items-center">
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold
                                         border ${risk.bg}`}>
                          {risk.label}
                        </span>
                      </div>

                      {/* Anomaly status */}
                      <div className="col-span-2 flex items-center">
                        {r.anomalyDetected ? (
                          <span className="flex items-center gap-1.5 text-xs text-red-400">
                            <ShieldAlert className="w-3.5 h-3.5" /> Alert created
                          </span>
                        ) : (
                          <span className="flex items-center gap-1.5 text-xs text-green-400">
                            <CheckCircle2 className="w-3.5 h-3.5" /> All clear
                          </span>
                        )}
                      </div>

                      {/* View link */}
                      <div className="col-span-1 flex items-center justify-end">
                        <Link
                          to={`/meters/${r.meter._id}`}
                          className="text-brand-400 hover:text-brand-300 transition-colors"
                          title="View meter"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </Link>
                      </div>
                    </div>
                  );
                })}
              {bulkResult.results.filter((r) => r?.skipped).length > 0 && (
                <div className="px-6 py-3 text-xs text-white/25">
                  {bulkResult.results.filter((r) => r?.skipped).length} meters skipped (no readings in last 30 days)
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ─── Empty state — no analysis yet ───────────────── */}
      {!bulkResult && (
        <div className="glass-card py-20 text-center">
          <BarChart2 className="w-14 h-14 text-white/10 mx-auto mb-5" />
          <h3 className="text-lg font-semibold text-white/40 mb-2">No Analysis Yet</h3>
          <p className="text-sm text-white/25 max-w-xs mx-auto">
            Click <strong className="text-white/40">Analyze All Meters</strong> to run the ML detection engine
            across your entire network and see a risk scorecard.
          </p>
        </div>
      )}
    </div>
  );
}
