import React, { useMemo, useState } from 'react';
import {
  TableProperties,
  Download,
  Filter,
  Columns3,
  Search,
  CheckSquare,
  Square
} from 'lucide-react';
import { useDataset } from '../context/DatasetContext';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { DataTable } from '../components/common/DataTable';

export const DataExplorer: React.FC = () => {
  const { transactions, uploadedDataset, exportTransactionsToCSV } = useDataset();

  // If custom uploaded dataset exists, allow exploring its raw records, else transactions
  const isCustomDataset = uploadedDataset !== null && uploadedDataset.rawRecords.length > 0;
  const rawData = isCustomDataset ? uploadedDataset.rawRecords : transactions;

  // Derive column list
  const allColumns = useMemo(() => {
    if (rawData.length === 0) return [];
    return Object.keys(rawData[0]);
  }, [rawData]);

  const [visibleColumns, setVisibleColumns] = useState<string[]>(() => {
    if (allColumns.length > 8) {
      return allColumns.slice(0, 8);
    }
    return allColumns;
  });

  const [showColPicker, setShowColPicker] = useState(false);

  // Aggregation metrics for the current view
  const aggregations = useMemo(() => {
    if (rawData.length === 0) return null;
    const count = rawData.length;

    // Find numeric keys
    const first = rawData[0];
    const numericKeys = Object.keys(first).filter((k) => typeof first[k] === 'number');

    const sums: Record<string, number> = {};
    numericKeys.forEach((k) => {
      sums[k] = (rawData as any[]).reduce((acc: number, row: any) => acc + (Number(row[k]) || 0), 0);
    });

    return {
      count,
      sums
    };
  }, [rawData]);

  const toggleColumn = (col: string) => {
    if (visibleColumns.includes(col)) {
      if (visibleColumns.length > 1) {
        setVisibleColumns(visibleColumns.filter((c) => c !== col));
      }
    } else {
      setVisibleColumns([...visibleColumns, col]);
    }
  };

  const tableColumns = useMemo(() => {
    return visibleColumns.map((col) => ({
      key: col,
      header: col.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ').toUpperCase(),
      sortable: true,
      render: (row: any) => {
        const val = row[col];
        if (typeof val === 'boolean') {
          return val ? (
            <Badge variant="danger" size="sm">Yes</Badge>
          ) : (
            <Badge variant="neutral" size="sm">No</Badge>
          );
        }
        if (typeof val === 'number') {
          if (col.toLowerCase().includes('revenue') || col.toLowerCase().includes('price') || col.toLowerCase().includes('cost') || col.toLowerCase().includes('margin') && !col.toLowerCase().includes('pct')) {
            return <span className="font-semibold text-slate-900">${val.toFixed(2)}</span>;
          }
          if (col.toLowerCase().includes('pct') || col.toLowerCase().includes('rate')) {
            return <span>{val}%</span>;
          }
          return <span className="text-slate-800">{val}</span>;
        }
        return <span className="text-slate-700">{String(val ?? '')}</span>;
      }
    }));
  }, [visibleColumns]);

  return (
    <div id="data-explorer-page" className="space-y-6">
      <PageHeader
        id="explorer-page-header"
        title="Universal Data Explorer & Ledger"
        description="Tabular drilldown across all ingested attributes with multi-column sorting, visibility filters, and rapid CSV exportation."
        badge={<Badge variant="primary">{rawData.length} Records</Badge>}
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowColPicker(!showColPicker)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <Columns3 className="w-3.5 h-3.5 text-slate-500" />
              <span>Columns ({visibleColumns.length}/{allColumns.length})</span>
            </button>

            <button
              onClick={exportTransactionsToCSV}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold text-white bg-slate-900 rounded-lg hover:bg-slate-800 transition-colors shadow-xs"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </button>
          </div>
        }
      />

      {/* Column picker dropdown */}
      {showColPicker && (
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm animate-in fade-in">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-100 text-xs">
            <span className="font-bold text-slate-800">Select Visible Attributes:</span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setVisibleColumns(allColumns)}
                className="text-blue-600 hover:text-blue-800 font-semibold"
              >
                Show All
              </button>
              <span className="text-slate-300">|</span>
              <button
                onClick={() => setVisibleColumns(allColumns.slice(0, 6))}
                className="text-slate-600 hover:text-slate-900 font-medium"
              >
                Reset Default
              </button>
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 text-xs">
            {allColumns.map((col) => {
              const isSelected = visibleColumns.includes(col);
              return (
                <button
                  key={col}
                  onClick={() => toggleColumn(col)}
                  className={`flex items-center gap-1.5 p-1.5 rounded text-left transition-colors ${
                    isSelected
                      ? 'bg-blue-50 text-blue-800 font-medium'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {isSelected ? (
                    <CheckSquare className="w-3.5 h-3.5 text-blue-600 flex-shrink-0" />
                  ) : (
                    <Square className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                  )}
                  <span className="truncate">{col}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Aggregation Summary Bar */}
      {aggregations && (
        <div className="bg-slate-50 border border-slate-200/90 rounded-xl p-3 flex flex-wrap items-center gap-4 sm:gap-6 text-xs text-slate-700">
          <div>
            <span className="text-slate-400 font-semibold uppercase text-[10px] block">
              Total Records
            </span>
            <span className="text-sm font-bold text-slate-900 font-display">
              {aggregations.count.toLocaleString()} rows
            </span>
          </div>

          {aggregations.sums['netRevenue'] !== undefined && (
            <div className="border-l border-slate-200 pl-4 sm:pl-6">
              <span className="text-slate-400 font-semibold uppercase text-[10px] block">
                Total Net Sales
              </span>
              <span className="text-sm font-bold text-slate-900 font-display">
                ${aggregations.sums['netRevenue'].toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </span>
            </div>
          )}

          {aggregations.sums['grossMargin'] !== undefined && (
            <div className="border-l border-slate-200 pl-4 sm:pl-6">
              <span className="text-slate-400 font-semibold uppercase text-[10px] block">
                Total Gross Margin
              </span>
              <span className="text-sm font-bold text-emerald-700 font-display">
                ${aggregations.sums['grossMargin'].toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </span>
            </div>
          )}

          {aggregations.sums['quantity'] !== undefined && (
            <div className="border-l border-slate-200 pl-4 sm:pl-6">
              <span className="text-slate-400 font-semibold uppercase text-[10px] block">
                Total Units
              </span>
              <span className="text-sm font-bold text-slate-900 font-display">
                {aggregations.sums['quantity'].toLocaleString()} units
              </span>
            </div>
          )}
        </div>
      )}

      {/* Main Data Table */}
      <DataTable
        id="table-universal-data-ledger"
        title="Active Analytical Ledger"
        subtitle="Full schema record set rendered with dynamic formatting"
        data={rawData}
        columns={tableColumns}
      />
    </div>
  );
};
