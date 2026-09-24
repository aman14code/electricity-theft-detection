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
  Plus, X, UploadCloud,
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

// ─── Default blank reading form ──────────────────────────
function blankReading() {
  return {
    consumptionKwh: '',
    voltage: '230',
    current: '',
    powerFactor: '0.92',
    frequency: '50',
    tamperFlag: false,
  };
}

export default function MeterDetail() {
  const { id } = useParams();
  const toast = useToast();
  const [meter, setMeter] = useState(null);
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [days, setDays] = useState(7);

  // Ingest modal state
  const [showIngest, setShowIngest] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [ingestForm, setIngestForm] = useState(blankReading());
  const [ingestCount, setIngestCount] = useState(24);

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

  // ─── Ingest simulated readings ───────────────────────
  const handleIngest = async (e) => {
    e.preventDefault();
    setIngesting(true);
    try {
      const now = new Date();
      const readingsPayload = Array.from({ length: ingestCount }, (_, i) => {
        const ts = new Date(now.getTime() - (ingestCount - 1 - i) * 3600 * 1000);
        return {
          meter: id,
          timestamp: ts.toISOString(),
          consumptionKwh: parseFloat(ingestForm.consumptionKwh) || 0,
          voltage: parseFloat(ingestForm.voltage) || 230,
          current: parseFloat(ingestForm.current) || 0,
          powerFactor: parseFloat(ingestForm.powerFactor) || 0.92,
          frequency: parseFloat(ingestForm.frequency) || 50,
          tamperFlag: ingestForm.tamperFlag,
        };
      });

      await api.post('/readings', { readings: readingsPayload });
      toast.success(`${ingestCount} readings ingested successfully`);
      setShowIngest(false);
      setIngestForm(blankReading());
      // Refresh chart
      const readingsRes = await api.get(`/readings/${id}?days=${days}`);
      const byDay = {};
      readingsRes.data.data.forEach((r) => {
        const day = new Date(r.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        if (!byDay[day]) byDay[day] = { date: day, consumption: 0, avgVoltage: 0, avgCurrent: 0, count: 0 };
        byDay[day].consumption += r.consumptionKwh;
        byDay[day].avgVoltage += r.voltage;
        byDay[day].avgCurrent += r.current;
        byDay[day].count++;
      });
      setReadings(Object.values(byDay).map((d) => ({
        date: d.date,
        consumption: Math.round(d.consumption * 100) / 100,
        avgVoltage: Math.round((d.avgVoltage / d.count) * 10) / 10,
        avgCurrent: Math.round((d.avgCurrent / d.count) * 100) / 100,
      })));
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to ingest readings');
    } finally {
      setIngesting(false);
    }
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Link to="/meters" className="flex items-center gap-1 text-xs text-white/40 hover:text-white/60
                                        transition-colors mb-2">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Meters
          </Link>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            {meter.consumerType === 'commercial' ? (
              <Building2 className="w-6 h-6 text-brand-400" />
            ) : (
              <Home className="w-6 h-6 text-brand-400" />
            )}
            {meter.location}
          </h1>
          <div className="flex items-center gap-4 mt-2 text-xs text-white/40">
            <span className="flex items-center gap-1">
              <MapPin className="w-3 h-3" /> {meter.consumerType}
            </span>
            <span className="flex items-center gap-1">
              <Zap className="w-3 h-3" /> {meter.baselineConsumption} kWh/hr baseline
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            id="ingest-btn"
            onClick={() => setShowIngest(true)}
            className="btn-ghost flex items-center gap-2 w-fit"
          >
            <Plus className="w-4 h-4" /> Add Readings
          </button>
          <button
            id="analyze-btn"
            onClick={handleAnalyze}
            disabled={analyzing}
            className="btn-primary flex items-center gap-2 w-fit"
          >
            {analyzing ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing…</>
            ) : (
              <><ScanSearch className="w-4 h-4" /> Analyze Anomalies</>
            )}
          </button>
        </div>
      </div>

      {/* ─── Analysis result ─────────────────────────────── */}
      {analysisResult && (
        <div className={`glass-card p-6 animate-slide-up border-l-4 ${
          analysisResult.anomalyDetected
            ? 'border-l-red-500'
            : analysisResult.success === false
              ? 'border-l-amber-500'
              : 'border-l-green-500'
        }`}>
          {analysisResult.success === false ? (
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <p className="text-sm text-amber-400">{analysisResult.message}</p>
            </div>
          ) : analysisResult.anomalyDetected ? (
            <div>
              <div className="flex items-center gap-3 mb-4">
                <ShieldAlert className="w-6 h-6 text-red-400" />
                <div>
                  <h3 className="text-lg font-bold text-red-400">Anomaly Detected!</h3>
                  <p className="text-sm text-white/50">
                    Theft probability:{' '}
                    <span className="font-bold text-red-400">
                      {(analysisResult.mlResult.theft_probability * 100).toFixed(1)}%
                    </span>
                    {' '}— Risk:{' '}
                    <span className={`font-bold ${
                      analysisResult.mlResult.risk_level === 'critical' ? 'text-red-400' :
                      analysisResult.mlResult.risk_level === 'high' ? 'text-orange-400' :
                      analysisResult.mlResult.risk_level === 'medium' ? 'text-amber-400' :
                      'text-green-400'
                    }`}>
                      {analysisResult.mlResult.risk_level?.toUpperCase()}
                    </span>
                  </p>
                </div>
              </div>

              {/* ── Anomaly breakdown bars ──────────────────── */}
              {breakdown && (
                <div className="mt-4">
                  <h4 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">
                    Detection Measure Breakdown
                  </h4>
                  <div className="space-y-2">
                    {Object.entries({
                      consumptionDrop: 'Consumption Drop',
                      voltageAnomaly: 'Voltage Anomaly',
                      currentAnomaly: 'Current Bypass',
                      powerFactorAnomaly: 'Power Factor',
                      frequencyDeviation: 'Frequency Drift',
                      tamperDetected: 'Tamper Detection',
                      patternIrregularity: 'Pattern Irregularity',
                      flatLineDetection: 'Flat-line Detection',
                    }).map(([key, label]) => {
                      const score = breakdown[key] || 0;
                      const pct = Math.round(score * 100);
                      return (
                        <div key={key} className="group">
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-white/50">{label}</span>
                            <span className={`font-mono font-bold ${
                              pct >= 70 ? 'text-red-400' :
                              pct >= 40 ? 'text-amber-400' :
                              'text-green-400'
                            }`}>{pct}%</span>
                          </div>
                          <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
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

              {/* ── Ensemble Model Scores (New) ──────────────────── */}
              {analysisResult.mlResult.model_scores && analysisResult.mlResult.model_scores.length > 0 && (
                <div className="mt-6 border-t border-white/10 pt-4">
                  <h4 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">
                    Ensemble Details ({analysisResult.mlResult.ensemble_method})
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {analysisResult.mlResult.model_scores.map((score, idx) => (
                      <div key={idx} className="bg-white/5 rounded-lg p-3">
                        <p className="text-[11px] text-white/40 uppercase font-semibold">{score.model_name}</p>
                        <div className="flex items-end justify-between mt-1">
                          <p className={`text-lg font-bold ${score.probability >= 0.5 ? 'text-red-400' : 'text-green-400'}`}>
                            {(score.probability * 100).toFixed(1)}%
                          </p>
                          <p className="text-[10px] text-white/30 uppercase">{score.prediction}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── SHAP Feature Attributions (New) ──────────────────── */}
              {analysisResult.mlResult.shap_explanations && analysisResult.mlResult.shap_explanations.length > 0 && (
                <div className="mt-6 border-t border-white/10 pt-4">
                  <h4 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">
                    Top Risk Factors (SHAP Explanability)
                  </h4>
                  <div className="space-y-3">
                    {analysisResult.mlResult.shap_explanations.map((shap, idx) => (
                      <div key={idx} className="flex items-center justify-between bg-white/[0.02] p-2 px-3 rounded-lg border border-white/[0.05]">
                        <div>
                          <p className="text-sm text-white/80">{shap.feature_name.replace(/_/g, ' ')}</p>
                          <p className="text-[10px] text-white/40">Value: {shap.feature_value.toFixed(2)}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-bold text-red-400">+{shap.shap_value.toFixed(4)}</p>
                          <p className="text-[10px] text-white/40">impact</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-green-400" />
              <div>
                <h3 className="text-lg font-bold text-green-400">All Clear</h3>
                <p className="text-sm text-white/50">
                  No anomalies detected — probability:{' '}
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
      <div className="flex gap-2">
        {[7, 14, 30].map((d) => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all duration-200 ${
              days === d
                ? 'bg-brand-500/20 text-brand-400 border border-brand-500/30'
                : 'bg-white/[0.04] text-white/40 border border-transparent hover:text-white/60'
            }`}
          >
            {d} Days
          </button>
        ))}
      </div>

      {/* ─── Consumption chart ───────────────────────────── */}
      <div className="glass-card p-6">
        <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-6">
          Daily Consumption
        </h3>
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
                tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: 16, fontSize: 12 }} iconType="circle" iconSize={8} />
              <Line
                type="monotone"
                dataKey="consumption"
                name="Consumption (kWh)"
                stroke="#3b82f6"
                strokeWidth={2.5}
                dot={{ r: 4, fill: '#1e293b', stroke: '#3b82f6', strokeWidth: 2 }}
                activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2, fill: '#3b82f6' }}
              />
              <Line
                type="monotone"
                dataKey="avgVoltage"
                name="Avg Voltage (V)"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={{ r: 3, fill: '#1e293b', stroke: '#06b6d4', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-64">
            <p className="text-white/30 text-sm">No readings for this period</p>
          </div>
        )}
      </div>

      {/* ─── Ingest Readings Modal ────────────────────────── */}
      {showIngest && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          onClick={() => setShowIngest(false)}
        >
          <div
            className="glass-card p-8 w-full max-w-md animate-slide-up gradient-border"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500/20 to-electric-purple/20
                                flex items-center justify-center border border-brand-500/20">
                  <UploadCloud className="w-4 h-4 text-brand-400" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-white">Ingest Readings</h2>
                  <p className="text-xs text-white/30">Add simulated hourly readings</p>
                </div>
              </div>
              <button
                onClick={() => setShowIngest(false)}
                className="text-white/30 hover:text-white/60 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleIngest} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">
                    Consumption (kWh)
                  </label>
                  <input
                    id="ingest-consumption"
                    type="number"
                    step="0.01"
                    min="0"
                    value={ingestForm.consumptionKwh}
                    onChange={(e) => setIngestForm({ ...ingestForm, consumptionKwh: e.target.value })}
                    placeholder="e.g. 0 for suspicious"
                    className="input-field"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">
                    Voltage (V)
                  </label>
                  <input
                    id="ingest-voltage"
                    type="number"
                    step="0.1"
                    value={ingestForm.voltage}
                    onChange={(e) => setIngestForm({ ...ingestForm, voltage: e.target.value })}
                    className="input-field"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">
                    Current (A)
                  </label>
                  <input
                    id="ingest-current"
                    type="number"
                    step="0.01"
                    min="0"
                    value={ingestForm.current}
                    onChange={(e) => setIngestForm({ ...ingestForm, current: e.target.value })}
                    placeholder="e.g. 0.01 for bypass"
                    className="input-field"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">
                    Power Factor
                  </label>
                  <input
                    id="ingest-pf"
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={ingestForm.powerFactor}
                    onChange={(e) => setIngestForm({ ...ingestForm, powerFactor: e.target.value })}
                    className="input-field"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">
                    Frequency (Hz)
                  </label>
                  <input
                    id="ingest-frequency"
                    type="number"
                    step="0.1"
                    value={ingestForm.frequency}
                    onChange={(e) => setIngestForm({ ...ingestForm, frequency: e.target.value })}
                    className="input-field"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">
                    # of Readings
                  </label>
                  <input
                    id="ingest-count"
                    type="number"
                    min="1"
                    max="720"
                    value={ingestCount}
                    onChange={(e) => setIngestCount(parseInt(e.target.value) || 24)}
                    className="input-field"
                  />
                </div>
              </div>

              {/* Tamper flag toggle */}
              <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <button
                  type="button"
                  id="ingest-tamper"
                  onClick={() => setIngestForm({ ...ingestForm, tamperFlag: !ingestForm.tamperFlag })}
                  className={`relative w-10 h-5 rounded-full transition-colors duration-200 flex-shrink-0 ${
                    ingestForm.tamperFlag ? 'bg-red-500' : 'bg-white/10'
                  }`}
                >
                  <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200 ${
                    ingestForm.tamperFlag ? 'translate-x-5' : 'translate-x-0.5'
                  }`} />
                </button>
                <div>
                  <p className="text-xs font-semibold text-white/70">Tamper Flag</p>
                  <p className="text-[11px] text-white/30">Mark readings as hardware tampered</p>
                </div>
              </div>

              {/* Hint */}
              <p className="text-[11px] text-white/25 leading-relaxed">
                Readings will be injected as {ingestCount} consecutive hourly timestamps ending now.
                Use consumption=0 + tamper=on to simulate a theft scenario.
              </p>

              <div className="flex gap-3 pt-1">
                <button type="button" onClick={() => setShowIngest(false)} className="btn-ghost flex-1">
                  Cancel
                </button>
                <button type="submit" disabled={ingesting} className="btn-primary flex-1 flex items-center justify-center gap-2">
                  {ingesting ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> Ingesting…</>
                  ) : (
                    <><UploadCloud className="w-4 h-4" /> Ingest {ingestCount} Readings</>
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
