import React, { useMemo, useState } from 'react';
import {
  DollarSign,
  Tag,
  TrendingUp,
  Percent,
  Layers,
  ShoppingBag
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  AreaChart,
  Area,
  ScatterChart,
  Scatter
} from 'recharts';
import { useDataset } from '../context/DatasetContext';
import { useFilters } from '../context/FilterContext';
import {
  calculateRetailKPIs,
  calculateMonthlyTrends,
  calculateChannelPerformance,
  calculateRegionalPerformance
} from '../utils/retailCalculations';
import { RetailTransaction } from '../types';
import { KPICard } from '../components/common/KPICard';
import { ChartCard } from '../components/common/ChartCard';
import { FilterBar } from '../components/common/FilterBar';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

export const SalesAnalysis: React.FC = () => {
  const {
    transactions,
    isLoadingRetail,
    retailLoadError,
    reloadRetailData
  } = useDataset();
  const { filterTransactions } = useFilters();
  const [viewMetric, setViewMetric] = useState<'revenue' | 'profit'>('revenue');

  const filteredTx = useMemo(() => filterTransactions(transactions), [transactions, filterTransactions]);
  const kpis = useMemo(() => calculateRetailKPIs(filteredTx), [filteredTx]);

  // Aggregate stats from pure dynamic calculations
  const stats = useMemo(() => {
    return {
      grossSales: kpis.grossSales,
      discounts: kpis.totalDiscounts,
      netSales: kpis.totalSales,
      cogs: kpis.totalSales - kpis.totalProfit,
      grossProfit: kpis.totalProfit,
      totalUnits: kpis.totalQuantity,
      discountRate: kpis.discountRate,
      marginPct: kpis.profitMargin,
      avgBasketSize: kpis.avgBasketSize
    };
  }, [kpis]);

  // Monthly timeline trend
  const timelineData = useMemo(() => {
    return calculateMonthlyTrends(filteredTx).map((m) => ({
      date: m.label,
      revenue: m.revenue,
      profit: m.profit,
      discount: m.discount,
      orders: m.orders,
      units: m.units
    }));
  }, [filteredTx]);

  // Channel Breakdown with pure metrics
  const channelBreakdown = useMemo(() => {
    return calculateChannelPerformance(filteredTx);
  }, [filteredTx]);

  // Regional Sales Data
  const regionalData = useMemo(() => {
    return calculateRegionalPerformance(filteredTx);
  }, [filteredTx]);

  // Scatter plot: Discount % vs Margin %
  const discountScatterData = useMemo(() => {
    return filteredTx.slice(0, 100).map((t) => ({
      discount: Math.round(t.discountPct * 100),
      margin: t.marginPct,
      product: t.productName,
      category: t.category,
      revenue: t.netRevenue
    }));
  }, [filteredTx]);

  if (isLoadingRetail) {
    return (
      <div id="sales-dashboard-loading" className="p-6">
        <LoadingState message="Loading Sales & Revenue Intelligence from real datasets..." />
      </div>
    );
  }

  if (retailLoadError) {
    return (
      <div id="sales-dashboard-error" className="p-6">
        <ErrorState
          title="Failed to Load Sales Analytics"
          message={retailLoadError}
          onRetry={reloadRetailData}
        />
      </div>
    );
  }

  return (
    <div id="sales-analysis-page" className="space-y-6">
      <PageHeader
        id="sales-page-header"
        title="Sales & Revenue Intelligence"
        description="Deep-dive into omnichannel revenue streams, promotional discount impact, and regional commercial velocity."
        badge={<Badge variant="primary">Commercial Analytics</Badge>}
      />

      <FilterBar id="sales-filter-bar" />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-6 gap-4">
        <KPICard
          id="sales-kpi-net"
          title="Gross Sales"
          value={`$${stats.grossSales.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          change={12.4}
          changePeriod="YoY Trend"
          subtitle="Topline gross merchandise volume"
          icon={DollarSign}
        />
        <KPICard
          id="sales-kpi-discounts"
          title="Total Discounts"
          value={`$${stats.discounts.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          change={-3.1}
          changePeriod="Promotion Spend"
          subtitle="Customer price concessions"
          icon={Tag}
          variant="warning"
        />
        <KPICard
          id="sales-kpi-discount-rate"
          title="Effective Discount"
          value={`${stats.discountRate.toFixed(2)}%`}
          subtitle="Promotional margin erosion rate"
          icon={Percent}
        />
        <KPICard
          id="sales-kpi-gross-margin"
          title="Gross Margin"
          value={`${stats.marginPct.toFixed(2)}%`}
          change={1.9}
          changePeriod="vs benchmark"
          target="50.0%"
          icon={TrendingUp}
          variant="success"
        />
        <KPICard
          id="sales-kpi-units"
          title="Units Sold"
          value={stats.totalUnits.toLocaleString()}
          change={6.2}
          changePeriod="Volume growth"
          subtitle="Aggregate merchandise units"
          icon={ShoppingBag}
        />
        <KPICard
          id="sales-kpi-basket"
          title="Avg Basket Size"
          value={`${stats.avgBasketSize.toFixed(2)} items`}
          subtitle="Units per checkout event"
          icon={Layers}
        />
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Area Chart */}
        <div className="lg:col-span-2">
          <ChartCard
            id="chart-sales-velocity"
            title="Sales Velocity & Net Contribution"
            subtitle="Cumulative net sales trajectory over time"
            actions={
              <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg text-xs font-semibold">
                <button
                  onClick={() => setViewMetric('revenue')}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    viewMetric === 'revenue' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600'
                  }`}
                >
                  Revenue
                </button>
                <button
                  onClick={() => setViewMetric('profit')}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    viewMetric === 'profit' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600'
                  }`}
                >
                  Gross Profit
                </button>
              </div>
            }
          >
            <div className="h-72 w-full">
              {timelineData.length === 0 ? (
                <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                  No timeline records match the active filter criteria.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={timelineData} margin={{ top: 10, right: 15, left: 10, bottom: 0 }}>
                    <defs>
                      <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
                      </linearGradient>
                      <linearGradient id="profitGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                    <XAxis dataKey="date" stroke="#94A3B8" fontSize={11} tickLine={false} />
                    <YAxis
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      tickFormatter={(v) => `$${v >= 1000000 ? (v / 1000000).toFixed(1) + 'M' : (v / 1000).toFixed(0) + 'k'}`}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                      formatter={(val: any) => [`$${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, viewMetric === 'revenue' ? 'Net Revenue' : 'Gross Profit']}
                    />
                    <Area
                      type="monotone"
                      dataKey={viewMetric}
                      stroke={viewMetric === 'revenue' ? '#3B82F6' : '#10B981'}
                      strokeWidth={2}
                      fillOpacity={1}
                      fill={`url(#${viewMetric === 'revenue' ? 'salesGradient' : 'profitGradient'})`}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>
          </ChartCard>
        </div>

        {/* Regional Distribution */}
        <div className="lg:col-span-1">
          <ChartCard
            id="chart-regional-sales"
            title="Regional Sales Distribution"
            subtitle="Commercial contribution by geographic territory"
          >
            <div className="h-72 w-full">
              {regionalData.length === 0 ? (
                <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                  No regional records match the active filter criteria.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={regionalData} margin={{ top: 10, right: 15, left: 10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                    <XAxis dataKey="region" stroke="#94A3B8" fontSize={11} tickLine={false} />
                    <YAxis
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      tickFormatter={(v) => `$${v >= 1000000 ? (v / 1000000).toFixed(1) + 'M' : (v / 1000).toFixed(0) + 'k'}`}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                      formatter={(val: any) => [`$${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 'Net Revenue']}
                    />
                    <Bar dataKey="revenue" fill="#6366F1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </ChartCard>
        </div>
      </div>

      {/* Channel Comparison & Discount Sensitivity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Channel Table / Chart */}
        <ChartCard
          id="chart-channel-margin-comparison"
          title="Channel Margin Health"
          subtitle="Net sales revenue and gross profit margin across sales channels"
        >
          <div className="h-64 w-full">
            {channelBreakdown.length === 0 ? (
              <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                No channel records match the active filter criteria.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={channelBreakdown} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis dataKey="channel" stroke="#94A3B8" fontSize={11} tickLine={false} />
                  <YAxis
                    stroke="#94A3B8"
                    fontSize={11}
                    tickLine={false}
                    tickFormatter={(v) => `$${v >= 1000000 ? (v / 1000000).toFixed(1) + 'M' : (v / 1000).toFixed(0) + 'k'}`}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                    formatter={(val: any, name: any) => [`$${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, name]}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Bar dataKey="revenue" name="Net Revenue" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="profit" name="Gross Profit" fill="#10B981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </ChartCard>

        {/* Discount vs Margin Scatter Plot */}
        <ChartCard
          id="chart-discount-margin-scatter"
          title="Discount vs Realized Margin Analysis"
          subtitle="Observation points showing discount depth impact on unit gross profit margin"
        >
          <div className="h-64 w-full">
            {discountScatterData.length === 0 ? (
              <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                No transaction scatter data available for the active filters.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                  <XAxis
                    type="number"
                    dataKey="discount"
                    name="Discount %"
                    unit="%"
                    stroke="#94A3B8"
                    fontSize={11}
                    tickLine={false}
                  />
                  <YAxis
                    type="number"
                    dataKey="margin"
                    name="Margin %"
                    unit="%"
                    stroke="#94A3B8"
                    fontSize={11}
                    tickLine={false}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                    formatter={(value: any, name: any) => [`${value}%`, name]}
                  />
                  <Scatter name="Transactions" data={discountScatterData} fill="#EC4899" opacity={0.65} />
                </ScatterChart>
              </ResponsiveContainer>
            )}
          </div>
        </ChartCard>
      </div>

      {/* Transactions Data Table */}
      <DataTable<RetailTransaction>
        id="table-sales-transactions"
        title="Transaction Ledger"
        subtitle="Recent point-of-sale and online transactions with realized margin"
        data={filteredTx}
        columns={[
          {
            key: 'orderId',
            header: 'Order ID',
            sortable: true,
            render: (row) => <span className="font-mono font-semibold text-slate-900">{row.orderId}</span>
          },
          {
            key: 'date',
            header: 'Date',
            sortable: true,
            render: (row) => <span className="text-slate-600">{row.date}</span>
          },
          {
            key: 'customerName',
            header: 'Customer',
            sortable: true,
            render: (row) => (
              <div>
                <span className="font-medium text-slate-800 block">{row.customerName}</span>
                <span className="text-[11px] text-slate-400">{row.storeLocation}</span>
              </div>
            )
          },
          {
            key: 'channel',
            header: 'Channel',
            sortable: true,
            render: (row) => (
              <Badge
                variant={
                  row.channel === 'Online'
                    ? 'primary'
                    : row.channel === 'Retail Store'
                    ? 'success'
                    : row.channel === 'Marketplace'
                    ? 'purple'
                    : 'warning'
                }
                size="sm"
              >
                {row.channel}
              </Badge>
            )
          },
          {
            key: 'productName',
            header: 'Product',
            sortable: true,
            render: (row) => (
              <div className="max-w-[180px] truncate" title={row.productName}>
                <span className="font-medium text-slate-800 block truncate">{row.productName}</span>
                <span className="text-[10px] text-slate-400 font-mono">{row.sku}</span>
              </div>
            )
          },
          {
            key: 'quantity',
            header: 'Qty',
            sortable: true,
            align: 'center'
          },
          {
            key: 'discountPct',
            header: 'Discount',
            sortable: true,
            align: 'right',
            render: (row) => (
              <span className={row.discountPct > 0 ? 'text-amber-600 font-medium' : 'text-slate-400'}>
                {Math.round(row.discountPct * 100)}%
              </span>
            )
          },
          {
            key: 'netRevenue',
            header: 'Net Revenue',
            sortable: true,
            align: 'right',
            render: (row) => (
              <span className="font-bold text-slate-900">
                ${row.netRevenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            )
          },
          {
            key: 'marginPct',
            header: 'Margin',
            sortable: true,
            align: 'right',
            render: (row) => (
              <span
                className={`font-semibold ${
                  row.marginPct > 55
                    ? 'text-emerald-600'
                    : row.marginPct > 40
                    ? 'text-blue-600'
                    : 'text-amber-600'
                }`}
              >
                {row.marginPct}%
              </span>
            )
          }
        ]}
      />
    </div>
  );
};
