import React, { useState, useMemo } from 'react';
import {
  Layers,
  BarChart3,
  PieChart as PieIcon,
  LineChart as LineIcon,
  ArrowRight,
  UploadCloud,
  FileSpreadsheet
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { useDataset } from '../context/DatasetContext';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { ChartCard } from '../components/common/ChartCard';
import { EmptyState } from '../components/common/EmptyState';

const PALETTE = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EC4899', '#06B6D4', '#64748B'];

export const UniversalDashboard: React.FC<{ onNavigate?: (page: any) => void }> = ({ onNavigate }) => {
  const { uploadedDataset, transactions } = useDataset();

  // Determine active raw data source
  const isCustomUploaded = uploadedDataset !== null && uploadedDataset.rawRecords.length > 0;
  const activeRecords = isCustomUploaded ? uploadedDataset.rawRecords : transactions;
  const datasetTitle = isCustomUploaded ? uploadedDataset.name : 'Omnichannel Retail Transactions (Default)';

  // Infer dimensions and metrics
  const { numericCols, categoricalCols, dateCols } = useMemo(() => {
    if (activeRecords.length === 0) {
      return { numericCols: [], categoricalCols: [], dateCols: [] };
    }
    const sample = activeRecords[0];
    const nCols: string[] = [];
    const cCols: string[] = [];
    const dCols: string[] = [];

    Object.keys(sample).forEach((key) => {
      const val = sample[key];
      if (typeof val === 'number') {
        nCols.push(key);
      } else if (typeof val === 'string' && val.length >= 8 && !isNaN(Date.parse(val))) {
        dCols.push(key);
      } else {
        cCols.push(key);
      }
    });

    return { numericCols: nCols, categoricalCols: cCols, dateCols: dCols };
  }, [activeRecords]);

  // Dimension and metric pickers
  const [selectedX, setSelectedX] = useState<string>(() => categoricalCols[0] || 'category');
  const [selectedY, setSelectedY] = useState<string>(() => numericCols[0] || 'netRevenue');
  const [chartType, setChartType] = useState<'bar' | 'line' | 'pie'>('bar');

  // Dynamically aggregate records
  const dynamicChartData = useMemo(() => {
    if (activeRecords.length === 0 || !selectedX || !selectedY) return [];

    const map = new Map<string, number>();
    activeRecords.forEach((row: any) => {
      const xVal = String(row[selectedX] ?? 'Unknown');
      const yVal = Number(row[selectedY]) || 0;
      map.set(xVal, (map.get(xVal) || 0) + yVal);
    });

    return Array.from(map.entries())
      .map(([name, value]) => ({
        name,
        value: Math.round(value * 100) / 100
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 12);
  }, [activeRecords, selectedX, selectedY]);

  // Dynamic KPI totals
  const kpiStats = useMemo(() => {
    if (activeRecords.length === 0) return [];
    return numericCols.slice(0, 4).map((col) => {
      const sum = (activeRecords as any[]).reduce((acc: number, r: any) => acc + (Number(r[col]) || 0), 0);
      const avg = Math.round((sum / activeRecords.length) * 100) / 100;
      return {
        col,
        label: col.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ').toUpperCase(),
        sum: Math.round(sum * 100) / 100,
        avg
      };
    });
  }, [activeRecords, numericCols]);

  return (
    <div id="universal-dashboard-page" className="space-y-6">
      <PageHeader
        id="universal-page-header"
        title="Universal Analytics"
        description="Autonomous visualization engine dynamically mapping any ingested dataset's schema into interactive analytical charts."
        badge={<Badge variant="primary" dot>{datasetTitle}</Badge>}
        actions={
          onNavigate && (
            <button
              onClick={() => onNavigate('upload')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 transition-colors"
            >
              <UploadCloud className="w-3.5 h-3.5 text-slate-500" />
              <span>Upload Another File</span>
            </button>
          )
        }
      />

      {/* Dynamic Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-400 font-semibold uppercase block">
            Record Volume
          </span>
          <span className="text-xl font-bold text-slate-900 font-display">
            {activeRecords.length.toLocaleString()}
          </span>
          <span className="text-[11px] text-slate-400 block mt-0.5">Rows analyzed</span>
        </div>

        {kpiStats.slice(0, 3).map((kpi, idx) => (
          <div key={idx} className="p-4 bg-white rounded-xl border border-slate-200 shadow-xs">
            <span className="text-xs text-slate-400 font-semibold uppercase block truncate" title={kpi.label}>
              Sum of {kpi.label}
            </span>
            <span className="text-xl font-bold text-slate-900 font-display">
              {kpi.sum > 1000 ? `$${kpi.sum.toLocaleString()}` : kpi.sum.toLocaleString()}
            </span>
            <span className="text-[11px] text-slate-400 block mt-0.5">
              Avg: {kpi.avg.toLocaleString()}
            </span>
          </div>
        ))}
      </div>

      {/* Dynamic Chart Builder Controls */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-4 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-700">Group By (X-Axis):</span>
            <select
              id="universal-select-x"
              value={selectedX}
              onChange={(e) => setSelectedX(e.target.value)}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-medium focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {[...categoricalCols, ...dateCols].map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-700">Metric (Y-Axis):</span>
            <select
              id="universal-select-y"
              value={selectedY}
              onChange={(e) => setSelectedY(e.target.value)}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-medium focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {numericCols.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Chart type toggle */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg">
          <button
            onClick={() => setChartType('bar')}
            className={`p-1.5 rounded ${chartType === 'bar' ? 'bg-white shadow-xs text-blue-600' : 'text-slate-500'}`}
            title="Bar Chart"
          >
            <BarChart3 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setChartType('line')}
            className={`p-1.5 rounded ${chartType === 'line' ? 'bg-white shadow-xs text-blue-600' : 'text-slate-500'}`}
            title="Line Chart"
          >
            <LineIcon className="w-4 h-4" />
          </button>
          <button
            onClick={() => setChartType('pie')}
            className={`p-1.5 rounded ${chartType === 'pie' ? 'bg-white shadow-xs text-blue-600' : 'text-slate-500'}`}
            title="Pie Chart"
          >
            <PieIcon className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Dynamic Chart Rendering */}
      <ChartCard
        id="card-dynamic-visualization"
        title={`Aggregated ${selectedY} grouped by ${selectedX}`}
        subtitle={`Dynamically evaluated across ${activeRecords.length} dataset rows`}
        badge={<Badge variant="primary">Auto Chart</Badge>}
      >
        <div className="h-80 w-full pt-2">
          {dynamicChartData.length === 0 ? (
            <EmptyState title="No data to plot" message="Select a different X or Y attribute." />
          ) : chartType === 'bar' ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dynamicChartData} margin={{ top: 10, right: 20, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis
                  dataKey="name"
                  stroke="#94A3B8"
                  fontSize={11}
                  tickLine={false}
                  angle={-20}
                  textAnchor="end"
                />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]}>
                  {dynamicChartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : chartType === 'line' ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dynamicChartData} margin={{ top: 10, right: 20, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis
                  dataKey="name"
                  stroke="#94A3B8"
                  fontSize={11}
                  tickLine={false}
                  angle={-20}
                  textAnchor="end"
                />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#3B82F6"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#3B82F6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={dynamicChartData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="value"
                  nameKey="name"
                  label={(entry) => `${entry.name} (${entry.value})`}
                  labelLine={false}
                >
                  {dynamicChartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </ChartCard>
    </div>
  );
};
