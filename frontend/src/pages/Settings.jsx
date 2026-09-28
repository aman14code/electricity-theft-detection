import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import {
  Settings as SettingsIcon,
  User,
  Bell,
  Shield,
  Database,
  Brain,
  Save,
  Moon,
  Sun,
  Smartphone
} from 'lucide-react';

export default function Settings() {
  const { user } = useAuth();
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

  // Form states
  const [profile, setProfile] = useState({
    name: user?.name || 'Admin User',
    email: user?.email || 'admin@powerguard.in',
    phone: '+91 9876543210'
  });

  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    smsAlerts: true,
    whatsappAlerts: true,
    dailyReport: false,
    highRiskOnly: false
  });

  const [system, setSystem] = useState({
    dtrWarningThreshold: 8,
    dtrCriticalThreshold: 15,
    autoDispatchHighRisk: false,
    activeModel: 'ensemble_soft_voting',
    dataRetentionDays: 365
  });

  const handleSave = (e) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      toast.success('Settings saved successfully!');
    }, 1000);
  };

  const tabs = [
    { id: 'profile', label: 'My Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'system', label: 'System & ML', icon: Brain },
    { id: 'security', label: 'Security', icon: Shield },
  ];

  return (
    <div className="space-y-6">
      {/* ─── Header ──────────────────────────────────────── */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <SettingsIcon className="text-brand-400" /> Platform Settings
        </h1>
        <p className="text-sm text-white/40 mt-1">
          Manage your account, notification preferences, and system thresholds.
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* ─── Sidebar Tabs ──────────────────────────────── */}
        <div className="lg:w-64 shrink-0">
          <div className="glass-card overflow-hidden">
            <div className="flex flex-col">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-3 px-4 py-3 text-sm font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-brand-500/10 text-brand-400 border-l-2 border-brand-500'
                      : 'text-white/50 hover:bg-white/[0.02] hover:text-white/80 border-l-2 border-transparent'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* ─── Tab Content ───────────────────────────────── */}
        <div className="flex-1 glass-card p-6">
          <form onSubmit={handleSave}>
            
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="space-y-6 animate-fade-in">
                <h3 className="text-lg font-bold text-white mb-4">Profile Information</h3>
                
                <div className="flex items-center gap-6 mb-6">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-brand-500 to-electric-purple flex items-center justify-center text-2xl font-bold text-white border-2 border-brand-500/30">
                    {profile.name.charAt(0)}
                  </div>
                  <button type="button" className="btn-ghost text-xs">Change Avatar</button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">Full Name</label>
                    <input 
                      type="text" 
                      value={profile.name}
                      onChange={e => setProfile({...profile, name: e.target.value})}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">Email Address</label>
                    <input 
                      type="email" 
                      value={profile.email}
                      onChange={e => setProfile({...profile, email: e.target.value})}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">Phone Number</label>
                    <input 
                      type="tel" 
                      value={profile.phone}
                      onChange={e => setProfile({...profile, phone: e.target.value})}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">Role</label>
                    <input 
                      type="text" 
                      value="System Administrator"
                      disabled
                      className="input-field opacity-50 cursor-not-allowed"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="space-y-6 animate-fade-in">
                <h3 className="text-lg font-bold text-white mb-4">Notification Preferences</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
                    <div>
                      <h4 className="text-sm font-semibold text-white">Email Alerts</h4>
                      <p className="text-xs text-white/40 mt-1">Receive daily summaries and critical alerts via email.</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" checked={notifications.emailAlerts} onChange={e => setNotifications({...notifications, emailAlerts: e.target.checked})} className="sr-only peer" />
                      <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-500"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
                    <div>
                      <h4 className="text-sm font-semibold text-white">WhatsApp / SMS Dispatch</h4>
                      <p className="text-xs text-white/40 mt-1">Automatically notify field officers via WhatsApp when a ticket is created.</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" checked={notifications.whatsappAlerts} onChange={e => setNotifications({...notifications, whatsappAlerts: e.target.checked})} className="sr-only peer" />
                      <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-500"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
                    <div>
                      <h4 className="text-sm font-semibold text-white">High Risk Only</h4>
                      <p className="text-xs text-white/40 mt-1">Only notify me for Critical/High risk alerts (>50% probability).</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" checked={notifications.highRiskOnly} onChange={e => setNotifications({...notifications, highRiskOnly: e.target.checked})} className="sr-only peer" />
                      <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-500"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* System Tab */}
            {activeTab === 'system' && (
              <div className="space-y-6 animate-fade-in">
                <h3 className="text-lg font-bold text-white mb-4">System & Machine Learning</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">Active ML Model</label>
                    <select 
                      value={system.activeModel}
                      onChange={e => setSystem({...system, activeModel: e.target.value})}
                      className="input-field"
                    >
                      <option value="ensemble_soft_voting">Ensemble (Soft Voting) - Recommended</option>
                      <option value="random_forest">Random Forest</option>
                      <option value="xgboost">XGBoost</option>
                      <option value="dnn">Deep Neural Network (DNN)</option>
                    </select>
                    <p className="text-[10px] text-white/30 mt-1">The active model used for live inference.</p>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">Data Retention (Days)</label>
                    <input 
                      type="number" 
                      value={system.dataRetentionDays}
                      onChange={e => setSystem({...system, dataRetentionDays: e.target.value})}
                      className="input-field"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-amber-400/80 mb-2 uppercase tracking-wider">DTR Warning Threshold (%)</label>
                    <input 
                      type="number" 
                      value={system.dtrWarningThreshold}
                      onChange={e => setSystem({...system, dtrWarningThreshold: e.target.value})}
                      className="input-field border-amber-500/30 focus:border-amber-400"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-red-400/80 mb-2 uppercase tracking-wider">DTR Critical Threshold (%)</label>
                    <input 
                      type="number" 
                      value={system.dtrCriticalThreshold}
                      onChange={e => setSystem({...system, dtrCriticalThreshold: e.target.value})}
                      className="input-field border-red-500/30 focus:border-red-400"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <div className="space-y-6 animate-fade-in">
                <h3 className="text-lg font-bold text-white mb-4">Security</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">Current Password</label>
                    <input type="password" placeholder="••••••••" className="input-field max-w-md" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-white/50 mb-2 uppercase tracking-wider">New Password</label>
                    <input type="password" placeholder="••••••••" className="input-field max-w-md" />
                  </div>
                  <button type="button" className="btn-ghost border border-white/10 mt-2">Update Password</button>
                </div>

                <div className="pt-6 mt-6 border-t border-white/5">
                  <h4 className="text-sm font-semibold text-red-400 mb-2">Danger Zone</h4>
                  <p className="text-xs text-white/40 mb-4">Permanently delete all simulated data from the database.</p>
                  <button type="button" className="btn-ghost text-red-400 border border-red-500/20 hover:bg-red-500/10">Factory Reset Database</button>
                </div>
              </div>
            )}

            {/* Save Button */}
            <div className="mt-8 pt-6 border-t border-white/10 flex justify-end">
              <button 
                type="submit" 
                disabled={loading}
                className="btn-primary flex items-center gap-2"
              >
                {loading ? 'Saving...' : <><Save className="w-4 h-4" /> Save Changes</>}
              </button>
            </div>

          </form>
        </div>
      </div>
    </div>
  );
}
