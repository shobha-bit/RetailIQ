import React, { useMemo } from 'react';
import { Filter, RotateCcw, Search, Calendar, Globe, Tag, Store } from 'lucide-react';
import { useFilters } from '../../context/FilterContext';
import { useDataset } from '../../context/DatasetContext';
import { REGIONS, CATEGORIES, CHANNELS } from '../../data/mockData';

export const FilterBar: React.FC<{ id?: string }> = ({ id = 'global-filter-bar' }) => {
  const {
    filters,
    setDateRange,
    setRegion,
    setCategory,
    setChannel,
    setSearchQuery,
    resetFilters,
    hasActiveFilters
  } = useFilters();

  const { realDataset, isRealRetailDataLoaded } = useDataset();

  const availableRegions = useMemo(() => {
    if (isRealRetailDataLoaded && realDataset && realDataset.orders.length > 0) {
      const set = new Set(realDataset.orders.map((o) => o.region).filter(Boolean));
      return Array.from(set).sort();
    }
    return REGIONS;
  }, [isRealRetailDataLoaded, realDataset]);

  const availableCategories = useMemo(() => {
    if (isRealRetailDataLoaded && realDataset && realDataset.products.length > 0) {
      const set = new Set(realDataset.products.map((p) => p.category).filter(Boolean));
      return Array.from(set).sort();
    }
    return CATEGORIES;
  }, [isRealRetailDataLoaded, realDataset]);

  const availableChannels = useMemo(() => {
    if (isRealRetailDataLoaded && realDataset && realDataset.customers.length > 0) {
      const set = new Set(realDataset.customers.map((c) => c.segment).filter(Boolean));
      return Array.from(set).sort();
    }
    return CHANNELS;
  }, [isRealRetailDataLoaded, realDataset]);

  const dateRangeOptions: { id: typeof filters.dateRange; label: string }[] = [
    { id: 'all', label: 'All Time' },
    { id: '7d', label: 'Last 7D' },
    { id: '30d', label: 'Last 30D' },
    { id: '90d', label: 'Last 90D' },
    { id: 'ytd', label: 'YTD' },
    { id: '1y', label: 'Last 1Y' }
  ];

  return (
    <div
      id={id}
      className="bg-white border border-slate-200/90 rounded-xl p-3 shadow-xs mb-6 flex flex-col xl:flex-row xl:items-center justify-between gap-3 text-xs"
    >
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-100 text-slate-700 font-semibold">
          <Filter className="w-3.5 h-3.5 text-blue-600" />
          <span>Filters</span>
          {hasActiveFilters && (
            <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
          )}
        </div>

        {/* Date presets */}
        <div className="flex items-center gap-1 bg-slate-50 p-1 rounded-lg border border-slate-200/80">
          <Calendar className="w-3.5 h-3.5 text-slate-400 ml-1 mr-0.5" />
          {dateRangeOptions.map((opt) => (
            <button
              key={opt.id}
              id={`filter-date-${opt.id}`}
              onClick={() => setDateRange(opt.id)}
              className={`px-2 py-1 rounded font-medium transition-all ${
                filters.dateRange === opt.id
                  ? 'bg-blue-600 text-white shadow-xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {/* Region selector */}
        <div className="flex items-center gap-1 bg-slate-50 px-2 py-1 rounded-lg border border-slate-200/80">
          <Globe className="w-3.5 h-3.5 text-slate-400" />
          <select
            id="filter-region-select"
            value={filters.region}
            onChange={(e) => setRegion(e.target.value)}
            className="bg-transparent text-slate-700 font-medium focus:outline-none cursor-pointer"
          >
            <option value="all">All Regions</option>
            {availableRegions.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>

        {/* Category selector */}
        <div className="flex items-center gap-1 bg-slate-50 px-2 py-1 rounded-lg border border-slate-200/80">
          <Tag className="w-3.5 h-3.5 text-slate-400" />
          <select
            id="filter-category-select"
            value={filters.category}
            onChange={(e) => setCategory(e.target.value)}
            className="bg-transparent text-slate-700 font-medium focus:outline-none cursor-pointer"
          >
            <option value="all">All Categories</option>
            {availableCategories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        {/* Channel selector */}
        <div className="flex items-center gap-1 bg-slate-50 px-2 py-1 rounded-lg border border-slate-200/80">
          <Store className="w-3.5 h-3.5 text-slate-400" />
          <select
            id="filter-channel-select"
            value={filters.channel}
            onChange={(e) => setChannel(e.target.value)}
            className="bg-transparent text-slate-700 font-medium focus:outline-none cursor-pointer"
          >
            <option value="all">All Channels / Segments</option>
            {availableChannels.map((ch) => (
              <option key={ch} value={ch}>
                {ch}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex items-center gap-2 self-end xl:self-auto w-full xl:w-auto">
        <div className="relative flex-1 xl:w-56">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            id="filter-search-input"
            type="text"
            value={filters.searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search SKU, order, customer..."
            className="w-full pl-8 pr-2.5 py-1.5 text-xs bg-slate-50 border border-slate-200/90 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white"
          />
        </div>

        {hasActiveFilters && (
          <button
            id="filter-reset-button"
            onClick={resetFilters}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-600 hover:text-rose-600 hover:border-rose-200 transition-colors font-medium"
            title="Clear all active filters"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset</span>
          </button>
        )}
      </div>
    </div>
  );
};
