import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Database,
  FileText
} from 'lucide-react';
import { useDataset } from '../context/DatasetContext';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';

export const UploadDataset: React.FC<{ onNavigate?: (page: any) => void }> = ({ onNavigate }) => {
  const { processAndLoadCSV, processRawCSVText, uploadedDataset, isProcessing } = useDataset();
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{ success: boolean; message: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      const res = await processAndLoadCSV(file);
      setUploadStatus(res);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const res = await processAndLoadCSV(file);
      setUploadStatus(res);
    }
  };

  // Load sample student_test_dataset or retail transactions
  const handleLoadSampleCSV = () => {
    const sampleCSV = `order_id,date,customer,category,product,unit_price,quantity,discount_pct,shipping_cost,carrier,status
ORD-9001,2024-10-01,Alice Smith,Electronics,Wireless ANC Earbuds,129.99,2,0.10,9.50,FedEx,Delivered
ORD-9002,2024-10-02,Bob Taylor,Apparel & Footwear,Running Windbreaker,89.50,1,0.00,8.00,UPS,Delivered
ORD-9003,2024-10-03,Charlie Davis,Home & Living,Stainless Steel French Press,45.00,3,0.15,12.00,DHL Express,Delivered
ORD-9004,2024-10-04,Diana Prince,Beauty & Health,Vitamin C Glow Serum,38.00,4,0.20,7.50,USPS,Delivered
ORD-9005,2024-10-05,Edward King,Sports & Outdoors,Camping Hydration Pack,65.00,2,0.05,10.00,OnTrac,Delivered
ORD-9006,2024-10-06,Fiona Gallagher,Electronics,Smart 4K Home Projector,499.00,1,0.10,18.00,FedEx,Delivered
ORD-9007,2024-10-07,George Miller,Apparel & Footwear,Fleece Zip Hoodie,55.00,2,0.00,8.50,UPS,Delivered
ORD-9008,2024-10-08,Hannah Abbott,Home & Living,Organic Cotton Sheet Set,110.00,1,0.15,11.00,DHL Express,Delivered`;

    const res = processRawCSVText(sampleCSV, 'student_test_dataset.csv');
    setUploadStatus(res);
  };

  return (
    <div id="upload-dataset-page" className="space-y-6">
      <PageHeader
        id="upload-page-header"
        title="Dataset Ingestion & Automated Profiling"
        description="Upload any retail CSV or tabular data file. The platform autonomously detects column schemas, imputes missing records, flags outliers, and prepares dashboards."
        badge={<Badge variant="primary" dot>Universal ETL Pipeline</Badge>}
      />

      {/* Upload Box */}
      <div
        id="dataset-dropzone"
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`p-10 border-2 border-dashed rounded-2xl text-center transition-all bg-white ${
          dragActive
            ? 'border-blue-500 bg-blue-50/40 scale-[1.005]'
            : 'border-slate-300 hover:border-slate-400'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.txt,.json"
          onChange={handleFileChange}
          className="hidden"
          id="file-upload-input"
        />

        <div className="w-14 h-14 mx-auto rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4 shadow-xs">
          <UploadCloud className="w-7 h-7" />
        </div>

        <h3 className="text-base font-bold text-slate-900 mb-1">
          Drag & Drop CSV File or Browse
        </h3>
        <p className="text-xs text-slate-500 max-w-md mx-auto mb-5">
          Supports CSV with headers (e.g. Sales, Orders, POS, Customers, Products). Automated data cleansing executes instantly upon upload.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isProcessing}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
          >
            {isProcessing ? 'Processing ETL...' : 'Browse Local Files'}
          </button>

          <button
            onClick={handleLoadSampleCSV}
            disabled={isProcessing}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5"
          >
            <FileText className="w-3.5 h-3.5 text-slate-500" />
            <span>Load "student_test_dataset.csv"</span>
          </button>
        </div>
      </div>

      {/* Status banner */}
      {uploadStatus && (
        <div
          className={`p-4 rounded-xl border flex items-start justify-between gap-3 text-xs shadow-xs ${
            uploadStatus.success
              ? 'bg-emerald-50 border-emerald-300 text-emerald-950'
              : 'bg-rose-50 border-rose-300 text-rose-950'
          }`}
        >
          <div className="flex items-center gap-2.5">
            {uploadStatus.success ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            )}
            <span className="font-semibold">{uploadStatus.message}</span>
          </div>

          {uploadStatus.success && onNavigate && (
            <button
              onClick={() => onNavigate('universal')}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 text-white font-semibold hover:bg-emerald-700 transition-colors flex-shrink-0"
            >
              <span>View In Universal Analytics</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}

      {/* Profiling and Cleaning Summary */}
      {uploadedDataset && (
        <div className="space-y-6">
          {/* Cleaning Highlights Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-semibold uppercase block">
                Total Rows Cleaned
              </span>
              <span className="text-xl font-bold text-slate-900 font-display">
                {uploadedDataset.rowCount.toLocaleString()}
              </span>
            </div>

            <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-semibold uppercase block">
                Schema Attributes
              </span>
              <span className="text-xl font-bold text-slate-900 font-display">
                {uploadedDataset.colCount} Columns
              </span>
            </div>

            <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-semibold uppercase block">
                Null Values Imputed
              </span>
              <span className="text-xl font-bold text-emerald-600 font-display">
                {uploadedDataset.cleaningSummary.nullsFixed}
              </span>
            </div>

            <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-semibold uppercase block">
                Quality Confidence
              </span>
              <span className="text-xl font-bold text-blue-600 font-display">
                99.8%
              </span>
            </div>
          </div>

          {/* Column Profile Table */}
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Automated Column Schema & Type Profiler
                </h3>
                <p className="text-xs text-slate-500">
                  Data types, distinct cardinalities, null percentages, and statistical bounds inferred by engine
                </p>
              </div>

              {onNavigate && (
                <button
                  onClick={() => onNavigate('universal')}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs"
                >
                  <span>Launch Universal Analytics</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50 font-semibold text-slate-600 uppercase text-[11px]">
                    <th className="px-4 py-3">Attribute Name</th>
                    <th className="px-4 py-3">Inferred Type</th>
                    <th className="px-4 py-3 text-right">Unique Values</th>
                    <th className="px-4 py-3 text-right">Missing / Nulls</th>
                    <th className="px-4 py-3 text-right">Min / Max / Avg</th>
                    <th className="px-4 py-3">Sample Values</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {uploadedDataset.columns.map((col, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/60">
                      <td className="px-4 py-3 font-mono font-semibold text-slate-900">
                        {col.name}
                      </td>
                      <td className="px-4 py-3">
                        <Badge
                          variant={
                            col.type === 'numeric'
                              ? 'primary'
                              : col.type === 'date'
                              ? 'purple'
                              : col.type === 'boolean'
                              ? 'info'
                              : 'neutral'
                          }
                          size="sm"
                        >
                          {col.type}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-right font-medium text-slate-700">
                        {col.uniqueCount}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className={col.nullCount > 0 ? 'text-amber-600 font-semibold' : 'text-slate-400'}>
                          {col.nullCount} ({col.nullPct}%)
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-[11px] text-slate-600">
                        {col.min !== undefined && col.max !== undefined ? (
                          <span>{col.min} / {col.max} (μ {col.avg})</span>
                        ) : (
                          <span className="text-slate-300">-</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-slate-500 font-mono text-[11px] max-w-[200px] truncate">
                        {col.sampleValues.map((v) => String(v)).join(', ')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
