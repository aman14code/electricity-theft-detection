import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Zap, AlertTriangle, ShieldAlert, CheckCircle2, 
  MapPin, Activity, ChevronRight, UserPlus, FileText
} from 'lucide-react';
import { useToast } from '../context/ToastContext';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

export default function DTRMonitoring() {
  const toast = useToast();
  const [loading, setLoading] = useState(true);

  // Mock DTR data for the MVP view since we don't have DTRs in the DB yet
  const [dtrs, setDtrs] = useState([
    {
      id: 'DTR-Noida-62-A',
      location: 'Sector 62, Main Feeder',
      capacity: 500,
      meters: 142,
      transformerOutput: 45000,
      sumOfMeters: 38200,
      technicalLoss: 1350,
      status: 'warning'
    },
    {
      id: 'DTR-Vaishali-4-B',
      location: 'Vaishali Sector 4',
      capacity: 250,
      meters: 85,
      transformerOutput: 21000,
      sumOfMeters: 16500,
      technicalLoss: 630,
      status: 'alert'
    },
    {
      id: 'DTR-Indirapuram-1-C',
      location: 'Indirapuram Hub 1',
      capacity: 1000,
      meters: 310,
      transformerOutput: 92000,
      sumOfMeters: 89000,
      technicalLoss: 2760,
      status: 'normal'
    }
  ]);

  useEffect(() => {
    // Simulate API fetch delay
    const timer = setTimeout(() => {
      // Calculate unaccounted loss dynamically
      const processed = dtrs.map(dtr => {
        const unaccountedLoss = dtr.transformerOutput - dtr.sumOfMeters - dtr.technicalLoss;
        const lossPercentage = (unaccountedLoss / dtr.transformerOutput) * 100;
        
        let status = 'normal';
        if (lossPercentage > 15) status = 'alert';
        else if (lossPercentage > 8) status = 'warning';

        return {
          ...dtr,
          unaccountedLoss,
          lossPercentage,
          status
        };
      });
      setDtrs(processed);
      setLoading(false);
    }, 800);

    return () => clearTimeout(timer);
  }, []);

  const handleDispatch = (dtrId) => {
    toast.success(`Line Patrol dispatched to ${dtrId} successfully.`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-white/40">Loading Transformer Data…</p>
        </div>
      </div>
    );
  }

  // Aggregate data for the Chart
  const chartData = dtrs.map(dtr => ({
    name: dtr.id.split('-').slice(1).join('-'), // Shorten name
    'Meter Consumption': dtr.sumOfMeters,
    'Technical Loss (Heat/Line)': dtr.technicalLoss,
    'Unaccounted Loss (Theft)': dtr.unaccountedLoss > 0 ? dtr.unaccountedLoss : 0
  }));

  return (
    <div className="space-y-6">
      {/* ─── Header ──────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Zap className="text-yellow-400" /> DTR Energy Balance
          </h1>
          <p className="text-sm text-white/40 mt-1">
            Distribution Transformer Monitoring & Macro-level Theft Detection
          </p>
        </div>
        <button className="btn-ghost flex items-center gap-2 text-xs">
          <FileText className="w-4 h-4" /> Export DTR Audit
        </button>
      </div>

      {/* ─── Macro Energy Chart ────────────────────────── */}
      <div className="glass-card p-6">
        <h3 className="text-sm font-semibold text-white/90 mb-6 flex items-center gap-2">
          <Activity className="w-4 h-4 text-brand-400" />
          Energy Balance Overview (kWh)
        </h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
              <XAxis dataKey="name" stroke="#ffffff40" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="#ffffff40" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#ffffff20', borderRadius: '8px', color: '#fff' }}
                cursor={{ fill: '#ffffff05' }}
              />
              <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px', color: '#ffffff80' }}/>
              <Bar dataKey="Meter Consumption" stackId="a" fill="#10b981" />
              <Bar dataKey="Technical Loss (Heat/Line)" stackId="a" fill="#f59e0b" />
              <Bar dataKey="Unaccounted Loss (Theft)" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ─── DTR List ───────────────────────────────────── */}
      <div className="space-y-4">
        <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wider">
          Transformer Audits
        </h3>
        
        <div className="grid gap-4">
          {dtrs.map(dtr => (
            <div key={dtr.id} className={`glass-card p-5 border-l-4 ${
              dtr.status === 'alert' ? 'border-l-red-500' : 
              dtr.status === 'warning' ? 'border-l-amber-500' : 
              'border-l-green-500'
            }`}>
              <div className="flex flex-col lg:flex-row gap-6 justify-between items-start lg:items-center">
                
                {/* Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h2 className="text-lg font-bold text-white">{dtr.id}</h2>
                    {dtr.status === 'alert' && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-red-500/10 text-red-400 border border-red-500/20 flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> High Loss Detected
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-xs text-white/40">
                    <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {dtr.location}</span>
                    <span className="flex items-center gap-1"><Zap className="w-3 h-3" /> {dtr.capacity} kVA</span>
                    <span className="flex items-center gap-1 text-brand-400 font-semibold">{dtr.meters} Downstream Meters</span>
                  </div>
                </div>

                {/* Energy Balance Stats */}
                <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4 bg-black/20 p-3 rounded-xl border border-white/5">
                  <div>
                    <p className="text-[10px] text-white/40 uppercase tracking-wider font-semibold">Total Output</p>
                    <p className="text-sm font-mono text-cyan-400">{dtr.transformerOutput.toLocaleString()} <span className="text-[10px]">kWh</span></p>
                  </div>
                  <div>
                    <p className="text-[10px] text-white/40 uppercase tracking-wider font-semibold">Metered Sum</p>
                    <p className="text-sm font-mono text-green-400">{dtr.sumOfMeters.toLocaleString()} <span className="text-[10px]">kWh</span></p>
                  </div>
                  <div>
                    <p className="text-[10px] text-white/40 uppercase tracking-wider font-semibold">Tech Loss (3%)</p>
                    <p className="text-sm font-mono text-amber-400">{dtr.technicalLoss.toLocaleString()} <span className="text-[10px]">kWh</span></p>
                  </div>
                  <div className={`${dtr.status === 'alert' ? 'bg-red-500/10 rounded px-2 -mx-2 -my-1 py-1 border border-red-500/20' : ''}`}>
                    <p className="text-[10px] text-white/40 uppercase tracking-wider font-semibold">Unaccounted</p>
                    <p className={`text-sm font-mono font-bold ${dtr.status === 'alert' ? 'text-red-400' : 'text-white/80'}`}>
                      {dtr.unaccountedLoss.toLocaleString()} <span className="text-[10px]">kWh</span>
                      <span className="ml-1 text-[10px]">({dtr.lossPercentage.toFixed(1)}%)</span>
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="shrink-0">
                  {dtr.status === 'alert' ? (
                    <button 
                      onClick={() => handleDispatch(dtr.id)}
                      className="btn-primary bg-red-600 hover:bg-red-500 flex items-center gap-2 text-xs py-2 shadow-lg shadow-red-500/20"
                    >
                      <ShieldAlert className="w-4 h-4" /> Dispatch Patrol
                    </button>
                  ) : (
                    <button className="btn-ghost flex items-center gap-2 text-xs py-2">
                      <CheckCircle2 className="w-4 h-4 text-green-400" /> Status Normal
                    </button>
                  )}
                </div>
                
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
