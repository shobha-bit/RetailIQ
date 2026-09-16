import React from 'react';
import {
  Layers,
  Database,
  Cpu,
  TrendingUp,
  ShieldCheck,
  CheckCircle2,
  GitBranch,
  Terminal,
  Activity
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';

export const AboutProject: React.FC = () => {
  return (
    <div id="about-project-page" className="space-y-6">
      <PageHeader
        id="about-page-header"
        title="Enterprise Platform Blueprint & Technical Architecture"
        description="Comprehensive technical overview of data ingestion pipelines, analytical machine learning models, and system architectural specifications."
        badge={<Badge variant="primary">v2.4 Production Spec</Badge>}
      />

      {/* Architecture Layers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-slate-200/90 rounded-xl p-5 shadow-xs">
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
            <Database className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 mb-1">1. Ingestion & In-Memory ETL</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            High-throughput data ingestion capable of processing omnichannel POS transactions, e-commerce web hooks, CSV bulk uploads, and warehouse EDI streams with automated null-imputation and timestamp normalization.
          </p>
          <ul className="mt-3 space-y-1.5 text-xs text-slate-600 border-t border-slate-100 pt-3">
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>PapaParse streaming CSV parser</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>IQR Outlier anomaly capping</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Schema type detection engine</span>
            </li>
          </ul>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-xl p-5 shadow-xs">
          <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center mb-3">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 mb-1">2. Analytical & ML Engines</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Python and TypeScript predictive modules executing RFM customer behavioral clustering, exponential smoothing revenue forecasting, and log-log price elasticity regression for promotional calibration.
          </p>
          <ul className="mt-3 space-y-1.5 text-xs text-slate-600 border-t border-slate-100 pt-3">
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-purple-600" />
              <span>Quintile RFM Segmentation matrix</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-purple-600" />
              <span>Additive Holt-Winters time-series</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-purple-600" />
              <span>Price Elasticity of Demand (PED)</span>
            </li>
          </ul>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-xl p-5 shadow-xs">
          <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3">
            <TrendingUp className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 mb-1">3. Decision & Intelligence Layer</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Prescriptive intelligence dashboard, carrier SLA scorecard tracking, stockout risk mitigation alerts, and an interactive Gemini AI retail copilot delivering executive briefings on command.
          </p>
          <ul className="mt-3 space-y-1.5 text-xs text-slate-600 border-t border-slate-100 pt-3">
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Dynamic Recharts visual analytics</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Lead-time safety buffer monitor</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Reverse logistics defect playbooks</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Core Mathematical Formulations */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-5 shadow-xs space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-600" />
          <span>Core Analytical Formulations</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
            <span className="font-bold text-slate-800 block mb-1">Price Elasticity of Demand (PED)</span>
            <code className="text-blue-700 font-mono text-[11px] block mb-1">
              PED = (%Δ Quantity) / (%Δ Price)
            </code>
            <p className="text-slate-500">
              Evaluates consumer price sensitivity. Values &lt; -1 indicate elastic demand where price hikes severely reduce volume.
            </p>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
            <span className="font-bold text-slate-800 block mb-1">Reorder Point (ROP) with Buffer</span>
            <code className="text-blue-700 font-mono text-[11px] block mb-1">
              ROP = (Daily Demand × Lead Time) + Safety Stock
            </code>
            <p className="text-slate-500">
              Determines minimum replenishment triggers preventing stockouts during supplier transit lead times.
            </p>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
            <span className="font-bold text-slate-800 block mb-1">RFM Quintile Matrix</span>
            <code className="text-blue-700 font-mono text-[11px] block mb-1">
              RFM Score = (R × 100) + (F × 10) + M
            </code>
            <p className="text-slate-500">
              Ranks customer purchase recency, order count, and monetary spend into quintiles (1-5) for churn mitigation.
            </p>
          </div>
        </div>
      </div>

      {/* Technology Specifications */}
      <div className="bg-slate-900 text-slate-300 rounded-xl p-5 shadow-md">
        <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
          <Terminal className="w-4 h-4 text-blue-400" />
          <span>Platform Technology Stack</span>
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div>
            <span className="text-slate-500 block uppercase text-[10px]">Frontend Framework</span>
            <span className="text-white font-bold">React 19 & Vite 6</span>
          </div>
          <div>
            <span className="text-slate-500 block uppercase text-[10px]">Styling Engine</span>
            <span className="text-white font-bold">Tailwind CSS 4.1</span>
          </div>
          <div>
            <span className="text-slate-500 block uppercase text-[10px]">Data Visualization</span>
            <span className="text-white font-bold">Recharts 2.15</span>
          </div>
          <div>
            <span className="text-slate-500 block uppercase text-[10px]">AI Integration</span>
            <span className="text-white font-bold">@google/genai 2.4.0</span>
          </div>
        </div>
      </div>
    </div>
  );
};
