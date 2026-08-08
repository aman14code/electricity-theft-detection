import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import { useToast } from '../context/ToastContext';
import {
  Gauge, Plus, MapPin, Home, Building2, Zap,
  Search, ChevronRight, X
} from 'lucide-react';

export default function Meters() {
  const toast = useToast();
  const [meters, setMeters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    location: '',
    consumerType: 'residential',
    baselineConsumption: '',
  });
  const [creating, setCreating] = useState(false);

  const fetchMeters = async () => {
    try {
      const { data } = await api.get('/meters');
      setMeters(data.data);
    } catch (err) {
      console.error('Fetch meters error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMeters();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      await api.post('/meters', {
        ...form,
        baselineConsumption: parseFloat(form.baselineConsumption),
      });
      setShowCreate(false);
      setForm({ location: '', consumerType: 'residential', baselineConsumption: '' });
      toast.success('Meter created successfully');
      fetchMeters();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to create meter');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this meter?')) return;
    try {
      await api.delete(`/meters/${id}`);
      toast.success('Meter deleted');
      fetchMeters();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to delete meter');
    }
  };

  const filtered = meters.filter((m) =>
    m.location.toLowerCase().includes(search.toLowerCase())
  );

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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Smart Meters</h1>
          <p className="text-sm text-white/40 mt-1">{meters.length} meters registered</p>
        </div>
        <button
          id="create-meter-btn"
          onClick={() => setShowCreate(true)}
          className="btn-primary flex items-center gap-2 w-fit"
        >
          <Plus className="w-4 h-4" />
          Add Meter
        </button>
      </div>

      {/* ─── Search ──────────────────────────────────────── */}
      <div className="relative max-w-md">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/25" />
        <input
          id="meter-search"
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by location…"
          className="input-field pl-11"
        />
      </div>

      {/* ─── Meter grid ──────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filtered.map((meter, i) => (
          <Link
            key={meter._id}
            to={`/meters/${meter._id}`}
            className="glass-card-hover p-5 group block"
            style={{ animationDelay: `${i * 50}ms` }}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br
                              from-brand-500/20 to-brand-600/10
                              flex items-center justify-center border border-brand-500/20">
                {meter.consumerType === 'commercial' ? (
                  <Building2 className="w-5 h-5 text-brand-400" />
                ) : (
                  <Home className="w-5 h-5 text-brand-400" />
                )}
              </div>
              <ChevronRight className="w-4 h-4 text-white/20 group-hover:text-white/50
                                       group-hover:translate-x-1 transition-all duration-200" />
            </div>

            <h3 className="text-sm font-semibold text-white/90 mb-1 truncate">
              {meter.location}
            </h3>

            <div className="flex items-center gap-4 text-xs text-white/40 mt-3">
              <div className="flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                <span className="capitalize">{meter.consumerType}</span>
              </div>
              <div className="flex items-center gap-1">
                <Zap className="w-3 h-3" />
                <span>{meter.baselineConsumption} kWh/hr</span>
              </div>
            </div>

            <div className="mt-3 flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${meter.isActive ? 'bg-green-400 animate-pulse' : 'bg-white/20'}`} />
              <span className={`text-xs font-medium ${meter.isActive ? 'text-green-400' : 'text-white/30'}`}>
                {meter.isActive ? 'Active' : 'Inactive'}
              </span>
            </div>
          </Link>
        ))}

        {filtered.length === 0 && (
          <div className="col-span-full text-center py-16">
            <Gauge className="w-12 h-12 text-white/10 mx-auto mb-4" />
            <p className="text-white/40">No meters found</p>
          </div>
        )}
      </div>

      {/* ─── Create modal ────────────────────────────────── */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
             onClick={() => setShowCreate(false)}>
          <div className="glass-card p-8 w-full max-w-md animate-slide-up gradient-border"
               onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold text-white">Add New Meter</h2>
              <button onClick={() => setShowCreate(false)}
                      className="text-white/30 hover:text-white/60 transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">
                  Location
                </label>
                <input
                  id="meter-location"
                  type="text"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  placeholder="Block A — Building 1"
                  className="input-field"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">
                  Consumer Type
                </label>
                <select
                  id="meter-type"
                  value={form.consumerType}
                  onChange={(e) => setForm({ ...form, consumerType: e.target.value })}
                  className="input-field"
                >
                  <option value="residential">Residential</option>
                  <option value="commercial">Commercial</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">
                  Baseline Consumption (kWh/hr)
                </label>
                <input
                  id="meter-baseline"
                  type="number"
                  step="0.1"
                  value={form.baselineConsumption}
                  onChange={(e) => setForm({ ...form, baselineConsumption: e.target.value })}
                  placeholder="3.5"
                  className="input-field"
                  required
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowCreate(false)} className="btn-ghost flex-1">
                  Cancel
                </button>
                <button type="submit" disabled={creating} className="btn-primary flex-1">
                  {creating ? 'Creating…' : 'Create Meter'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
