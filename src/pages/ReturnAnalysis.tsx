import React, { useMemo } from 'react';
import {
  RotateCcw,
  DollarSign,
  AlertOctagon,
  Percent,
  CheckCircle2,
  ShieldAlert,
  ArrowRight,
  Package,
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
  Cell,
  PieChart,
  Pie
} from 'recharts';
import { useDataset } from '../context/DatasetContext';
import { useFilters } from '../context/FilterContext';
import {
  calculateRetailKPIs,
  calculateCategoryPerformance,
  calculateReturnReasons
} from '../utils/retailCalculations';
import { KPICard } from '../components/common/KPICard';
import { ChartCard } from '../components/common/ChartCard';
import { FilterBar } from '../components/common/FilterBar';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

const REASON_COLORS: Record<string, string> = {
  'Late Delivery': '#F59E0B',
  'Defective Product': '#EF4444',
  'Customer Changed Mind': '#8B5CF6',
  'Wrong Item': '#EC4899',
  'Damaged Product': '#F97316',
  'Other': '#64748B'
};

export const ReturnAnalysis: React.FC = () => {
  const {
    transactions,
    isLoadingRetail,
    retailLoadError,
    reloadRetailData
  } = useDataset();
  const { filterTransactions } = useFilters();

  const filteredTx = useMemo(() => filterTransactions(transactions), [transactions, filterTransactions]);
  const kpis = useMemo(() => calculateRetailKPIs(filteredTx), [filteredTx]);

  // Category return breakdown dynamically derived
  const categoryReturnData = useMemo(() => {
    return calculateCategoryPerformance(filteredTx)
      .map((c) => ({
        category: c.category,
        returnRate: c.returnRate,
        returned: c.returns,
        total: c.orders
      }))
      .sort((a, b) => b.returnRate - a.returnRate);
  }, [filteredTx]);

  const highestCat = categoryReturnData.length > 0 ? categoryReturnData[0].category : 'N/A';
  const highestCatRate = categoryReturnData.length > 0 ? categoryReturnData[0].returnRate : 0;

  // Return calculations purely dynamic and rigorously preserving definitions
  const stats = useMemo(() => {
    const returnedTx = filteredTx.filter((t) => t.isReturned);
    const totalReturnRecords = returnedTx.length;
    const uniqueReturnedProducts = new Set(returnedTx.map((t) => t.sku).filter(Boolean)).size;
    const distinctReturnedOrders = new Set(returnedTx.map((t) => t.orderId).filter(Boolean)).size;
    const returnRate = kpis.returnRate;
    const totalReturnCost = kpis.totalReturnCost;
    const totalRefunds = returnedTx.reduce((acc, t) => acc + (t.returnCost || 0), 0);

    return {
      totalOrders: kpis.totalOrders,
      totalReturnRecords,
      uniqueReturnedProducts,
      distinctReturnedOrders,
      returnRate,
      totalReturnCost,
      totalRefunds,
      highestCat,
      highestCatRate
    };
  }, [filteredTx, kpis, highestCat, highestCatRate]);

  // Return reasons breakdown purely dynamic
  const reasonData = useMemo(() => {
    return calculateReturnReasons(filteredTx);
  }, [filteredTx]);

  // Product return register
  const productReturns = useMemo(() => {
    const pMap: Record<string, { sku: string; name: string; category: string; totalSold: number; returned: number; returnCost: number; reasons: Record<string, number> }> = {};
    filteredTx.forEach((t) => {
      const p = pMap[t.sku] || {
        sku: t.sku,
        name: t.productName,
        category: t.category,
        totalSold: 0,
        returned: 0,
        returnCost: 0,
        reasons: {}
      };
      p.totalSold += t.quantity;
      if (t.isReturned) {
        p.returned += 1;
        p.returnCost += t.returnCost + t.netRevenue;
        p.reasons[t.returnReason] = (p.reasons[t.returnReason] || 0) + 1;
      }
      pMap[t.sku] = p;
    });

    return Object.values(pMap)
      .map((p) => {
        let topReason = 'None';
        let maxR = 0;
        Object.entries(p.reasons).forEach(([r, count]) => {
          if (count > maxR) {
            maxR = count;
            topReason = r;
          }
        });

        const rate = p.totalSold > 0 ? Math.round((p.returned / p.totalSold) * 1000) / 10 : 0;
        let recommendation = 'Standard Quality Monitoring';
        if (topReason === 'Late Delivery') recommendation = 'Shift SKU to Priority Expedited Carrier Hub';
        else if (topReason === 'Defective Product') recommendation = 'Audit Vendor QC & Manufacturing Tolerances';
        else if (topReason === 'Customer Changed Mind') recommendation = 'Calibrate Sizing & Product Specs Guide';
        else if (topReason === 'Wrong Item') recommendation = 'Barcode Pick-and-Pack Verification Scan';
        else if (topReason === 'Damaged Product') recommendation = 'Upgrade Shock-Absorbing Transit Packaging';

        return {
          sku: p.sku,
          name: p.name,
          category: p.category,
          totalSold: p.totalSold,
          returned: p.returned,
          returnRate: rate,
          returnCost: Math.round(p.returnCost),
          topReason,
          recommendation
        };
      })
      .sort((a, b) => b.returnRate - a.returnRate);
  }, [filteredTx]);

  if (isLoadingRetail) {
    return (
      <div id="return-dashboard-loading" className="p-6">
        <LoadingState message="Calculating return diagnostics and reverse logistics costs from real returns data..." />
      </div>
    );
  }

  if (retailLoadError) {
    return (
      <div id="return-dashboard-error" className="p-6">
        <ErrorState
          title="Failed to Load Return Diagnostics"
          message={retailLoadError}
          onRetry={reloadRetailData}
        />
      </div>
    );
  }

  return (
    <div id="return-analysis-page" className="space-y-6">
      <PageHeader
        id="return-page-header"
        title="Return & Refund Intelligence"
        description="Root-cause diagnostic on merchandise returns, reverse logistics expenditure, and defect mitigation playbooks."
        badge={<Badge variant="danger" dot>Reverse Logistics Diagnostics</Badge>}
      />

      <FilterBar id="return-filter-bar" />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <KPICard
          id="return-kpi-rate"
          title="Return Rate"
          value={`${stats.returnRate.toFixed(2)}%`}
          subtitle="Total return frequency"
          icon={Percent}
          variant={stats.returnRate > 12 ? 'warning' : 'default'}
        />
        <KPICard
          id="return-kpi-count"
          title="Total Returns"
          value={stats.totalReturnRecords.toLocaleString()}
          subtitle="Return records logged"
          icon={RotateCcw}
        />
        <KPICard
          id="return-kpi-products"
          title="Returned Products"
          value={stats.uniqueReturnedProducts.toLocaleString()}
          subtitle="Unique catalog SKUs"
          icon={Package}
        />
        <KPICard
          id="return-kpi-orders"
          title="Distinct Returned Orders"
          value={stats.distinctReturnedOrders.toLocaleString()}
          subtitle="Distinct order IDs affected"
          icon={ShoppingBag}
        />
        <KPICard
          id="return-kpi-cost"
          title="Financial Cost Impact"
          value={`$${stats.totalReturnCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          subtitle={`Includes $${Math.round(stats.totalRefunds).toLocaleString()} direct refunds`}
          icon={DollarSign}
          variant="accent"
        />
        <KPICard
          id="return-kpi-highest-cat"
          title="High-Return Category"
          value={stats.highestCat}
          subtitle={`${stats.highestCatRate.toFixed(1)}% return frequency`}
          icon={ShieldAlert}
        />
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Return Rate Bar Chart */}
        <ChartCard
          id="chart-category-returns"
          title="Return Rate by Merchandise Department"
          subtitle="Percentage of dispatched orders returned by product vertical"
        >
          <div className="h-72 w-full">
            {categoryReturnData.length === 0 ? (
              <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                No return records match the active filters.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={categoryReturnData}
                  layout="vertical"
                  margin={{ top: 10, right: 25, left: 10, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
                  <XAxis
                    type="number"
                    stroke="#94A3B8"
                    fontSize={11}
                    tickLine={false}
                    tickFormatter={(v) => `${v}%`}
                  />
                  <YAxis
                    type="category"
                    dataKey="category"
                    stroke="#94A3B8"
                    fontSize={11}
                    tickLine={false}
                    width={110}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0F172A',
                      border: 'none',
                      borderRadius: '8px',
                      color: '#fff',
                      fontSize: '12px'
                    }}
                    formatter={(val: any, _name: any, item: any) => [
                      `${Number(val).toFixed(2)}% (${item.payload.returned.toLocaleString()} returned of ${item.payload.total.toLocaleString()})`,
                      'Return Rate'
                    ]}
                  />
                  <Bar dataKey="returnRate" radius={[0, 4, 4, 0]}>
                    {categoryReturnData.map((entry) => (
                      <Cell
                        key={entry.category}
                        fill={entry.returnRate > 15 ? '#EF4444' : entry.returnRate > 8 ? '#F59E0B' : '#3B82F6'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </ChartCard>

        {/* Return Reasons Donut */}
        <ChartCard
          id="chart-return-reasons"
          title="Root Cause Classification"
          subtitle="Customer reported justifications for merchandise return"
        >
          <div className="h-72 w-full flex flex-col items-center justify-center">
            {reasonData.length === 0 ? (
              <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                No return reason records to display.
              </div>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={reasonData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {reasonData.map((entry) => (
                        <Cell key={entry.name} fill={REASON_COLORS[entry.name] || '#64748B'} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0F172A',
                        border: 'none',
                        borderRadius: '8px',
                        color: '#fff',
                        fontSize: '12px'
                      }}
                      formatter={(val: any, _name: any, item: any) => [
                        `${Number(val).toLocaleString()} cases (${item.payload.pct}%)`,
                        'Occurrences'
                      ]}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="w-full grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-slate-100 text-xs">
                  {reasonData.map((entry) => (
                    <div key={entry.name} className="flex items-center gap-1.5 min-w-0">
                      <span
                        className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                        style={{ backgroundColor: REASON_COLORS[entry.name] || '#64748B' }}
                      />
                      <span className="text-slate-600 truncate" title={entry.name}>
                        {entry.name}:
                      </span>
                      <span className="font-bold text-slate-900 ml-auto whitespace-nowrap">
                        {entry.value.toLocaleString()} ({entry.pct}%)
                      </span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </ChartCard>
      </div>

      {/* Return Register Table */}
      <DataTable<typeof productReturns[0]>
        id="table-product-returns"
        title="SKU Return Rate & Corrective Action Playbook"
        subtitle="Identified high-return products and prescriptive operational mitigations"
        data={productReturns}
        columns={[
          {
            key: 'sku',
            header: 'SKU',
            sortable: true,
            render: (row) => <span className="font-mono font-semibold text-slate-800 text-xs">{row.sku}</span>
          },
          {
            key: 'name',
            header: 'Product',
            sortable: true,
            render: (row) => (
              <div className="max-w-[240px] truncate" title={row.name}>
                <span className="font-medium text-slate-900 block truncate">{row.name}</span>
                <span className="text-[11px] text-slate-400">{row.category}</span>
              </div>
            )
          },
          {
            key: 'totalSold',
            header: 'Sold',
            sortable: true,
            align: 'right',
            render: (row) => <span className="text-slate-700 font-medium">{row.totalSold.toLocaleString()}</span>
          },
          {
            key: 'returned',
            header: 'Returned',
            sortable: true,
            align: 'right',
            render: (row) => <span className="text-slate-700 font-medium">{row.returned.toLocaleString()}</span>
          },
          {
            key: 'returnRate',
            header: 'Return Rate',
            sortable: true,
            align: 'right',
            render: (row) => (
              <Badge
                variant={row.returnRate > 15 ? 'danger' : row.returnRate > 8 ? 'warning' : 'success'}
                size="sm"
              >
                {row.returnRate.toFixed(1)}%
              </Badge>
            )
          },
          {
            key: 'returnCost',
            header: 'Reverse Cost',
            sortable: true,
            align: 'right',
            render: (row) => (
              <span className="font-semibold text-slate-900">${row.returnCost.toLocaleString()}</span>
            )
          },
          {
            key: 'topReason',
            header: 'Top Reason',
            sortable: true,
            render: (row) => (
              <span className="text-slate-700 font-medium text-xs whitespace-nowrap">{row.topReason}</span>
            )
          },
          {
            key: 'recommendation',
            header: 'Prescriptive Action',
            render: (row) => (
              <div className="flex items-center gap-1.5 text-xs text-blue-700 font-medium max-w-[260px]">
                <ArrowRight className="w-3.5 h-3.5 flex-shrink-0 text-blue-500" />
                <span className="truncate" title={row.recommendation}>{row.recommendation}</span>
              </div>
            )
          }
        ]}
      />
    </div>
  );
};
