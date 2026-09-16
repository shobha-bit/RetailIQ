import React, { useMemo } from 'react';
import {
  DollarSign,
  ShoppingCart,
  Percent,
  TrendingUp,
  RotateCcw,
  Truck,
  AlertCircle,
  ArrowUpRight,
  Sparkles
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Line,
  PieChart,
  Pie,
  Cell,
  ComposedChart,
  Legend
} from 'recharts';
import { useDataset } from '../context/DatasetContext';
import { useFilters } from '../context/FilterContext';
import {
  calculateMonthlyTrends,
  calculateChannelPerformance,
  calculateCategoryPerformance,
  calculateTopProducts
} from '../utils/retailCalculations';
import { KPICard } from '../components/common/KPICard';
import { ChartCard } from '../components/common/ChartCard';
import { FilterBar } from '../components/common/FilterBar';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

const CHANNEL_COLORS: Record<string, string> = {
  Consumer: '#3B82F6',
  Corporate: '#8B5CF6',
  'Home Office': '#10B981',
  Online: '#3B82F6',
  'Retail Store': '#10B981',
  Marketplace: '#8B5CF6',
  'B2B Wholesale': '#F59E0B'
};

export const ExecutiveDashboard: React.FC<{ onNavigate?: (page: any) => void }> = ({ onNavigate }) => {
  const {
    transactions,
    inventory,
    isLoadingRetail,
    retailLoadError,
    reloadRetailData,
    getRetailKPIs
  } = useDataset();
  const { filterTransactions, retailFilters } = useFilters();

  // Dynamically filter transactions using the existing retail filter engine
  const filteredTx = useMemo(() => filterTransactions(transactions), [transactions, filterTransactions]);

  // Centralized real retail analytics KPIs
  const kpis = useMemo(() => getRetailKPIs(retailFilters), [getRetailKPIs, retailFilters]);

  const monthlyData = useMemo(() => {
    return calculateMonthlyTrends(filteredTx).map((m) => ({
      ...m,
      month: m.label
    }));
  }, [filteredTx]);

  const channelData = useMemo(() => {
    return calculateChannelPerformance(filteredTx).map((c) => ({
      name: c.channel,
      value: c.revenue,
      orders: c.orders
    }));
  }, [filteredTx]);

  const categoryData = useMemo(() => calculateCategoryPerformance(filteredTx), [filteredTx]);
  const topProducts = useMemo(() => {
    return calculateTopProducts(filteredTx, 5).map((p) => ({
      ...p,
      revenue: p.sales
    }));
  }, [filteredTx]);

  // Stockout alerts from real inventory
  const criticalItems = useMemo(() => {
    return inventory.filter((i) => i.stockoutRisk === 'Critical' || i.stockoutRisk === 'High').slice(0, 3);
  }, [inventory]);

  if (isLoadingRetail) {
    return (
      <div id="executive-dashboard-loading" className="p-6">
        <LoadingState message="Loading Executive Retail Intelligence from real datasets..." />
      </div>
    );
  }

  if (retailLoadError) {
    return (
      <div id="executive-dashboard-error" className="p-6">
        <ErrorState
          title="Failed to Load Executive Analytics"
          message={retailLoadError}
          onRetry={reloadRetailData}
        />
      </div>
    );
  }

  return (
    <div id="executive-dashboard-page" className="space-y-6">
      <PageHeader
        id="executive-page-header"
        title="Executive Intelligence Dashboard"
        description="Unified enterprise view of revenue velocity, margin health, omnichannel fulfillment, and strategic inventory signals."
        badge={<Badge variant="primary" dot>Omnichannel Live</Badge>}
        actions={
          <button
            id="header-ai-briefing-btn"
            onClick={() => onNavigate && onNavigate('insights')}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-xs transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Generate Executive Briefing</span>
          </button>
        }
      />

      <FilterBar id="executive-filter-bar" />

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-6 gap-4">
        <KPICard
          id="kpi-net-revenue"
          title="Total Sales"
          value={`$${kpis.totalSales.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          change={kpis.salesYoY}
          changePeriod="YoY Growth"
          target="$2.5M"
          icon={DollarSign}
          variant="accent"
        />
        <KPICard
          id="kpi-total-orders"
          title="Total Orders"
          value={kpis.totalOrders.toLocaleString()}
          subtitle="Completed transactions across channels"
          icon={ShoppingCart}
          variant="success"
        />
        <KPICard
          id="kpi-aov"
          title="Average Order Value"
          value={`$${kpis.averageOrderValue.toFixed(2)}`}
          subtitle="Revenue realized per distinct order"
          icon={TrendingUp}
        />
        <KPICard
          id="kpi-total-returns"
          title="Total Returns"
          value={kpis.totalReturns.toLocaleString()}
          subtitle="Verified return line item records"
          icon={RotateCcw}
        />
        <KPICard
          id="kpi-return-rate"
          title="Return Rate"
          value={`${kpis.returnRate.toFixed(2)}%`}
          target="< 10%"
          icon={Percent}
        />
        <KPICard
          id="kpi-avg-delivery"
          title="Average Delivery Days"
          value={`${kpis.averageDeliveryDays.toFixed(2)} days`}
          target="< 5 days"
          icon={Truck}
        />
      </div>

      {/* Real-time Alerts Banner */}
      {criticalItems.length > 0 && (
        <div className="bg-amber-50/80 border border-amber-200/90 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
          <div className="flex items-start sm:items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-100 text-amber-700 flex-shrink-0">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-xs font-bold text-amber-950 uppercase tracking-wide">
                  Supply Chain Alert: High Stockout Risk
                </h4>
                <Badge variant="warning" size="sm">{kpis.lowStockItems} Items at Reorder Point</Badge>
              </div>
              <p className="text-xs text-amber-800 mt-0.5">
                {kpis.lowStockItems} catalog items are below safety thresholds (including {criticalItems.map((item) => `${item.sku}`).join(', ')}). Average outbound delivery turnaround is {kpis.averageDeliveryDays.toFixed(2)} days.
              </p>
            </div>
          </div>
          <button
            onClick={() => onNavigate && onNavigate('inventory')}
            className="inline-flex items-center gap-1 text-xs font-semibold text-amber-900 bg-white border border-amber-300 px-3 py-1.5 rounded-lg hover:bg-amber-100 transition-colors flex-shrink-0"
          >
            <span>Review Replenishment</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Composite Revenue & Gross Margin Trend */}
        <div className="lg:col-span-2">
          <ChartCard
            id="chart-revenue-margin-trend"
            title="Revenue & Gross Profit Performance"
            subtitle="Monthly net sales volume plotted against gross profit contribution"
            badge={<Badge variant="neutral">Monthly Cadence</Badge>}
          >
            <div className="h-72 w-full">
              {monthlyData.length === 0 ? (
                <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                  No monthly trend records match the active filter criteria.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={monthlyData} margin={{ top: 10, right: 15, left: 10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                    <XAxis dataKey="month" stroke="#94A3B8" fontSize={11} tickLine={false} />
                    <YAxis
                      yAxisId="left"
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      tickFormatter={(v) => `$${v >= 1000000 ? (v / 1000000).toFixed(1) + 'M' : (v / 1000).toFixed(0) + 'k'}`}
                    />
                    <YAxis
                      yAxisId="right"
                      orientation="right"
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      tickFormatter={(v) => `$${v >= 1000000 ? (v / 1000000).toFixed(1) + 'M' : (v / 1000).toFixed(0) + 'k'}`}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                      formatter={(val: any, name: any) => [`$${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, name]}
                    />
                    <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px' }} />
                    <Bar yAxisId="left" dataKey="revenue" name="Net Revenue" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                    <Bar yAxisId="left" dataKey="profit" name="Gross Profit" fill="#10B981" radius={[4, 4, 0, 0]} />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="revenue"
                      name="Growth Trajectory"
                      stroke="#6366F1"
                      strokeWidth={2.5}
                      dot={{ r: 3, fill: '#6366F1' }}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              )}
            </div>
          </ChartCard>
        </div>

        {/* Channel Share Donut */}
        <div className="lg:col-span-1">
          <ChartCard
            id="chart-channel-share"
            title="Omnichannel Sales Split"
            subtitle="Gross contribution by retail touchpoint"
          >
            <div className="h-72 w-full flex flex-col items-center justify-center">
              {channelData.length === 0 ? (
                <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                  No channel records match the active filter criteria.
                </div>
              ) : (
                <>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={channelData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {channelData.map((entry) => (
                          <Cell key={entry.name} fill={CHANNEL_COLORS[entry.name] || '#64748B'} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                        formatter={(val: any) => [`$${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 'Revenue']}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="w-full flex flex-wrap items-center justify-center gap-x-4 gap-y-1.5 mt-2 pt-2 border-t border-slate-100 text-xs">
                    {channelData.map((entry) => (
                      <div key={entry.name} className="flex items-center gap-1.5">
                        <span
                          className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                          style={{ backgroundColor: CHANNEL_COLORS[entry.name] || '#64748B' }}
                        />
                        <span className="text-slate-600 truncate">{entry.name}:</span>
                        <span className="font-bold text-slate-900 ml-1">
                          ${entry.value >= 1000000 ? (entry.value / 1000000).toFixed(2) + 'M' : (entry.value / 1000).toFixed(1) + 'k'}
                        </span>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </ChartCard>
        </div>
      </div>

      {/* Category Performance & Top SKUs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ChartCard
            id="chart-category-performance"
            title="Category Revenue Distribution"
            subtitle="Gross sales generated per merchandise department"
          >
            <div className="h-72 w-full">
              {categoryData.length === 0 ? (
                <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                  No category records match the active filter criteria.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={categoryData}
                    layout="vertical"
                    margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
                    <XAxis
                      type="number"
                      stroke="#94A3B8"
                      fontSize={10}
                      tickLine={false}
                      tickFormatter={(v) => `$${v >= 1000000 ? (v / 1000000).toFixed(1) + 'M' : (v / 1000).toFixed(0) + 'k'}`}
                    />
                    <YAxis
                      type="category"
                      dataKey="category"
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      width={95}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                      formatter={(val: any) => [`$${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 'Revenue']}
                    />
                    <Bar dataKey="revenue" fill="#3B82F6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </ChartCard>
        </div>

        <div className="lg:col-span-2">
          <DataTable<typeof topProducts[0]>
            id="table-top-performing-skus"
            title="Top Velocity Products"
            subtitle="Highest revenue generating SKUs across active time horizon"
            data={topProducts}
            columns={[
              {
                key: 'sku',
                header: 'SKU',
                sortable: true,
                render: (row) => <span className="font-mono font-semibold text-slate-800">{row.sku}</span>
              },
              {
                key: 'name',
                header: 'Product Name',
                sortable: true,
                render: (row) => (
                  <div className="max-w-[200px] truncate" title={row.name}>
                    <span className="font-medium text-slate-900 block truncate">{row.name}</span>
                    <span className="text-[11px] text-slate-500">{row.category}</span>
                  </div>
                )
              },
              {
                key: 'units',
                header: 'Units Sold',
                sortable: true,
                align: 'right',
                render: (row) => <span className="font-semibold text-slate-800">{row.units}</span>
              },
              {
                key: 'revenue',
                header: 'Net Revenue',
                sortable: true,
                align: 'right',
                render: (row) => <span className="font-bold text-slate-900">${row.revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              },
              {
                key: 'profit',
                header: 'Gross Profit',
                sortable: true,
                align: 'right',
                render: (row) => <span className="font-semibold text-emerald-700">${row.profit.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              },
              {
                key: 'marginPct',
                header: 'Margin %',
                sortable: true,
                align: 'right',
                render: (row) => (
                  <Badge variant={row.marginPct > 50 ? 'success' : 'neutral'} size="sm">
                    {row.marginPct}%
                  </Badge>
                )
              }
            ]}
          />
        </div>
      </div>
    </div>
  );
};
