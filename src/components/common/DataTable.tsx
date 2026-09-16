import React, { useState, useMemo } from 'react';
import { ArrowUpDown, ChevronLeft, ChevronRight, Download, Search } from 'lucide-react';
import Papa from 'papaparse';

export interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (item: T, index: number) => React.ReactNode;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
  width?: string;
}

export interface DataTableProps<T> {
  id: string;
  title?: string;
  subtitle?: string;
  data: T[];
  columns: Column<T>[];
  pageSizeOptions?: number[];
  searchable?: boolean;
  searchPlaceholder?: string;
  exportFilename?: string;
  actions?: React.ReactNode;
  emptyMessage?: string;
}

export function DataTable<T extends Record<string, any>>({
  id,
  title,
  subtitle,
  data,
  columns,
  pageSizeOptions = [10, 25, 50],
  searchable = true,
  searchPlaceholder = 'Search records...',
  exportFilename = 'retail_export',
  actions,
  emptyMessage = 'No matching records found'
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(pageSizeOptions[0] || 10);

  // Search filtering
  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) return data;
    const term = searchTerm.toLowerCase();
    return data.filter((item) =>
      Object.values(item).some((val) => {
        if (val === null || val === undefined) return false;
        return String(val).toLowerCase().includes(term);
      })
    );
  }, [data, searchTerm]);

  // Sorting
  const sortedData = useMemo(() => {
    if (!sortKey) return filteredData;
    return [...filteredData].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (aVal === bVal) return 0;
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      return sortDirection === 'asc'
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });
  }, [filteredData, sortKey, sortDirection]);

  // Pagination
  const totalPages = Math.ceil(sortedData.length / pageSize) || 1;
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedData.slice(start, start + pageSize);
  }, [sortedData, currentPage, pageSize]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      if (sortDirection === 'asc') setSortDirection('desc');
      else {
        setSortKey(null);
        setSortDirection('asc');
      }
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const handleExportCSV = () => {
    const csv = Papa.unparse(sortedData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${exportFilename}_${Date.now()}.csv`;
    link.click();
  };

  return (
    <div id={id} className="bg-white border border-slate-200/90 rounded-xl shadow-xs overflow-hidden">
      {(title || searchable || actions) && (
        <div className="p-4 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-slate-50/50">
          <div>
            {title && <h3 className="text-base font-bold text-slate-900 tracking-tight">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-700 mt-0.5">{subtitle}</p>}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {searchable && (
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  id={`${id}-search-input`}
                  type="text"
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setCurrentPage(1);
                  }}
                  placeholder={searchPlaceholder}
                  className="pl-8 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 w-48 sm:w-60"
                />
              </div>
            )}

            {actions}

            <button
              id={`${id}-export-button`}
              onClick={handleExportCSV}
              title="Export filtered records to CSV"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-slate-500" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/80">
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  onClick={() => col.sortable && handleSort(col.key as string)}
                  style={{ width: col.width }}
                  className={`px-4 py-3 font-semibold text-slate-600 uppercase tracking-wider text-[11px] select-none ${
                    col.sortable ? 'cursor-pointer hover:bg-slate-100/80 transition-colors' : ''
                  } ${
                    col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'
                  }`}
                >
                  <div className={`inline-flex items-center gap-1 ${col.align === 'right' ? 'flex-row-reverse' : ''}`}>
                    <span>{col.header}</span>
                    {col.sortable && (
                      <ArrowUpDown
                        className={`w-3 h-3 ${
                          sortKey === col.key ? 'text-blue-600 font-bold' : 'text-slate-400 opacity-60'
                        }`}
                      />
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-12 text-center text-slate-700">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              paginatedData.map((row, rowIdx) => (
                <tr
                  key={rowIdx}
                  className="hover:bg-blue-50/20 transition-colors odd:bg-white even:bg-slate-50/30"
                >
                  {columns.map((col, colIdx) => (
                    <td
                      key={colIdx}
                      className={`px-4 py-3 text-slate-700 ${
                        col.align === 'right'
                          ? 'text-right'
                          : col.align === 'center'
                          ? 'text-center'
                          : 'text-left'
                      }`}
                    >
                      {col.render ? col.render(row, rowIdx) : String(row[col.key as string] ?? '')}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-3.5 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-700 bg-slate-50/40">
        <div className="flex items-center gap-2">
          <span>
            Showing <strong className="text-slate-800">{sortedData.length === 0 ? 0 : (currentPage - 1) * pageSize + 1}</strong> to{' '}
            <strong className="text-slate-800">{Math.min(currentPage * pageSize, sortedData.length)}</strong> of{' '}
            <strong className="text-slate-800">{sortedData.length}</strong> entries
          </span>
          <div className="flex items-center gap-1.5 ml-3 border-l border-slate-200 pl-3">
            <span>Per page:</span>
            <select
              id={`${id}-pagesize-select`}
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="px-2 py-1 text-xs bg-white border border-slate-200 rounded text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {pageSizeOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            id={`${id}-prev-page-btn`}
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="p-1.5 rounded border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="px-2.5 py-1 text-xs font-semibold text-slate-700">
            Page {currentPage} of {totalPages}
          </span>
          <button
            id={`${id}-next-page-btn`}
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="p-1.5 rounded border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
