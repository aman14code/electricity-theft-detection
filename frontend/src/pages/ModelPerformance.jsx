import { useState, useEffect } from 'react';
import api from '../api/axios';
import { useToast } from '../context/ToastContext';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, RadarChart, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, Radar, Legend,
  PieChart, Pie,
} from 'recharts';
import {
  Brain, TrendingUp, Target, Award, Database,
  Layers, Activity, Info, ChevronDown, ChevronUp,
} from 'lucide-react';

// ─── Color palette ───────────────────────────────────────
const MODEL_COLORS = {
  'Random Forest': '#3b82f6',
  'XGBoost': '#f59e0b',
  'DNN': '#8b5cf6',
  'Isolation Forest': '#10b981',
  'LSTM': '#ec4899',
  'Soft Voting Ensemble': '#06b6d4',
};

const getModelColor = (name) => MODEL_COLORS[name] || '#94a3b8';

// ─── Custom Tooltip ──────────────────────────────────────
const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card px-4 py-3 !border-brand-500/20 !shadow-xl">
      <p className="text-xs font-semibold text-white/60 mb-2">{label}</p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          <span className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
          <span className="text-white/50">{entry.name}:</span>
          <span className="font-semibold text-white font-mono">
            {typeof entry.value === 'number'
              ? entry.value >= 1 ? entry.value : (entry.value * 100).toFixed(1) + '%'
              : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function ModelPerformance() {
  const toast = useToast();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedModel, setExpandedModel] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const { data } = await api.get('/dashboard/ml-metrics');
        if (data.success && data.data) {
          setMetrics(data.data);
        } else {
          toast.info('No model metrics available yet. Train the model first.');
        }
      } catch {
        toast.error('Failed to load model metrics');
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-white/40">Loading model metrics…</p>
        </div>
      </div>
    );
  }

  if (!metrics || !metrics.individual_models) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <Brain className="w-16 h-16 text-white/10" />
        <h2 className="text-xl font-semibold text-white/40">No Model Metrics Available</h2>
        <p className="text-sm text-white/25 max-w-md text-center">
          Train the ML models first using <code className="text-brand-400">python train_model.py</code> to generate
          evaluation results and performance metrics.
        </p>
      </div>
    );
  }

  const models = metrics.individual_models;
  const ensemble = models.find(m => m.model.includes('Ensemble'));
  const individualModels = models.filter(m => !m.model.includes('Ensemble'));
  const featureNames = metrics.feature_names || [];
  const datasetInfo = metrics.dataset_info || {};
  const shapImportance = metrics.shap_importance || {};

  // ── Prepare chart data ──────────────────────────────────
  const comparisonData = models.map(m => ({
    name: m.model.replace('Soft Voting ', ''),
    Accuracy: m.accuracy,
    Precision: m.precision,
    Recall: m.recall,
    'F1 Score': m.f1_score,
    'AUC-ROC': m.auc_roc,
    fill: getModelColor(m.model),
  }));

  const radarData = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC-ROC', 'PR-AUC'].map(metric => {
    const entry = { metric };
    models.forEach(m => {
      const key = metric.toLowerCase().replace(/[ -]/g, '_');
      entry[m.model.replace('Soft Voting ', '')] = m[key] || 0;
    });
    return entry;
  });

  const aucData = models.map(m => ({
    name: m.model.replace('Soft Voting ', ''),
    'AUC-ROC': m.auc_roc,
    'PR-AUC': m.pr_auc,
    fill: getModelColor(m.model),
  }));

  // SHAP feature importance data
  const shapData = Object.entries(shapImportance)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 15)
    .map(([name, value]) => ({
      name: name.replace(/_/g, ' '),
      importance: value,
    }));

  return (
    <div className="space-y-8">
      {/* ─── Header ──────────────────────────────────────── */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <Brain className="w-7 h-7 text-brand-400" />
          Model Performance
        </h1>
        <p className="text-sm text-white/40 mt-1">
          Comprehensive evaluation of the 5-model ensemble per the research paper methodology
        </p>
      </div>

      {/* ─── Dataset & Training Info ─────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {[
          {
            label: 'Consumers', value: datasetInfo.n_consumers?.toLocaleString() || '—',
            icon: Database, desc: 'SGCC dataset', gradient: 'from-brand-500/20 to-brand-600/10',
            border: 'border-brand-500/20', iconColor: 'text-brand-400',
          },
          {
            label: 'Features', value: datasetInfo.n_features || featureNames.length || '—',
            icon: Layers, desc: 'Engineered features', gradient: 'from-purple-500/20 to-purple-600/10',
            border: 'border-purple-500/20', iconColor: 'text-purple-400',
          },
          {
            label: 'Theft Rate', value: `${((datasetInfo.theft_rate || 0) * 100).toFixed(1)}%`,
            icon: Target, desc: 'Class imbalance', gradient: 'from-amber-500/20 to-amber-600/10',
            border: 'border-amber-500/20', iconColor: 'text-amber-400',
          },
          {
            label: 'Best AUC-ROC',
            value: ensemble ? (ensemble.auc_roc * 100).toFixed(1) + '%' : '—',
            icon: Award, desc: 'Ensemble performance', gradient: 'from-green-500/20 to-green-600/10',
            border: 'border-green-500/20', iconColor: 'text-green-400',
          },
        ].map(card => (
          <div key={card.label} className="glass-card p-5 animate-fade-in">
            <div className="flex items-start justify-between mb-4">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${card.gradient} flex items-center justify-center border ${card.border}`}>
                <card.icon className={`w-5 h-5 ${card.iconColor}`} />
              </div>
            </div>
            <p className="text-3xl font-bold text-white font-mono">{card.value}</p>
            <p className="text-xs text-white/40 mt-1">{card.label}</p>
            <p className="text-[10px] text-white/25 mt-0.5">{card.desc}</p>
          </div>
        ))}
      </div>

      {/* ─── Model Comparison Bar Chart ───────────────────── */}
      <div className="glass-card p-6 animate-slide-up">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500/20 to-electric-purple/20
                          flex items-center justify-center border border-brand-500/20">
            <TrendingUp className="w-5 h-5 text-brand-400" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Model Performance Comparison</h3>
            <p className="text-xs text-white/40">
              AUC-ROC scores across all {models.length} models (higher is better)
            </p>
          </div>
        </div>

        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={aucData} margin={{ top: 5, right: 10, left: 0, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
            <XAxis
              dataKey="name"
              tick={{ fill: 'rgba(255,255,255,0.45)', fontSize: 11 }}
              axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
              tickLine={false}
              angle={-20}
              textAnchor="end"
              interval={0}
            />
            <YAxis
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              domain={[0, 1.05]}
            />
            <Tooltip content={<ChartTooltip />} />
            <Legend wrapperStyle={{ paddingTop: 16, fontSize: 12 }} iconType="circle" iconSize={8} />
            <Bar dataKey="AUC-ROC" radius={[6, 6, 0, 0]}>
              {aucData.map((entry, i) => (
                <Cell key={i} fill={entry.fill} opacity={0.85} />
              ))}
            </Bar>
            <Bar dataKey="PR-AUC" radius={[6, 6, 0, 0]} opacity={0.5}>
              {aucData.map((entry, i) => (
                <Cell key={i} fill={entry.fill} opacity={0.45} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ─── Radar Chart ─────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="glass-card p-6 animate-slide-up">
          <h3 className="text-sm font-semibold text-white mb-1">Multi-Metric Radar</h3>
          <p className="text-xs text-white/40 mb-4">
            Comparing all evaluation metrics across models
          </p>
          <ResponsiveContainer width="100%" height={320}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.08)" />
              <PolarAngleAxis
                dataKey="metric"
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }}
              />
              <PolarRadiusAxis
                tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 9 }}
                domain={[0, 1]}
                tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              />
              {individualModels.slice(0, 3).map((m) => (
                <Radar
                  key={m.model}
                  name={m.model}
                  dataKey={m.model.replace('Soft Voting ', '')}
                  stroke={getModelColor(m.model)}
                  fill={getModelColor(m.model)}
                  fillOpacity={0.1}
                  strokeWidth={2}
                />
              ))}
              {ensemble && (
                <Radar
                  name="Ensemble"
                  dataKey="Ensemble"
                  stroke={getModelColor('Soft Voting Ensemble')}
                  fill={getModelColor('Soft Voting Ensemble')}
                  fillOpacity={0.15}
                  strokeWidth={2.5}
                  strokeDasharray="5 3"
                />
              )}
              <Legend
                wrapperStyle={{ fontSize: 11, paddingTop: 12 }}
                iconType="circle"
                iconSize={8}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* ─── SHAP Feature Importance ─────────────────────── */}
        <div className="glass-card p-6 animate-slide-up">
          <h3 className="text-sm font-semibold text-white mb-1">
            SHAP Feature Importance
          </h3>
          <p className="text-xs text-white/40 mb-4">
            Top features by mean |SHAP| value — driving theft predictions
          </p>
          {shapData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={140}
                  tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="importance" name="SHAP Impact" radius={[0, 4, 4, 0]}>
                  {shapData.map((_, i) => (
                    <Cell
                      key={i}
                      fill={`hsl(${200 + i * 10}, 70%, ${55 - i * 2}%)`}
                      opacity={0.8}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <Info className="w-10 h-10 text-white/10 mx-auto mb-3" />
                <p className="text-sm text-white/30">
                  SHAP values not computed yet.
                </p>
                <p className="text-xs text-white/20 mt-1">
                  Install <code className="text-brand-400">shap</code> and retrain.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ─── Per-Model Detail Cards ───────────────────────── */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold text-white/40 uppercase tracking-wider flex items-center gap-2">
          <Activity className="w-4 h-4" />
          Detailed Model Evaluation
        </h2>

        <div className="space-y-3">
          {models.map((model, idx) => {
            const isExpanded = expandedModel === idx;
            const cm = model.confusion_matrix;
            const isEnsemble = model.model.includes('Ensemble');

            return (
              <div
                key={idx}
                className={`glass-card overflow-hidden animate-fade-in transition-all duration-300 ${
                  isEnsemble ? 'border-l-4 border-l-cyan-500' : ''
                }`}
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                {/* Card Header */}
                <button
                  onClick={() => setExpandedModel(isExpanded ? null : idx)}
                  className="w-full px-6 py-4 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ background: getModelColor(model.model) }}
                    />
                    <div className="text-left">
                      <h4 className="text-sm font-semibold text-white">
                        {model.model}
                        {isEnsemble && (
                          <span className="ml-2 text-[10px] font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full uppercase">
                            Best
                          </span>
                        )}
                      </h4>
                      <p className="text-[11px] text-white/30">
                        Threshold: {model.threshold.toFixed(4)}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    {/* Quick metrics */}
                    <div className="hidden sm:flex items-center gap-6">
                      {[
                        { label: 'Acc', value: model.accuracy },
                        { label: 'F1', value: model.f1_score },
                        { label: 'AUC', value: model.auc_roc },
                      ].map(m => (
                        <div key={m.label} className="text-right">
                          <p className={`text-sm font-bold font-mono ${
                            m.value >= 0.95 ? 'text-green-400' :
                            m.value >= 0.8 ? 'text-amber-400' :
                            'text-red-400'
                          }`}>
                            {(m.value * 100).toFixed(1)}%
                          </p>
                          <p className="text-[10px] text-white/30">{m.label}</p>
                        </div>
                      ))}
                    </div>

                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-white/30" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-white/30" />
                    )}
                  </div>
                </button>

                {/* Expanded Detail */}
                {isExpanded && (
                  <div className="px-6 pb-5 pt-2 border-t border-white/[0.06] animate-slide-up">
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                      {[
                        { label: 'Accuracy', value: model.accuracy },
                        { label: 'Precision', value: model.precision },
                        { label: 'Recall', value: model.recall },
                        { label: 'F1 Score', value: model.f1_score },
                        { label: 'AUC-ROC', value: model.auc_roc },
                        { label: 'PR-AUC', value: model.pr_auc },
                      ].map(m => (
                        <div key={m.label} className="bg-white/[0.03] rounded-xl p-3 border border-white/[0.05]">
                          <p className="text-[10px] text-white/40 uppercase font-semibold tracking-wider">
                            {m.label}
                          </p>
                          <p className={`text-lg font-bold font-mono mt-1 ${
                            m.value >= 0.95 ? 'text-green-400' :
                            m.value >= 0.8 ? 'text-amber-400' :
                            m.value >= 0.6 ? 'text-orange-400' :
                            'text-red-400'
                          }`}>
                            {(m.value * 100).toFixed(1)}%
                          </p>
                        </div>
                      ))}
                    </div>

                    {/* Confusion Matrix */}
                    {cm && (
                      <div>
                        <h5 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">
                          Confusion Matrix
                        </h5>
                        <div className="inline-grid grid-cols-3 gap-0 text-center text-xs">
                          {/* Header */}
                          <div className="p-2" />
                          <div className="p-2 text-white/40 font-semibold">Predicted Normal</div>
                          <div className="p-2 text-white/40 font-semibold">Predicted Theft</div>

                          {/* Row 1: Actual Normal */}
                          <div className="p-2 text-white/40 font-semibold text-right pr-4">Actual Normal</div>
                          <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg m-0.5">
                            <p className="text-lg font-bold text-green-400 font-mono">{cm[0][0]}</p>
                            <p className="text-[10px] text-green-400/60">TN</p>
                          </div>
                          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg m-0.5">
                            <p className="text-lg font-bold text-red-400 font-mono">{cm[0][1]}</p>
                            <p className="text-[10px] text-red-400/60">FP</p>
                          </div>

                          {/* Row 2: Actual Theft */}
                          <div className="p-2 text-white/40 font-semibold text-right pr-4">Actual Theft</div>
                          <div className="p-3 bg-orange-500/10 border border-orange-500/20 rounded-lg m-0.5">
                            <p className="text-lg font-bold text-orange-400 font-mono">{cm[1][0]}</p>
                            <p className="text-[10px] text-orange-400/60">FN</p>
                          </div>
                          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg m-0.5">
                            <p className="text-lg font-bold text-blue-400 font-mono">{cm[1][1]}</p>
                            <p className="text-[10px] text-blue-400/60">TP</p>
                          </div>
                        </div>

                        {/* Derived metrics */}
                        <div className="flex gap-4 mt-4 text-xs text-white/40">
                          <span>
                            TPR: <span className="text-white/70 font-mono">
                              {(cm[1][1] / (cm[1][1] + cm[1][0]) * 100 || 0).toFixed(1)}%
                            </span>
                          </span>
                          <span>
                            FPR: <span className="text-white/70 font-mono">
                              {(cm[0][1] / (cm[0][0] + cm[0][1]) * 100 || 0).toFixed(1)}%
                            </span>
                          </span>
                          <span>
                            Total: <span className="text-white/70 font-mono">
                              {cm[0][0] + cm[0][1] + cm[1][0] + cm[1][1]}
                            </span>
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ─── Feature Names ────────────────────────────────── */}
      {featureNames.length > 0 && (
        <div className="glass-card p-6 animate-slide-up">
          <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
            <Layers className="w-4 h-4 text-brand-400" />
            Engineered Features ({featureNames.length})
          </h3>
          <p className="text-xs text-white/40 mb-4">
            Features extracted per consumer following the research paper methodology
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2">
            {featureNames.map((name, i) => {
              const category = name.split('_')[0];
              const categoryColors = {
                stat: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
                temp: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
                anom: 'text-red-400 bg-red-500/10 border-red-500/20',
                comp: 'text-green-400 bg-green-500/10 border-green-500/20',
                meta: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
                adv: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
              };
              const colorClass = categoryColors[category] || 'text-white/60 bg-white/5 border-white/10';

              return (
                <div
                  key={i}
                  className={`px-3 py-2 rounded-lg text-xs font-medium border ${colorClass}
                              animate-fade-in`}
                  style={{ animationDelay: `${i * 15}ms` }}
                >
                  {name.replace(/_/g, ' ')}
                </div>
              );
            })}
          </div>
          <div className="flex flex-wrap gap-4 mt-4 text-[11px] text-white/30">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-400" /> Statistical
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-400" /> Temporal
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-red-400" /> Anomaly
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-400" /> Comparative
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-purple-400" /> Metadata
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400" /> Advanced
            </span>
          </div>
        </div>
      )}

      {/* ─── Research Paper Reference ─────────────────────── */}
      <div className="glass-card p-6 border-l-4 border-l-brand-500/40 animate-slide-up">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-brand-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-white mb-1">Research Paper Reference</h4>
            <p className="text-xs text-white/40 leading-relaxed">
              This implementation follows the methodology from{' '}
              <strong className="text-white/60">
                "Electricity Theft Detection Using Machine Learning"
              </strong>{' '}
              by Aggarwal, Sharma, Saini & Kumar (MIET). The pipeline includes SGCC dataset preprocessing,
              65+ engineered features across 6 categories, SMOTE class rebalancing, 5 model paradigms
              (RF, XGBoost, LSTM, IF, DNN), soft voting & stacking ensembles, and SHAP explainability.
            </p>
            <div className="flex gap-4 mt-3 text-[11px]">
              <span className="text-white/30">
                Models: <span className="text-brand-400">{models.length}</span>
              </span>
              <span className="text-white/30">
                Features: <span className="text-brand-400">{featureNames.length}</span>
              </span>
              <span className="text-white/30">
                Consumers: <span className="text-brand-400">{datasetInfo.n_consumers?.toLocaleString()}</span>
              </span>
              <span className="text-white/30">
                Ensemble: <span className="text-brand-400">Stacking + Soft Voting</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
