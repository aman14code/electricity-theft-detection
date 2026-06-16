import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, BarChart, Bar,
} from 'recharts';
import {
  ArrowLeft, MapPin, Zap, ScanSearch, Loader2,
  ShieldAlert, CheckCircle2, AlertTriangle, Home, Building2,
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
  const [meter, setMeter] = useState(null);
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [days, setDays] = useState(7);

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
    } catch (err) {
      setAnalysisResult({
        success: false,
        message: err.response?.data?.message || 'Analysis failed',
      });
    } finally {
      setAnalyzing(false);
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

        <button
          id="analyze-btn"
          onClick={handleAnalyze}
          disabled={analyzing}
          className="btn-primary flex items-center gap-2 w-fit"
        >
          {analyzing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" /> Analyzing…
            </>
          ) : (
            <>
              <ScanSearch className="w-4 h-4" /> Analyze Anomalies
            </>
          )}
        </button>
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
    </div>
  );
}
