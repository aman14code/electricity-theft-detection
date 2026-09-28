import { useState } from 'react';
import { 
  Bell, Mail, MessageSquare, CheckCircle2, AlertTriangle, ShieldAlert 
} from 'lucide-react';

export default function Notifications() {
  const [logs] = useState([
    {
      id: 1,
      type: 'whatsapp',
      recipient: 'Inspector Ramesh (+91 9876543210)',
      subject: 'DISPATCH: High-Risk Inspection (Sector 62)',
      content: 'TKT-9921 assigned. AI Flag: Consumption Drop. PDF Evidence Attached.',
      time: '10 mins ago',
      status: 'delivered'
    },
    {
      id: 2,
      type: 'email',
      recipient: 'billing@guptatraders.in',
      subject: 'PowerGuard: Abnormal Usage Warning',
      content: 'Dear Consumer, we noticed an anomaly in your recent power usage... Please contact support.',
      time: '2 hours ago',
      status: 'sent'
    },
    {
      id: 3,
      type: 'whatsapp',
      recipient: 'QRT Team Lead',
      subject: 'DTR ALERT: Vaishali Sector 4',
      content: 'Transformer Unaccounted Loss > 15%. Dispatching Line Patrol immediately.',
      time: '5 hours ago',
      status: 'delivered'
    },
    {
      id: 4,
      type: 'sms',
      recipient: 'Rakesh Verma (+91 9123456789)',
      subject: 'Inspection Notice',
      content: 'An engineer will visit your premises tomorrow for a routine meter audit.',
      time: '1 day ago',
      status: 'failed'
    }
  ]);

  return (
    <div className="space-y-6">
      {/* ─── Header ──────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Bell className="text-brand-400" /> Dispatch & Notifications Log
          </h1>
          <p className="text-sm text-white/40 mt-1">
            System log for automated SMS, WhatsApp, and Email alerts.
          </p>
        </div>
      </div>

      {/* ─── Log List ───────────────────────────────────── */}
      <div className="glass-card overflow-hidden">
        <div className="divide-y divide-white/[0.04]">
          {logs.map((log) => (
            <div key={log.id} className="p-6 hover:bg-white/[0.02] transition-colors">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                
                {/* Icon & Details */}
                <div className="flex gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 border ${
                    log.type === 'whatsapp' ? 'bg-green-500/20 text-green-400 border-green-500/20' :
                    log.type === 'email' ? 'bg-blue-500/20 text-blue-400 border-blue-500/20' :
                    'bg-amber-500/20 text-amber-400 border-amber-500/20'
                  }`}>
                    {log.type === 'whatsapp' ? <MessageSquare className="w-5 h-5" /> : 
                     log.type === 'email' ? <Mail className="w-5 h-5" /> : 
                     <MessageSquare className="w-5 h-5" />}
                  </div>
                  
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-white/40 border border-white/10 px-1.5 py-0.5 rounded">
                        {log.type}
                      </span>
                      <span className="text-xs text-white/40 font-medium">{log.time}</span>
                    </div>
                    <h3 className="text-sm font-bold text-white mb-0.5">{log.subject}</h3>
                    <p className="text-xs text-white/50 mb-2">To: <span className="text-brand-400 font-mono">{log.recipient}</span></p>
                    <p className="text-sm text-white/70 bg-black/20 p-3 rounded-lg border border-white/5">
                      {log.content}
                    </p>
                  </div>
                </div>

                {/* Status */}
                <div className="shrink-0 flex items-center gap-1.5 text-xs font-semibold">
                  {log.status === 'delivered' || log.status === 'sent' ? (
                    <span className="text-green-400 flex items-center gap-1.5 px-3 py-1.5 bg-green-500/10 rounded-full border border-green-500/20">
                      <CheckCircle2 className="w-4 h-4" /> {log.status.toUpperCase()}
                    </span>
                  ) : (
                    <span className="text-red-400 flex items-center gap-1.5 px-3 py-1.5 bg-red-500/10 rounded-full border border-red-500/20">
                      <AlertTriangle className="w-4 h-4" /> {log.status.toUpperCase()}
                    </span>
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
