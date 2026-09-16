import React from 'react';
import {
  Menu,
  Download,
  UploadCloud,
  Sparkles,
  Database,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import { useDataset } from '../../context/DatasetContext';
import { PageId } from './Sidebar';

interface NavbarProps {
  onToggleSidebar: () => void;
  onNavigate: (page: PageId) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar, onNavigate }) => {
  const { activeDatasetName, datasetType, exportTransactionsToCSV, resetToDefault } = useDataset();

  return (
    <header
      id="main-navbar"
      className="h-16 bg-white border-b border-slate-200/90 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-xs"
    >
      <div className="flex items-center gap-3">
        <button
          id="navbar-mobile-menu-btn"
          onClick={onToggleSidebar}
          className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          title="Toggle Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200 text-xs font-medium text-slate-700">
            <Database className="w-3.5 h-3.5 text-blue-600" />
            <span className="max-w-[200px] truncate" title={activeDatasetName}>
              {activeDatasetName}
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 ml-0.5" />
          </div>

          {datasetType !== 'default' && (
            <button
              id="navbar-reset-dataset-btn"
              onClick={resetToDefault}
              className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-medium ml-1"
              title="Reset to default enterprise dataset"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Reset Default</span>
            </button>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        {/* Upload quick action */}
        <button
          id="navbar-upload-btn"
          onClick={() => onNavigate('upload')}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-slate-50 border border-slate-200 hover:bg-slate-100 transition-colors"
        >
          <UploadCloud className="w-3.5 h-3.5 text-slate-600" />
          <span className="hidden md:inline">Upload Data</span>
        </button>

        {/* AI copilot button */}
        <button
          id="navbar-insights-btn"
          onClick={() => onNavigate('insights')}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200 hover:bg-indigo-100 transition-colors"
        >
          <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
          <span className="hidden sm:inline">AI Copilot</span>
        </button>

        {/* Export transactions */}
        <button
          id="navbar-export-btn"
          onClick={exportTransactionsToCSV}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 shadow-xs transition-colors"
          title="Export current analytical transactions to CSV"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export CSV</span>
        </button>

        <div className="hidden lg:flex items-center gap-1 text-xs text-slate-700 border-l border-slate-200 pl-3">
          <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          <span className="font-semibold text-slate-700">Live Engine Active</span>
        </div>
      </div>
    </header>
  );
};
