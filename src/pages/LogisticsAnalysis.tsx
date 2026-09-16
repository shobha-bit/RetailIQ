import React, { useMemo } from 'react';
import {
  Truck,
  CheckCircle2,
  Clock,
  DollarSign,
  AlertTriangle,
  MapPin
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
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { useDataset } from '../context/DatasetContext';
import { useFilters } from '../context/FilterContext';
import {
  calculateRetailKPIs,
  calculateCarrierScorecard
} from '../utils/retailCalculations';
import { KPICard } from '../components/common/KPICard';
import { ChartCard } from '../components/common/ChartCard';
import { FilterBar } from '../components/common/FilterBar';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

const STATUS_COLORS = {
  Delivered: '#10B981',
  'In Transit': '#3B82F6',
  Delayed: '#F59E0B',
  Cancelled: '#EF4444'
};

export const LogisticsAnalysis: React.FC = () => {
  const {
    transactions,
    isLoadingRetail,
    retailLoadError,
    reloadRetailData
  } = useDataset();
  const { filterTransactions } = useFilters();

  const filteredTx = useMemo(() => filterTransactions(transactions), [transactions, filterTransactions]);
  const kpis = useMemo(() => calculateRetailKPIs(filteredTx), [filteredTx]);
  const carrierChartData = useMemo(() => calculateCarrierScorecard(filteredTx), [filteredTx]);

  // Aggregate stats purely derived from transactional fulfillment data
  const stats = useMemo(() => {
    const total = filteredTx.length;
    const delivered = filteredTx.filter((t) => t.status === 'Delivered').length;
    const delayed = filteredTx.filter((t) => t.status === 'Delayed').length;
    const inTransit = filteredTx.filter((t) => t.status === 'In Transit').length;
    const avgCost = total > 0 ? Math.round((filteredTx.reduce((acc, t) => acc + (t.shippingCost || 0), 0) / total) * 100) / 100 : 0;
    const avgDeliveryDays = kpis.avgDeliveryDays;
    const otdRate = kpis.onTimeDeliveryRate;

    return {
      total,
      delivered,
      delayed,
      inTransit,
      avgCost,
      avgDeliveryDays,
      otdRate
    };
  }, [filteredTx, kpis]);

  // Status breakdown
  const statusData = useMemo(() => {
    return [
      { name: 'Delivered', value: stats.delivered },
      { name: 'In Transit', value: stats.inTransit },
      { name: 'Delayed', value: stats.delayed }
    ];
  }, [stats]);

  // Dynamic Carrier Partner Scorecard data
  const carrierScorecard = useMemo(() => {
    return carrierChartData.map((c) => ({
      carrier: c.carrier,
      totalShipments: c.totalShipments,
      onTimeDeliveries: c.delivered,
      delayedShipments: c.delayed,
      onTimeRate: c.onTimeRate,
      avgTransitDays: c.avgTransitDays,
      avgShippingCost: c.avgShippingCost,
      claimRate: Math.round((c.delayed / (c.totalShipments || 1)) * 10) / 10
    }));
  }, [carrierChartData]);

  if (isLoadingRetail) {
    return (
      <div id="logistics-dashboard-loading" className="p-6">
        <LoadingState message="Loading carrier fulfillment metrics from real transportation datasets..." />
      </div>
    );
  }

  if (retailLoadError) {
    return (
      <div id="logistics-dashboard-error" className="p-6">
        <ErrorState
          title="Failed to Load Logistics Intelligence"
          message={retailLoadError}
          onRetry={reloadRetailData}
        />
      </div>
    );
  }

  return (
    <div id="logistics-analysis-page" className="space-y-6">
      <PageHeader
        id="logistics-page-header"
        title="Logistics & Carrier Performance"
        description="Fulfillment tracking, carrier SLA compliance, transit time benchmarks, and shipping expenditure analysis."
        badge={<Badge variant="info" dot>Carrier Telemetry</Badge>}
      />

      <FilterBar id="logistics-filter-bar" />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        <KPICard
          id="logistics-kpi-total"
          title="Parcels Dispatched"
          value={stats.total.toLocaleString()}
          subtitle="Orders in fulfillment network"
          icon={Truck}
        />
        <KPICard
          id="logistics-kpi-otd"
          title="On-Time Delivery Rate"
          value={`${stats.otdRate.toFixed(1)}%`}
          target="95.0%"
          icon={CheckCircle2}
          variant="success"
        />
        <KPICard
          id="logistics-kpi-transit"
          title="Avg Transit Time"
          value={`${stats.avgDeliveryDays.toFixed(2)} days`}
          subtitle="Mean order dispatch to arrival"
          icon={Clock}
        />
        <KPICard
          id="logistics-kpi-cost"
          title="Avg Shipping Cost"
          value={`$${stats.avgCost.toFixed(2)}`}
          subtitle="Cost per parcel"
          icon={DollarSign}
        />
        <KPICard
          id="logistics-kpi-delayed"
          title="Delayed Shipments"
          value={stats.delayed.toLocaleString()}
          subtitle="Requiring tracking intervention"
          icon={AlertTriangle}
          variant={stats.delayed > 10 ? 'warning' : 'default'}
        />
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Carrier On-Time Rate Bar Chart */}
        <div className="lg:col-span-2">
          <ChartCard
            id="chart-carrier-performance"
            title="Carrier SLA Compliance (On-Time Delivery %)"
            subtitle="Comparing carrier reliability and average transit duration"
          >
            <div className="h-72 w-full">
              {carrierChartData.length === 0 ? (
                <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                  No carrier fulfillment records match the active filters.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={carrierChartData} margin={{ top: 10, right: 15, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                    <XAxis dataKey="carrier" stroke="#94A3B8" fontSize={11} tickLine={false} />
                    <YAxis
                      domain={[80, 100]}
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      tickFormatter={(v) => `${v}%`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0F172A',
                        border: 'none',
                        borderRadius: '8px',
                        color: '#fff',
                        fontSize: '12px'
                      }}
                      formatter={(val: any) => [`${Number(val).toFixed(1)}%`, 'On-Time Rate']}
                    />
                    <Bar dataKey="onTimeRate" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </ChartCard>
        </div>

        {/* Delivery Status Donut */}
        <div className="lg:col-span-1">
          <ChartCard
            id="chart-shipment-status"
            title="Fulfillment Status Breakdown"
            subtitle="Shipments categorized by real-time delivery state"
          >
            <div className="h-72 w-full flex flex-col items-center justify-center">
              {statusData.every((d) => d.value === 0) ? (
                <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                  No shipment records to display.
                </div>
              ) : (
                <>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={statusData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {statusData.map((entry) => (
                          <Cell
                            key={entry.name}
                            fill={STATUS_COLORS[entry.name as keyof typeof STATUS_COLORS] || '#64748B'}
                          />
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
                        formatter={(val: any) => [`${Number(val).toLocaleString()} orders`, 'Volume']}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="w-full grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-slate-100 text-xs">
                    {statusData.map((entry) => (
                      <div key={entry.name} className="flex items-center gap-1.5 min-w-0">
                        <span
                          className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                          style={{ backgroundColor: STATUS_COLORS[entry.name as keyof typeof STATUS_COLORS] || '#64748B' }}
                        />
                        <span className="text-slate-600 truncate">{entry.name}:</span>
                        <span className="font-bold text-slate-900 ml-auto whitespace-nowrap">
                          {entry.value.toLocaleString()}
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

      {/* Carrier Scorecard Table */}
      <DataTable
        id="table-carrier-scorecard"
        title="Carrier Partner Scorecard"
        subtitle="Performance KPIs, SLA compliance rates, and average cost per delivery"
        data={carrierScorecard}
        columns={[
          {
            key: 'carrier',
            header: 'Carrier Partner',
            sortable: true,
            render: (row) => <span className="font-bold text-slate-900">{row.carrier}</span>
          },
          {
            key: 'totalShipments',
            header: 'Shipments Handled',
            sortable: true,
            align: 'right',
            render: (row) => <span className="font-semibold text-slate-800">{row.totalShipments.toLocaleString()}</span>
          },
          {
            key: 'onTimeDeliveries',
            header: 'On-Time Units',
            sortable: true,
            align: 'right',
            render: (row) => <span className="text-slate-700 font-medium">{row.onTimeDeliveries.toLocaleString()}</span>
          },
          {
            key: 'onTimeRate',
            header: 'OTD Rate',
            sortable: true,
            align: 'right',
            render: (row) => (
              <Badge
                variant={row.onTimeRate >= 94 ? 'success' : row.onTimeRate >= 90 ? 'primary' : 'warning'}
                size="sm"
              >
                {row.onTimeRate.toFixed(1)}%
              </Badge>
            )
          },
          {
            key: 'avgTransitDays',
            header: 'Avg Transit',
            sortable: true,
            align: 'right',
            render: (row) => <span className="text-slate-700 font-medium">{row.avgTransitDays.toFixed(2)} days</span>
          },
          {
            key: 'avgShippingCost',
            header: 'Cost / Parcel',
            sortable: true,
            align: 'right',
            render: (row) => (
              <span className="font-semibold text-slate-900">${row.avgShippingCost.toFixed(2)}</span>
            )
          },
          {
            key: 'claimRate',
            header: 'Damage / Loss Claim %',
            sortable: true,
            align: 'right',
            render: (row) => (
              <span
                className={`font-semibold ${
                  row.claimRate < 1.0 ? 'text-emerald-600' : 'text-amber-600'
                }`}
              >
                {row.claimRate.toFixed(1)}%
              </span>
            )
          }
        ]}
      />
    </div>
  );
};
