import { useState } from 'react';
import { 
  MapPin, Phone, Camera, Navigation, AlertTriangle, 
  CheckCircle2, ChevronRight, Save, Navigation2, FileText 
} from 'lucide-react';
import { useToast } from '../context/ToastContext';

export default function FieldApp() {
  const toast = useToast();
  const [selectedTask, setSelectedTask] = useState(null);
  const [loading, setLoading] = useState(false);

  // Form State
  const [status, setStatus] = useState('hooking');
  const [notes, setNotes] = useState('');

  const [tasks] = useState([
    {
      id: 'TKT-9921',
      priority: 'high',
      consumer: 'Rahul Sharma',
      meterId: 'MTR-882-192',
      address: 'Plot 42, Sector 62, Noida',
      phone: '+91 98765 43210',
      reason: 'Consumption Drop (AI Flag)',
      status: 'pending'
    },
    {
      id: 'TKT-9922',
      priority: 'medium',
      consumer: 'Gupta Traders',
      meterId: 'MTR-115-442',
      address: 'Shop 12, Indirapuram Market',
      phone: '+91 99887 76655',
      reason: 'Voltage Anomaly',
      status: 'pending'
    }
  ]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      toast.success('Inspection Report Submitted Successfully!');
      setSelectedTask(null);
    }, 1200);
  };

  const captureGPS = () => {
    toast.info('GPS Location Captured: 28.6200° N, 77.3800° E');
  };

  const capturePhoto = () => {
    toast.info('Camera opened. Photo attached to evidence.');
  };

  if (selectedTask) {
    return (
      <div className="max-w-md mx-auto bg-surface-950 min-h-[80vh] rounded-3xl overflow-hidden border border-white/10 shadow-2xl relative">
        {/* Mobile Header */}
        <div className="bg-brand-600 p-4 pt-6 pb-6 text-white rounded-b-3xl shadow-lg">
          <button 
            onClick={() => setSelectedTask(null)}
            className="text-white/80 hover:text-white flex items-center gap-1 text-sm font-medium mb-4"
          >
            ← Back to Tasks
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xl font-bold">{selectedTask.consumer}</h2>
              <p className="text-brand-200 text-sm font-mono mt-1">{selectedTask.meterId}</p>
            </div>
            <span className="bg-red-500 text-white text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider">
              {selectedTask.priority}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 p-4 -mt-6">
          <button 
            className="flex-1 bg-surface-800 text-white p-3 rounded-xl shadow-lg border border-white/5 flex flex-col items-center gap-2 hover:bg-surface-700 transition"
            onClick={() => window.open(`https://maps.google.com/?q=${selectedTask.address}`)}
          >
            <div className="w-10 h-10 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center">
              <Navigation2 className="w-5 h-5" />
            </div>
            <span className="text-xs font-semibold">Navigate</span>
          </button>
          <button 
            className="flex-1 bg-surface-800 text-white p-3 rounded-xl shadow-lg border border-white/5 flex flex-col items-center gap-2 hover:bg-surface-700 transition"
            onClick={() => window.open(`tel:${selectedTask.phone}`)}
          >
            <div className="w-10 h-10 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center">
              <Phone className="w-5 h-5" />
            </div>
            <span className="text-xs font-semibold">Call User</span>
          </button>
        </div>

        {/* Inspection Form */}
        <div className="p-4 pt-0 space-y-4">
          <div className="bg-white/5 rounded-xl p-4 border border-white/5">
            <h3 className="text-xs font-bold text-white/50 uppercase tracking-wider mb-2">AI Flag Reason</h3>
            <p className="text-sm text-red-400 font-medium flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" /> {selectedTask.reason}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 bg-white/5 p-4 rounded-xl border border-white/5">
            <h3 className="text-sm font-bold text-white mb-2">Submit Inspection</h3>
            
            <div>
              <label className="block text-xs font-semibold text-white/50 mb-1">Found Theft Type</label>
              <select 
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full bg-surface-900 border border-white/10 rounded-lg p-2.5 text-sm text-white"
              >
                <option value="none">No Theft (Clean)</option>
                <option value="hooking">Direct Line Hooking</option>
                <option value="meter_tamper">Meter Hardware Tamper</option>
                <option value="bypass">Meter Bypass</option>
              </select>
            </div>

            <div className="flex gap-2">
              <button 
                type="button" 
                onClick={capturePhoto}
                className="flex-1 bg-surface-900 border border-white/10 rounded-lg p-3 flex flex-col items-center gap-2 hover:bg-surface-800"
              >
                <Camera className="w-5 h-5 text-cyan-400" />
                <span className="text-[10px] text-white/70 font-semibold uppercase">Add Photo</span>
              </button>
              <button 
                type="button"
                onClick={captureGPS}
                className="flex-1 bg-surface-900 border border-white/10 rounded-lg p-3 flex flex-col items-center gap-2 hover:bg-surface-800"
              >
                <MapPin className="w-5 h-5 text-amber-400" />
                <span className="text-[10px] text-white/70 font-semibold uppercase">Tag GPS</span>
              </button>
            </div>

            <div>
              <label className="block text-xs font-semibold text-white/50 mb-1">Inspector Notes</label>
              <textarea 
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Enter details about the inspection..."
                className="w-full bg-surface-900 border border-white/10 rounded-lg p-2.5 text-sm text-white min-h-[80px]"
                required
              />
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-brand-600 hover:bg-brand-500 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 shadow-lg shadow-brand-500/20"
            >
              {loading ? 'Submitting...' : <><Save className="w-4 h-4" /> Submit Report</>}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto bg-surface-950 min-h-[80vh] rounded-3xl overflow-hidden border border-white/10 shadow-2xl relative">
      {/* Mobile Header */}
      <div className="bg-brand-600 p-5 pt-8 rounded-b-3xl shadow-lg relative overflow-hidden">
        <div className="absolute -right-4 -top-4 opacity-10">
          <MapPin className="w-32 h-32" />
        </div>
        <p className="text-brand-200 text-sm font-semibold uppercase tracking-wider mb-1">Field App</p>
        <h1 className="text-2xl font-bold text-white">My Tasks</h1>
        <p className="text-sm text-white/80 mt-1">You have {tasks.length} pending inspections today.</p>
      </div>

      <div className="p-4 space-y-4">
        {/* Task List */}
        {tasks.map(task => (
          <div 
            key={task.id} 
            onClick={() => setSelectedTask(task)}
            className="bg-white/5 rounded-2xl p-4 border border-white/5 active:bg-white/10 cursor-pointer transition-colors"
          >
            <div className="flex justify-between items-start mb-2">
              <span className={`text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider ${
                task.priority === 'high' ? 'bg-red-500/20 text-red-400 border border-red-500/20' : 
                'bg-amber-500/20 text-amber-400 border border-amber-500/20'
              }`}>
                {task.priority} Priority
              </span>
              <span className="text-xs font-mono text-white/40">{task.id}</span>
            </div>
            
            <h3 className="text-lg font-bold text-white mb-1">{task.consumer}</h3>
            
            <div className="space-y-1.5 mb-4">
              <p className="text-xs text-white/60 flex items-center gap-2">
                <MapPin className="w-3.5 h-3.5" /> {task.address}
              </p>
              <p className="text-xs text-white/60 flex items-center gap-2">
                <AlertTriangle className="w-3.5 h-3.5 text-red-400" /> {task.reason}
              </p>
            </div>
            
            <div className="flex items-center justify-between pt-3 border-t border-white/5">
              <span className="text-xs text-brand-400 font-semibold flex items-center gap-1">
                Start Inspection <ChevronRight className="w-3 h-3" />
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
