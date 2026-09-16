import React, { useState } from 'react';
import {
  Terminal,
  Play,
  Copy,
  Check,
  Code2,
  Cpu,
  Clock,
  Sparkles,
  FileCode,
  Download
} from 'lucide-react';
import { PYTHON_PIPELINES } from '../data/mockData';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';

export const PythonHub: React.FC = () => {
  const [selectedScriptId, setSelectedScriptId] = useState<string>('etl_pipeline');
  const [copied, setCopied] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [activeLogs, setActiveLogs] = useState<string[]>([]);
  const [activeMetrics, setActiveMetrics] = useState<Record<string, string | number>>({});

  const activeScript = PYTHON_PIPELINES.find((p) => p.id === selectedScriptId) || PYTHON_PIPELINES[0];

  const handleRunSimulation = () => {
    setIsRunning(true);
    setActiveLogs(['[SYS] Allocating Python 3.12 data science runtime environment...']);
    setActiveMetrics({});

    let step = 0;
    const logs = activeScript.executionOutput.logs;

    const interval = setInterval(() => {
      if (step < logs.length) {
        setActiveLogs((prev) => [...prev, logs[step]]);
        step++;
      } else {
        clearInterval(interval);
        setIsRunning(false);
        setActiveMetrics(activeScript.executionOutput.metrics);
      }
    }, 280);
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(activeScript.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadScript = () => {
    const blob = new Blob([activeScript.code], { type: 'text/plain;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = activeScript.filename;
    link.click();
  };

  return (
    <div id="python-hub-page" className="space-y-6">
      <PageHeader
        id="python-hub-header"
        title="Python Data Science & ML Pipeline Hub"
        description="Inspect and execute production-grade Python data processing, RFM customer segmentation, Holt-Winters revenue forecasting, and pricing elasticity models."
        badge={<Badge variant="purple" dot>Python 3.12 Engine</Badge>}
      />

      {/* Script Selector Tabs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {PYTHON_PIPELINES.map((p) => {
          const isSelected = p.id === selectedScriptId;
          return (
            <button
              key={p.id}
              onClick={() => {
                setSelectedScriptId(p.id);
                setActiveLogs([]);
                setActiveMetrics({});
              }}
              className={`p-4 rounded-xl text-left border transition-all shadow-xs ${
                isSelected
                  ? 'bg-blue-50/80 border-blue-400 ring-2 ring-blue-500/20'
                  : 'bg-white border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="font-mono text-xs font-bold text-slate-800 flex items-center gap-1.5">
                  <FileCode className="w-3.5 h-3.5 text-blue-600" />
                  {p.filename}
                </span>
                <Badge variant={p.category === 'ETL' ? 'primary' : p.category === 'Segmentation' ? 'purple' : 'success'} size="sm">
                  {p.category}
                </Badge>
              </div>
              <h4 className="text-xs font-bold text-slate-900 line-clamp-1">{p.title}</h4>
              <p className="text-[11px] text-slate-500 line-clamp-2 mt-1 leading-snug">{p.description}</p>
            </button>
          );
        })}
      </div>

      {/* Main Execution Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Code Editor Panel */}
        <div className="lg:col-span-7 bg-slate-950 rounded-xl border border-slate-800 shadow-md overflow-hidden flex flex-col">
          <div className="px-4 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between text-xs text-slate-300">
            <div className="flex items-center gap-2">
              <Code2 className="w-4 h-4 text-blue-400" />
              <span className="font-mono font-bold text-white">{activeScript.filename}</span>
              <span className="text-[10px] text-slate-500">Python 3.12 (Pandas / Statsmodels / NumPy)</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyCode}
                className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                title="Copy script code"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              <button
                onClick={handleDownloadScript}
                className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                title="Download .py file"
              >
                <Download className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <pre className="p-4 text-xs font-mono text-slate-300 overflow-x-auto leading-relaxed max-h-[420px] bg-slate-950">
            <code>{activeScript.code}</code>
          </pre>
        </div>

        {/* Live Execution Console */}
        <div className="lg:col-span-5 flex flex-col space-y-4">
          <div className="bg-white border border-slate-200/90 rounded-xl p-5 shadow-xs flex-1 flex flex-col">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-slate-700" />
                <h3 className="text-sm font-bold text-slate-900">Pipeline Execution Terminal</h3>
              </div>

              <button
                onClick={handleRunSimulation}
                disabled={isRunning}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-xs"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{isRunning ? 'Executing...' : 'Run Pipeline'}</span>
              </button>
            </div>

            {/* Terminal Window */}
            <div className="bg-slate-950 text-emerald-400 font-mono text-[11px] p-3.5 rounded-lg flex-1 min-h-[200px] max-h-[260px] overflow-y-auto space-y-1">
              {activeLogs.length === 0 && !isRunning ? (
                <div className="text-slate-500 italic">
                  Ready to execute {activeScript.filename}. Click "Run Pipeline" to launch the simulated Python worker environment.
                </div>
              ) : (
                activeLogs.map((log, idx) => (
                  <div key={idx} className="leading-snug">
                    <span className="text-slate-500 mr-1.5">&gt;</span>
                    <span>{log}</span>
                  </div>
                ))
              )}
            </div>

            {/* Output Metrics Grid */}
            {Object.keys(activeMetrics).length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-100">
                <span className="text-[10px] uppercase font-bold text-slate-500 block mb-2">
                  Engine Execution Metrics
                </span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {Object.entries(activeMetrics).map(([key, val]) => (
                    <div key={key} className="p-2 bg-slate-50 rounded-lg border border-slate-200/80">
                      <span className="text-[10px] text-slate-500 block truncate">{key}</span>
                      <span className="font-bold text-slate-900 font-mono">{String(val)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
