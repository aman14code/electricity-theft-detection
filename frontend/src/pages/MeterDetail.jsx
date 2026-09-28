import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/axios';
import { useToast } from '../context/ToastContext';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, BarChart, Bar,
} from 'recharts';
import {
  ArrowLeft, MapPin, Zap, ScanSearch, Loader2,
  ShieldAlert, CheckCircle2, AlertTriangle, Home, Building2,
  Plus, X, UploadCloud, UserPlus, FileText, Smartphone
} from 'lucide-react';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card px-4 py-3 !border-brand-500/20 !shadow-xl">
      <p className="text-xs font-semibold text-white/60 mb-2">{label}</p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          <span className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
          <span className="text-white/50">{entry.name}:</span>
          <span className="font-semibold text-white">
            {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function MeterDetail() {
  const { id } = useParams();
  const toast = useToast();
  const [meter, setMeter] = useState(null);
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [days, setDays] = useState(7);

  // Modals
  const [showInspection, setShowInspection] = useState(false);
  const [dispatching, setDispatching] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [meterRes, readingsRes] = await Promise.all([
          api.get(`/meters/${id}`),
          api.get(`/readings/${id}?days=${days}`),
        ]);
        setMeter(meterRes.data.data);

        // Aggregate readings by day for the chart
        const byDay = {};
        readingsRes.data.data.forEach((r) => {
          const day = new Date(r.timestamp).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric',
          });
          if (!byDay[day]) {
            byDay[day] = { date: day, consumption: 0, avgVoltage: 0, avgCurrent: 0, count: 0 };
          }
          byDay[day].consumption += r.consumptionKwh;
          byDay[day].avgVoltage += r.voltage;
          byDay[day].avgCurrent += r.current;
          byDay[day].count++;
        });

        const aggregated = Object.values(byDay).map((d) => ({
          date: d.date,
          consumption: Math.round(d.consumption * 100) / 100,
          avgVoltage: Math.round((d.avgVoltage / d.count) * 10) / 10,
          avgCurrent: Math.round((d.avgCurrent / d.count) * 100) / 100,
        }));

        setReadings(aggregated);
      } catch (err) {
        console.error('Fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id, days]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setAnalysisResult(null);
    try {
      const { data } = await api.post(`/analyze/${id}`);
      setAnalysisResult(data);
      if (data.anomalyDetected) {
        toast.warning(`Anomaly detected! Theft probability: ${(data.mlResult.theft_probability * 100).toFixed(1)}%`);
      } else {
        toast.success('Analysis complete — no anomalies detected');
      }
    } catch (err) {
      const msg = err.response?.data?.message || 'Analysis failed';
      setAnalysisResult({ success: false, message: msg });
      toast.error(msg);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDispatch = (e) => {
    e.preventDefault();
    setDispatching(true);
    setTimeout(() => {
      setDispatching(false);
      setShowInspection(false);
      toast.success("Field Officer Dispatched! Evidence PDF sent via WhatsApp.");
    }, 1500);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-10 h-10 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!meter) {
    return (
      <div className="text-center py-20">
        <p className="text-white/40">Meter not found</p>
        <Link to="/meters" className="text-brand-400 text-sm mt-2 inline-block">← Back to meters</Link>
      </div>
    );
  }

  const breakdown = analysisResult?.mlResult?.anomaly_breakdown;

  return (
    <div className="space-y-6">
      {/* ─── Back + header ───────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <Link to="/meters" className="flex items-center gap-1 text-xs text-white/40 hover:text-white/60
                                        transition-colors mb-4">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Meters
          </Link>
          
          <div className="glass-card p-5 w-full max-w-2xl border-l-4 border-l-brand-500 relative overflow-hidden">
            <div className="absolute -right-10 -top-10 opacity-5 pointer-events-none">
              {meter.consumerType === 'commercial' ? <Building2 className="w-48 h-48" /> : <Home className="w-48 h-48" />}
            </div>
            <h1 className="text-2xl font-bold text-white mb-1">{meter.consumerName || "Unknown Consumer"}</h1>
            <p className="text-sm font-mono text-brand-400 mb-4">Meter ID: {meter.location}</p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2 border-t border-white/10 pt-4">
              <div>
                <p className="text-[10px] text-white/40 uppercase tracking-wider font-semibold">Connection</p>
                <p className="text-sm text-white/80 capitalize flex items-center gap-1 mt-1">
                  {meter.consumerType === 'commercial' ? <Building2 className="w-3 h-3" /> : <Home className="w-3 h-3" />}
                  {meter.consumerType}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-white/40 uppercase tracking-wider font-semibold">Feeder Area</p>
                <p className="text-sm text-white/80 flex items-center gap-1 mt-1 truncate">
                  <MapPin className="w-3 h-3" /> {meter.areaCode || 'Sector 62'}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-white/40 uppercase tracking-wider font-semibold">Expected Load</p>
                <p className="text-sm text-white/80 flex items-center gap-1 mt-1">
                  <Zap className="w-3 h-3" /> {meter.baselineConsumption} kW
                </p>
              </div>
              <div>
                <p className="text-[10px] text-white/40 uppercase tracking-wider font-semibold">Status</p>
                <p className="text-sm text-green-400 flex items-center gap-1 mt-1 font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" /> Active
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-3 shrink-0">
          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="btn-primary flex items-center justify-center gap-2 w-full sm:w-48 shadow-lg shadow-brand-500/20"
          >
            {analyzing ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing…</>
            ) : (
              <><ScanSearch className="w-4 h-4" /> Run AI Analysis</>
            )}
          </button>
          
          <button
            onClick={() => setShowInspection(true)}
            className="btn-ghost border border-amber-500/30 text-amber-400 hover:bg-amber-500/10 flex items-center justify-center gap-2 w-full sm:w-48"
          >
            <UserPlus className="w-4 h-4" /> Dispatch Officer
          </button>
        </div>
      </div>

      {/* ─── Analysis result ─────────────────────────────── */}
      {analysisResult && (
        <div className={`glass-card p-6 animate-slide-up border-t-4 ${
          analysisResult.anomalyDetected
            ? 'border-t-red-500'
            : analysisResult.success === false
              ? 'border-t-amber-500'
              : 'border-t-green-500'
        }`}>
          {analysisResult.success === false ? (
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <p className="text-sm text-amber-400">{analysisResult.message}</p>
            </div>
          ) : analysisResult.anomalyDetected ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Left Side: Overview and Breakdown */}
              <div>
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-14 h-14 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center">
                    <ShieldAlert className="w-7 h-7 text-red-400 animate-pulse" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-red-400">High Risk of Theft</h3>
                    <p className="text-sm text-white/60">
                      The AI is <span className="font-bold text-white">{(analysisResult.mlResult.theft_probability * 100).toFixed(1)}%</span> confident this consumer is engaging in NTL activities.
                    </p>
                  </div>
                </div>

                {/* ── Anomaly breakdown bars ──────────────────── */}
                {breakdown && (
                  <div className="mt-4 bg-black/20 p-4 rounded-xl border border-white/5">
                    <h4 className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-4">
                      Triggered Rules (Heuristics)
                    </h4>
                    <div className="space-y-3">
                      {Object.entries({
                        consumptionDrop: 'Consumption Drop',
                        voltageAnomaly: 'Voltage Anomaly',
                        currentAnomaly: 'Current Bypass',
                        powerFactorAnomaly: 'Power Factor',
                        tamperDetected: 'Tamper Detection',
                      }).map(([key, label]) => {
                        const score = breakdown[key] || 0;
                        const pct = Math.round(score * 100);
                        return (
                          <div key={key} className="group">
                            <div className="flex items-center justify-between text-xs mb-1">
                              <span className="text-white/60">{label}</span>
                              <span className={`font-mono font-bold ${
                                pct >= 70 ? 'text-red-400' :
                                pct >= 40 ? 'text-amber-400' :
                                'text-green-400'
                              }`}>{pct}%</span>
                            </div>
                            <div className="h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all duration-700 ease-out ${
                                  pct >= 70 ? 'bg-gradient-to-r from-red-500 to-red-400' :
                                  pct >= 40 ? 'bg-gradient-to-r from-amber-500 to-amber-400' :
                                  'bg-gradient-to-r from-green-500 to-green-400'
                                }`}
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>

              {/* Right Side: SHAP Explanation */}
              <div>
                {/* ── SHAP Feature Attributions ──────────────────── */}
                {analysisResult.mlResult.shap_explanations && analysisResult.mlResult.shap_explanations.length > 0 && (
                  <div className="bg-black/20 p-4 rounded-xl border border-white/5 h-full">
                    <h4 className="text-xs font-semibold text-brand-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                      <ScanSearch className="w-4 h-4" />
                      AI Decision Logic (SHAP Explainer)
                    </h4>
                    <p className="text-[11px] text-white/40 mb-4 leading-relaxed">
                      The Random Forest model flagged this meter primarily because of the following statistical deviations from normal Indian consumer baselines:
                    </p>
                    
                    <div className="space-y-2">
                      {/* Table Header */}
                      <div className="grid grid-cols-12 gap-2 text-[10px] font-bold text-white/30 uppercase tracking-wider px-2 pb-1 border-b border-white/5">
                        <div className="col-span-6">Feature (Symptom)</div>
                        <div className="col-span-3 text-right">Raw Value</div>
                        <div className="col-span-3 text-right">Impact</div>
                      </div>
                      
                      {/* Rows */}
                      {analysisResult.mlResult.shap_explanations.map((shap, idx) => (
                        <div key={idx} className="grid grid-cols-12 gap-2 items-center bg-white/[0.02] hover:bg-white/[0.04] transition-colors p-2 rounded border border-white/[0.02]">
                          <div className="col-span-6">
                            <p className="text-[11px] text-white/80 font-medium truncate">{shap.feature_name.replace(/_/g, ' ')}</p>
                          </div>
                          <div className="col-span-3 text-right">
                            <p className="text-[10px] text-white/50 font-mono">{shap.feature_value.toFixed(2)}</p>
                          </div>
                          <div className="col-span-3 text-right">
                            <div className="inline-flex items-center gap-1">
                              <span className="text-[10px] font-bold text-red-400">+{shap.shap_value.toFixed(2)}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-green-400" />
              <div>
                <h3 className="text-lg font-bold text-green-400">Normal Consumption Pattern</h3>
                <p className="text-sm text-white/50">
                  The AI confirms authentic usage. Theft probability:{' '}
                  <span className="font-bold text-green-400">
                    {(analysisResult.mlResult.theft_probability * 100).toFixed(1)}%
                  </span>
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ─── Time range selector ─────────────────────────── */}
      <div className="flex justify-between items-center mt-8">
        <h3 className="text-sm font-bold text-white/80 uppercase tracking-wider">
          Historical Telemetry
        </h3>
        <div className="flex gap-2">
          {[7, 14, 30].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase transition-all duration-200 ${
                days === d
                  ? 'bg-brand-500/20 text-brand-400 border border-brand-500/30'
                  : 'bg-white/[0.04] text-white/40 border border-transparent hover:text-white/60'
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
      </div>

      {/* ─── Consumption chart ───────────────────────────── */}
      <div className="glass-card p-6 border border-white/[0.06]">
        {readings.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={readings} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis
                dataKey="date"
                tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
                axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
                tickLine={false}
              />
              <YAxis
                yAxisId="left"
                tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: 16, fontSize: 12 }} iconType="circle" iconSize={8} />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="consumption"
                name="Consumption (kWh)"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ r: 3, fill: '#1e293b', stroke: '#3b82f6', strokeWidth: 2 }}
                activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2, fill: '#3b82f6' }}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="avgVoltage"
                name="Avg Voltage (V)"
                stroke="#06b6d4"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-64">
            <p className="text-white/30 text-sm font-medium">Awaiting smart meter telemetry for this period</p>
          </div>
        )}
      </div>

      {/* ─── Inspection Dispatch Modal ────────────────────────── */}
      {showInspection && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          onClick={() => setShowInspection(false)}
        >
          <div
            className="glass-card p-8 w-full max-w-lg animate-slide-up gradient-border border-amber-500/30"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center border border-amber-500/20">
                  <UserPlus className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">Create Inspection Ticket</h2>
                  <p className="text-xs text-white/40">Dispatch field officer to location</p>
                </div>
              </div>
              <button
                onClick={() => setShowInspection(false)}
                className="text-white/30 hover:text-white/60 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleDispatch} className="space-y-5">
              
              <div className="bg-black/30 p-3 rounded-lg border border-white/5 mb-2">
                <p className="text-[10px] text-white/40 uppercase font-bold mb-1">Target</p>
                <p className="text-sm text-white/90">{meter.consumerName} — {meter.location}</p>
                <p className="text-xs text-brand-400 mt-1">{meter.areaCode}, {meter.substation}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">
                    Priority Level
                  </label>
                  <select className="input-field py-2 text-sm text-red-400 font-semibold" defaultValue="high">
                    <option value="high">HIGH (Urgent)</option>
                    <option value="medium">MEDIUM</option>
                    <option value="low">LOW</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">
                    Assign Officer
                  </label>
                  <select className="input-field py-2 text-sm" required>
                    <option value="">Select Officer...</option>
                    <option value="ramesh">Inspector Ramesh K.</option>
                    <option value="suresh">Inspector Suresh M.</option>
                    <option value="vikas">Vikas (QRT Team)</option>
                  </select>
                </div>
              </div>
              
              <div className="space-y-2 mt-4">
                <label className="block text-xs font-semibold text-white/50 uppercase tracking-wider">
                  Auto-Generate Evidence Package
                </label>
                <div className="flex flex-col gap-2 bg-white/[0.02] p-3 rounded-lg border border-white/5">
                  <label className="flex items-center gap-2 text-sm text-white/80">
                    <input type="checkbox" defaultChecked className="rounded border-white/20 bg-transparent text-brand-500" />
                    <FileText className="w-4 h-4 text-brand-400" /> Attach SHAP AI Explanation (PDF)
                  </label>
                  <label className="flex items-center gap-2 text-sm text-white/80">
                    <input type="checkbox" defaultChecked className="rounded border-white/20 bg-transparent text-brand-500" />
                    <LineChart className="w-4 h-4 text-cyan-400" /> Attach 30-Day Consumption Graph (PDF)
                  </label>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setShowInspection(false)} className="btn-ghost flex-1 py-3">
                  Cancel
                </button>
                <button type="submit" disabled={dispatching} className="btn-primary bg-amber-600 hover:bg-amber-500 text-white flex-1 py-3 flex items-center justify-center gap-2">
                  {dispatching ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> Dispatching…</>
                  ) : (
                    <><Smartphone className="w-4 h-4" /> Send Ticket & WhatsApp</>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
