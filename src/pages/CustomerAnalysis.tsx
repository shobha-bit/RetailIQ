import React, { useMemo, useState } from 'react';
import {
  Users,
  Award,
  AlertTriangle,
  HeartHandshake,
  TrendingDown,
  Mail,
  CheckCircle2
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
  Pie,
  ScatterChart,
  Scatter,
  ZAxis
} from 'recharts';
import { useDataset } from '../context/DatasetContext';
import { CustomerRFM, RFMSegmentName } from '../types';
import { KPICard } from '../components/common/KPICard';
import { ChartCard } from '../components/common/ChartCard';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

const SEGMENT_COLORS: Record<RFMSegmentName, string> = {
  Champions: '#10B981',
  'Loyal Customers': '#3B82F6',
  'Potential Loyalists': '#8B5CF6',
  'At Risk': '#F59E0B',
  Hibernating: '#EC4899',
  Lost: '#64748B'
};

export const CustomerAnalysis: React.FC = () => {
  const { rfm, isLoadingRetail, retailLoadError, reloadRetailData } = useDataset();
  const [selectedSegment, setSelectedSegment] = useState<string>('all');
  const [targetedCustomerId, setTargetedCustomerId] = useState<string | null>(null);

  // Filtered RFM list
  const filteredRFM = useMemo(() => {
    if (selectedSegment === 'all') return rfm;
    return rfm.filter((c) => c.segment === selectedSegment);
  }, [rfm, selectedSegment]);

  // Aggregate stats dynamically derived from RFM segmentation
  const stats = useMemo(() => {
    const totalCustomers = rfm.length;
    const champions = rfm.filter((c) => c.segment === 'Champions');
    const atRisk = rfm.filter((c) => c.segment === 'At Risk' || c.segment === 'Hibernating');
    const totalSpend = rfm.reduce((acc, c) => acc + c.monetaryValue, 0);
    const avgCLV = totalCustomers > 0 ? Math.round(totalSpend / totalCustomers) : 0;
    const championsSpend = champions.reduce((acc, c) => acc + c.monetaryValue, 0);
    const revenueAtRisk = atRisk.reduce((acc, c) => acc + c.monetaryValue, 0);

    return {
      totalCustomers,
      championsCount: champions.length,
      championsSpend,
      atRiskCount: atRisk.length,
      revenueAtRisk,
      avgCLV
    };
  }, [rfm]);

  // Segment breakdown dynamically derived from RFM
  const segmentData = useMemo(() => {
    const segments: RFMSegmentName[] = [
      'Champions',
      'Loyal Customers',
      'Potential Loyalists',
      'At Risk',
      'Hibernating',
      'Lost'
    ];

    return segments.map((seg) => {
      const matched = rfm.filter((c) => c.segment === seg);
      const count = matched.length;
      const spend = Math.round(matched.reduce((acc, c) => acc + c.monetaryValue, 0));
      const avgSpend = count > 0 ? Math.round(spend / count) : 0;
      return {
        segment: seg,
        count,
        spend,
        avgSpend
      };
    });
  }, [rfm]);

  // Scatter data: Recency (x) vs Monetary (y) vs Frequency (z)
  const scatterData = useMemo(() => {
    return rfm.map((c) => ({
      name: c.customerName,
      recency: c.recencyDays,
      monetary: c.monetaryValue,
      frequency: c.frequency,
      segment: c.segment
    }));
  }, [rfm]);

  const handleTriggerReengagement = (customer: CustomerRFM) => {
    setTargetedCustomerId(customer.customerId);
    setTimeout(() => {
      setTargetedCustomerId(null);
    }, 2800);
  };

  if (isLoadingRetail) {
    return (
      <div id="customer-dashboard-loading" className="p-6">
        <LoadingState message="Calculating customer RFM segmentation from real customer transactions..." />
      </div>
    );
  }

  if (retailLoadError) {
    return (
      <div id="customer-dashboard-error" className="p-6">
        <ErrorState
          title="Failed to Load Customer Intelligence"
          message={retailLoadError}
          onRetry={reloadRetailData}
        />
      </div>
    );
  }

  return (
    <div id="customer-analysis-page" className="space-y-6">
      <PageHeader
        id="customer-page-header"
        title="Customer Intelligence & RFM Segmentation"
        description="Behavioral clustering based on Recency, Frequency, and Monetary quintiles to optimize retention and lifetime value (CLV)."
        badge={<Badge variant="purple" dot>Behavioral ML Matrix</Badge>}
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-5 gap-4">
        <KPICard
          id="rfm-kpi-total"
          title="Active Customer Base"
          value={stats.totalCustomers.toLocaleString()}
          subtitle="Unique retail accounts verified"
          icon={Users}
        />
        <KPICard
          id="rfm-kpi-champions"
          title="Champions Cohort"
          value={stats.championsCount.toLocaleString()}
          subtitle={`$${stats.championsSpend.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} revenue contribution`}
          icon={Award}
          variant="success"
        />
        <KPICard
          id="rfm-kpi-clv"
          title="Average CLV"
          value={`$${stats.avgCLV.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          subtitle="Customer Lifetime Value baseline"
          icon={HeartHandshake}
          variant="accent"
        />
        <KPICard
          id="rfm-kpi-at-risk"
          title="At-Risk Customers"
          value={stats.atRiskCount.toLocaleString()}
          subtitle="Dormant > 90 purchase days"
          icon={AlertTriangle}
          variant="warning"
        />
        <KPICard
          id="rfm-kpi-rev-risk"
          title="Revenue at Churn Risk"
          value={`$${stats.revenueAtRisk.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          subtitle="Target volume for win-back"
          icon={TrendingDown}
        />
      </div>

      {/* RFM Segment Pill Filter */}
      <div className="flex flex-wrap items-center gap-2 bg-white p-2.5 rounded-xl border border-slate-200/90 text-xs shadow-xs">
        <span className="font-bold text-slate-700 ml-2">Filter Cohort:</span>
        <button
          onClick={() => setSelectedSegment('all')}
          className={`px-3 py-1 rounded-lg font-medium transition-colors whitespace-nowrap ${
            selectedSegment === 'all'
              ? 'bg-slate-900 text-white font-semibold'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          All Customers ({stats.totalCustomers.toLocaleString()})
        </button>
        {segmentData.map((item) => (
          <button
            key={item.segment}
            onClick={() => setSelectedSegment(item.segment)}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-lg font-medium transition-colors whitespace-nowrap ${
              selectedSegment === item.segment
                ? 'bg-blue-600 text-white font-semibold'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <span
              className="w-2 h-2 rounded-full shrink-0"
              style={{ backgroundColor: SEGMENT_COLORS[item.segment] }}
            />
            <span>{item.segment} ({item.count.toLocaleString()})</span>
          </button>
        ))}
      </div>

      {/* Visual Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* RFM Cohort Bar Chart */}
        <div className="lg:col-span-1">
          <ChartCard
            id="chart-rfm-distribution"
            title="Customer Cluster Distribution"
            subtitle="Customer head-count grouped by behavioral segment"
          >
            <div className="h-72 w-full">
              {segmentData.length === 0 ? (
                <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                  No segment data available.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={segmentData}
                    layout="vertical"
                    margin={{ top: 5, right: 20, left: 15, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
                    <XAxis type="number" stroke="#94A3B8" fontSize={10} tickLine={false} />
                    <YAxis
                      type="category"
                      dataKey="segment"
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      width={115}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                      formatter={(val: any) => [`${Number(val).toLocaleString()} Customers`, 'Headcount']}
                    />
                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                      {segmentData.map((entry) => (
                        <Cell key={entry.segment} fill={SEGMENT_COLORS[entry.segment] || '#3B82F6'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </ChartCard>
        </div>

        {/* Recency vs Monetary Scatter */}
        <div className="lg:col-span-2">
          <ChartCard
            id="chart-rfm-scatter-matrix"
            title="RFM Behavioral Matrix (Recency vs Spend)"
            subtitle="Bubble size represents purchase frequency; X-axis represents recency days (fewer days is better)"
          >
            <div className="h-72 w-full">
              {scatterData.length === 0 ? (
                <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                  No customer scatter data available.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 10, right: 20, left: 15, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                    <XAxis
                      type="number"
                      dataKey="recency"
                      name="Recency"
                      unit=" days"
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                    />
                    <YAxis
                      type="number"
                      dataKey="monetary"
                      name="Spend"
                      unit="$"
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      tickFormatter={(v) => `$${v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v}`}
                    />
                    <ZAxis type="number" dataKey="frequency" range={[50, 400]} name="Orders" />
                    <Tooltip
                      cursor={{ strokeDasharray: '3 3' }}
                      contentStyle={{ backgroundColor: '#0F172A', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                      formatter={(value: any, name: any) => [name === 'Spend' ? `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : value, name]}
                    />
                    <Scatter data={scatterData} fill="#3B82F6">
                      {scatterData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={SEGMENT_COLORS[entry.segment as RFMSegmentName] || '#3B82F6'}
                          opacity={0.8}
                        />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              )}
            </div>
          </ChartCard>
        </div>
      </div>

      {/* Targeted Re-engagement confirmation banner */}
      {targetedCustomerId && (
        <div className="bg-emerald-50 border border-emerald-300 rounded-xl p-3.5 flex items-center gap-3 text-xs text-emerald-900 shadow-xs animate-in fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          <div>
            <span className="font-bold">Automated Re-engagement Triggered:</span> Personalized retention promotion code & email sequence queued for customer {targetedCustomerId}.
          </div>
        </div>
      )}

      {/* Customer RFM Table */}
      <DataTable<CustomerRFM>
        id="table-customer-rfm"
        title="Customer RFM Profiles"
        subtitle="Individual customer RFM scores, segment categorizations, and churn probability"
        data={filteredRFM}
        columns={[
          {
            key: 'customerName',
            header: 'Customer',
            sortable: true,
            render: (row) => (
              <div className="max-w-[200px] truncate">
                <span className="font-bold text-slate-900 block truncate" title={row.customerName}>
                  {row.customerName}
                </span>
                <span className="text-[11px] text-slate-400 truncate block" title={row.customerEmail}>
                  {row.customerEmail}
                </span>
              </div>
            )
          },
          {
            key: 'segment',
            header: 'Segment',
            sortable: true,
            render: (row) => (
              <Badge
                variant={
                  row.segment === 'Champions'
                    ? 'success'
                    : row.segment === 'Loyal Customers'
                    ? 'primary'
                    : row.segment === 'Potential Loyalists'
                    ? 'purple'
                    : row.segment === 'At Risk'
                    ? 'warning'
                    : 'danger'
                }
                dot
                size="sm"
              >
                {row.segment}
              </Badge>
            )
          },
          {
            key: 'recencyDays',
            header: 'Recency',
            sortable: true,
            align: 'right',
            render: (row) => (
              <span className="text-slate-700 font-medium">{row.recencyDays}d ago</span>
            )
          },
          {
            key: 'frequency',
            header: 'Orders',
            sortable: true,
            align: 'center',
            render: (row) => <span className="font-semibold text-slate-800">{row.frequency}</span>
          },
          {
            key: 'monetaryValue',
            header: 'Lifetime Spend',
            sortable: true,
            align: 'right',
            render: (row) => (
              <span className="font-bold text-slate-900">
                ${row.monetaryValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            )
          },
          {
            key: 'rfmScore',
            header: 'RFM Score',
            sortable: true,
            align: 'center',
            render: (row) => (
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-100 font-bold text-slate-700">
                {row.rScore}-{row.fScore}-{row.mScore}
              </span>
            )
          },
          {
            key: 'preferredCategory',
            header: 'Favorite Category',
            sortable: true,
            render: (row) => <span className="text-slate-700 text-xs">{row.preferredCategory}</span>
          },
          {
            key: 'churnProbability',
            header: 'Churn Risk',
            sortable: true,
            align: 'right',
            render: (row) => (
              <span
                className={`font-semibold text-xs ${
                  row.churnProbability > 0.6
                    ? 'text-rose-600'
                    : row.churnProbability > 0.3
                    ? 'text-amber-600'
                    : 'text-emerald-600'
                }`}
              >
                {Math.round(row.churnProbability * 100)}%
              </span>
            )
          },
          {
            key: 'actions',
            header: 'Action',
            render: (row) => (
              <button
                onClick={() => handleTriggerReengagement(row)}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 hover:bg-blue-50 hover:text-blue-700 text-slate-700 text-[11px] font-semibold transition-colors"
                title="Send personalized promotional campaign"
              >
                <Mail className="w-3 h-3" />
                <span>Re-engage</span>
              </button>
            )
          }
        ]}
      />
    </div>
  );
};
