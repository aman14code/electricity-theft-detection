import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import { useToast } from '../context/ToastContext';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import {
  BarChart2, Download, FileText, FileSpreadsheet, Calendar, Filter, 
  MapPin, AlertTriangle, ShieldAlert, CheckCircle2, ChevronRight
} from 'lucide-react';

export default function Reports() {
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [alerts, setAlerts] = useState([]);
  
  // Custom Report Generator State
  const [reportType, setReportType] = useState('theft_incidents');
  const [dateRange, setDateRange] = useState('last_30_days');
  const [areaFilter, setAreaFilter] = useState('all');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const alertsRes = await api.get('/alerts');
        setAlerts(alertsRes.data.data);
      } catch {
        toast.error('Failed to load report data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleExport = (format) => {
    setGenerating(true);
    toast.info(`Generating ${format.toUpperCase()} report...`);
    
    // Simulate generation delay
    setTimeout(() => {
      setGenerating(false);
      toast.success(`${format.toUpperCase()} Report downloaded successfully!`);
    }, 1500);
  };

  // Mock data for the report preview chart
  const trendData = [
    { name: 'Week 1', cases: 12, recovered: 45000 },
    { name: 'Week 2', cases: 19, recovered: 82000 },
    { name: 'Week 3', cases: 15, recovered: 55000 },
    { name: 'Week 4', cases: 22, recovered: 91000 },
  ];

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
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <BarChart2 className="text-brand-400" /> Analytics & Custom Reports
        </h1>
        <p className="text-sm text-white/40 mt-1">
          Generate comprehensive audit reports for DISCOM management
        </p>
      </div>

      {/* ─── Custom Report Generator ──────────────────────── */}
      <div className="glass-card p-6 border-l-4 border-l-brand-500">
        <h3 className="text-sm font-bold text-white mb-4 uppercase tracking-wider">Report Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Report Type */}
          <div>
            <label className="block text-xs font-semibold text-white/50 mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4" /> Report Type
            </label>
            <select 
              value={reportType} 
              onChange={(e) => setReportType(e.target.value)}
              className="input-field w-full py-2.5 text-sm"
            >
              <option value="theft_incidents">High-Risk Theft Incidents</option>
              <option value="revenue_recovery">Estimated Revenue Recovery</option>
              <option value="dtr_audit">Transformer (DTR) Energy Audit</option>
              <option value="officer_performance">Field Officer Performance</option>
            </select>
          </div>

          {/* Date Range */}
          <div>
            <label className="block text-xs font-semibold text-white/50 mb-2 flex items-center gap-2">
              <Calendar className="w-4 h-4" /> Date Range
            </label>
            <select 
              value={dateRange} 
              onChange={(e) => setDateRange(e.target.value)}
              className="input-field w-full py-2.5 text-sm"
            >
              <option value="last_7_days">Last 7 Days</option>
              <option value="last_30_days">Last 30 Days</option>
              <option value="this_quarter">This Quarter</option>
              <option value="ytd">Year to Date (YTD)</option>
              <option value="custom">Custom Range...</option>
            </select>
          </div>

          {/* Area Filter */}
          <div>
            <label className="block text-xs font-semibold text-white/50 mb-2 flex items-center gap-2">
              <Filter className="w-4 h-4" /> Area / Substation
            </label>
            <select 
              value={areaFilter} 
              onChange={(e) => setAreaFilter(e.target.value)}
              className="input-field w-full py-2.5 text-sm"
            >
              <option value="all">All Areas (Global)</option>
              <option value="sector62">Sector 62</option>
              <option value="indirapuram">Indirapuram</option>
              <option value="vaishali">Vaishali</option>
            </select>
          </div>
        </div>

        {/* Export Actions */}
        <div className="flex flex-wrap gap-3 pt-4 border-t border-white/10">
          <button 
            onClick={() => handleExport('pdf')}
            disabled={generating}
            className="btn-primary bg-red-600 hover:bg-red-500 shadow-lg shadow-red-500/20 flex items-center gap-2"
          >
            <FileText className="w-4 h-4" /> Export as PDF
          </button>
          <button 
            onClick={() => handleExport('excel')}
            disabled={generating}
            className="btn-primary bg-green-600 hover:bg-green-500 shadow-lg shadow-green-500/20 flex items-center gap-2"
          >
            <FileSpreadsheet className="w-4 h-4" /> Export as Excel
          </button>
          <button 
            onClick={() => handleExport('csv')}
            disabled={generating}
            className="btn-ghost flex items-center gap-2"
          >
            <Download className="w-4 h-4" /> Raw CSV
          </button>
        </div>
      </div>

      {/* ─── Report Preview ────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Chart Preview */}
        <div className="lg:col-span-2 glass-card p-6">
          <h3 className="text-sm font-semibold text-white/90 mb-6">Preview: 30-Day Trend</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="name" stroke="#ffffff40" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis yAxisId="left" stroke="#ffffff40" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis yAxisId="right" orientation="right" stroke="#10b981" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${v/1000}k`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#ffffff20', borderRadius: '8px', color: '#fff' }}
                  cursor={{ fill: '#ffffff05' }}
                />
                <Bar yAxisId="left" dataKey="cases" name="Theft Cases" fill="#ef4444" radius={[4, 4, 0, 0]} />
                <Bar yAxisId="right" dataKey="recovered" name="Est. Recovery (₹)" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Snapshot Summary */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold text-white/90 mb-4">Report Snapshot</h3>
          <div className="space-y-4">
            <div className="bg-white/5 p-4 rounded-xl border border-white/10">
              <p className="text-xs text-white/50 uppercase tracking-wider font-semibold">Total Cases</p>
              <p className="text-2xl font-bold text-red-400 font-mono mt-1">68</p>
            </div>
            <div className="bg-white/5 p-4 rounded-xl border border-white/10">
              <p className="text-xs text-white/50 uppercase tracking-wider font-semibold">Est. Recovery</p>
              <p className="text-2xl font-bold text-green-400 font-mono mt-1">₹2,73,000</p>
            </div>
            <div className="bg-white/5 p-4 rounded-xl border border-white/10">
              <p className="text-xs text-white/50 uppercase tracking-wider font-semibold">Highest Risk Area</p>
              <p className="text-lg font-bold text-orange-400 flex items-center gap-2 mt-1">
                <MapPin className="w-4 h-4" /> Sector 62
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
