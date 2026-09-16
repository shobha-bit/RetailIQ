import React from 'react';
import {
  LayoutDashboard,
  TrendingUp,
  Users,
  Boxes,
  Truck,
  RotateCcw,
  Sparkles,
  TableProperties,
  UploadCloud,
  Layers,
  Terminal,
  Info,
  ChevronLeft,
  ChevronRight,
  Database
} from 'lucide-react';
import { useDataset } from '../../context/DatasetContext';

export type PageId =
  | 'executive'
  | 'sales'
  | 'customers'
  | 'inventory'
  | 'logistics'
  | 'returns'
  | 'insights'
  | 'explorer'
  | 'upload'
  | 'universal'
  | 'python'
  | 'about';

interface SidebarProps {
  activePage: PageId;
  onSelectPage: (page: PageId) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activePage,
  onSelectPage,
  collapsed,
  onToggleCollapse
}) => {
  const { activeDatasetName, datasetType, loadSampleDataset } = useDataset();

  const navigationSections: {
    section: string;
    items: {
      id: PageId;
      label: string;
      icon: React.ElementType;
      badge?: string;
    }[];
  }[] = [
    {
      section: 'Core Intelligence',
      items: [
        { id: 'executive', label: 'Executive Dashboard', icon: LayoutDashboard },
        { id: 'sales', label: 'Sales & Revenue', icon: TrendingUp },
        { id: 'customers', label: 'Customer RFM', icon: Users, badge: 'RFM' },
        { id: 'inventory', label: 'Inventory & Stock', icon: Boxes },
        { id: 'logistics', label: 'Logistics & Carriers', icon: Truck },
        { id: 'returns', label: 'Return Analysis', icon: RotateCcw }
      ]
    },
    {
      section: 'Analytics & Models',
      items: [
        { id: 'insights', label: 'AI Retail Insights', icon: Sparkles, badge: 'AI' },
        { id: 'explorer', label: 'Universal Explorer', icon: TableProperties },
        { id: 'python', label: 'Python & ML Hub', icon: Terminal, badge: 'Py' }
      ]
    },
    {
      section: 'Data Engine',
      items: [
        { id: 'upload', label: 'Upload & Clean Data', icon: UploadCloud },
        { id: 'universal', label: 'Universal Analytics', icon: Layers, badge: 'Auto' },
        { id: 'about', label: 'Platform Architecture', icon: Info }
      ]
    }
  ];

  return (
    <aside
      id="main-sidebar"
      className={`fixed top-0 left-0 bottom-0 z-40 bg-slate-900 text-slate-300 flex flex-col transition-all duration-300 border-r border-slate-800 ${
        collapsed ? 'w-18' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800 bg-slate-950/40">
        {!collapsed ? (
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white font-black shadow-xs flex-shrink-0">
              RI
            </div>
            <div className="truncate">
              <span className="text-xs font-semibold text-blue-400 block leading-none uppercase tracking-wider">
                Enterprise
              </span>
              <span className="text-sm font-bold text-white tracking-tight leading-snug">
                Retail Intelligence
              </span>
            </div>
          </div>
        ) : (
          <div className="w-8 h-8 mx-auto rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white font-black shadow-xs">
            RI
          </div>
        )}

        <button
          id="sidebar-toggle-btn"
          onClick={onToggleCollapse}
          className={`p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors ${
            collapsed ? 'hidden' : 'block'
          }`}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
      </div>

      {/* Navigation List */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {navigationSections.map((sec, secIdx) => (
          <div key={secIdx} className="space-y-1">
            {!collapsed && (
              <h4 className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2">
                {sec.section}
              </h4>
            )}
            {sec.items.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  id={`nav-link-${item.id}`}
                  onClick={() => onSelectPage(item.id)}
                  title={collapsed ? item.label : undefined}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/80'
                  } ${collapsed ? 'justify-center px-0' : ''}`}
                >
                  <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  {!collapsed && <span className="truncate text-left flex-1">{item.label}</span>}
                  {!collapsed && item.badge && (
                    <span
                      className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded ${
                        isActive
                          ? 'bg-blue-800 text-blue-100'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </div>

      {/* Sidebar Footer: Active dataset & quick switcher */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/40">
        {!collapsed ? (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-[11px] text-slate-400">
              <Database className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
              <span className="font-semibold truncate text-slate-300" title={activeDatasetName}>
                {activeDatasetName}
              </span>
            </div>

            <div className="pt-1">
              <label className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                Switch Benchmark
              </label>
              <select
                id="sidebar-benchmark-select"
                value={datasetType}
                onChange={(e) => loadSampleDataset(e.target.value as any)}
                className="w-full text-xs bg-slate-900 border border-slate-700 text-slate-200 rounded-md p-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
              >
                <option value="default">Omnichannel Global Retail</option>
                <option value="sample_holiday">Q4 Holiday Peak & Black Friday</option>
                <option value="sample_apparel">Apparel High-Return Profile</option>
              </select>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <button
              onClick={onToggleCollapse}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title="Expand Sidebar"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </aside>
  );
};
