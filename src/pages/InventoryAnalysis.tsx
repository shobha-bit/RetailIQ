import React, { useMemo, useState } from 'react';
import {
  Boxes,
  AlertTriangle,
  Clock,
  RotateCcw,
  CheckCircle2,
  DollarSign,
  Plus,
  Warehouse,
  Package,
  Layers
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
import { InventoryItem } from '../types';
import { KPICard } from '../components/common/KPICard';
import { ChartCard } from '../components/common/ChartCard';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

const RISK_COLORS = {
  Critical: '#EF4444',
  High: '#F97316',
  Moderate: '#FBBF24',
  Low: '#10B981'
};

export const InventoryAnalysis: React.FC = () => {
  const { inventory, isLoadingRetail, retailLoadError, reloadRetailData, realDataset, retailKPIs } = useDataset();
  const [reorderedSkus, setReorderedSkus] = useState<Set<string>>(new Set());

  // Aggregate stats dynamically derived from inventory items and real dataset
  const stats = useMemo(() => {
    const totalUnits = retailKPIs?.totalStock ?? inventory.reduce((acc, i) => acc + i.currentStock, 0);
    const totalItems = retailKPIs?.inventoryItems ?? inventory.length;
    const lowStockCount = retailKPIs?.lowStockItems ?? (
      realDataset?.inventory
        ? realDataset.inventory.filter((i) => i.stock_status === 'Low Stock').length
        : inventory.filter((i) => i.stockoutRisk === 'Critical').length
    );
    const warehouseCount = retailKPIs?.warehouses ?? (
      realDataset?.inventory
        ? new Set(realDataset.inventory.map((i) => i.warehouse_name).filter(Boolean)).size
        : 3
    );
    const totalValuation = inventory.reduce((acc, i) => acc + (i.currentStock * i.unitCost), 0);
    const avgTurnover = inventory.length > 0
      ? Math.round((inventory.reduce((acc, i) => acc + i.turnoverRatio, 0) / inventory.length) * 10) / 10
      : 4.2;
    const avgDays = inventory.length > 0
      ? Math.round((inventory.reduce((acc, i) => acc + i.daysOfInventory, 0) / inventory.length) * 10) / 10
      : 45.0;

    return {
      totalUnits,
      totalItems,
      lowStockCount,
      warehouseCount,
      totalValuation,
      avgTurnover,
      avgDays
    };
  }, [inventory, realDataset, retailKPIs]);

  // Warehouse breakdown dynamically derived from real inventory data
  const warehouseBreakdown = useMemo(() => {
    if (!realDataset?.inventory || realDataset.inventory.length === 0) {
      return [
        { name: 'Office Supply Warehouse', location: 'Chicago', stock: 297000, items: 1082, lowStock: 14 },
        { name: 'Technology Warehouse', location: 'San Francisco', stock: 111733, items: 404, lowStock: 10 },
        { name: 'Furniture Warehouse', location: 'New York', stock: 103879, items: 375, lowStock: 10 }
      ];
    }

    const whMap: Record<string, { name: string; location: string; stock: number; items: number; lowStock: number }> = {};
    realDataset.inventory.forEach((r) => {
      const name = r.warehouse_name || 'Regional Hub';
      const loc = r.warehouse_location || 'Central';
      if (!whMap[name]) {
        whMap[name] = { name, location: loc, stock: 0, items: 0, lowStock: 0 };
      }
      whMap[name].stock += Number(r.stock_quantity) || 0;
      whMap[name].items += 1;
      if (r.stock_status === 'Low Stock') {
        whMap[name].lowStock += 1;
      }
    });

    return Object.values(whMap).sort((a, b) => b.stock - a.stock);
  }, [realDataset]);

  // Risk distribution for pie chart
  const riskData = useMemo(() => {
    const counts: Record<string, number> = { Critical: 0, High: 0, Moderate: 0, Low: 0 };
    inventory.forEach((i) => {
      counts[i.stockoutRisk] = (counts[i.stockoutRisk] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [inventory]);

  // Stock vs Reorder Point chart data (representative sample of catalog items)
  const stockComparisonData = useMemo(() => {
    return inventory.slice(0, 8).map((i) => ({
      sku: i.sku,
      name: i.productName.split(' ').slice(0, 3).join(' '),
      fullName: i.productName,
      currentStock: i.currentStock,
      reorderPoint: i.reorderPoint,
      safetyStock: i.safetyStock
    }));
  }, [inventory]);

  const handleCreatePurchaseOrder = (sku: string) => {
    setReorderedSkus((prev) => new Set(prev).add(sku));
  };

  if (isLoadingRetail) {
    return (
      <div id="inventory-dashboard-loading" className="p-6">
        <LoadingState message="Loading inventory valuations and stockout risks from real datasets..." />
      </div>
    );
  }

  if (retailLoadError) {
    return (
      <div id="inventory-dashboard-error" className="p-6">
        <ErrorState
          title="Failed to Load Inventory Optimization"
          message={retailLoadError}
          onRetry={reloadRetailData}
        />
      </div>
    );
  }

  return (
    <div id="inventory-analysis-page" className="space-y-6">
      <PageHeader
        id="inventory-page-header"
        title="Inventory Optimization & Supply Chain"
        description="Continuous stock monitoring, safety stock buffers, economic reorder thresholds, and inventory turnover health."
        badge={<Badge variant="warning" dot>Automated Replenishment Engine</Badge>}
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <KPICard
          id="inv-kpi-units"
          title="Total Stock"
          value={stats.totalUnits.toLocaleString()}
          subtitle="Physical units on hand"
          icon={Boxes}
        />
        <KPICard
          id="inv-kpi-items"
          title="Inventory Items"
          value={stats.totalItems.toLocaleString()}
          subtitle="Active catalog SKUs"
          icon={Package}
        />
        <KPICard
          id="inv-kpi-stockout"
          title="Low Stock Items"
          value={stats.lowStockCount.toLocaleString()}
          subtitle="SKUs below reorder point"
          icon={AlertTriangle}
          variant={stats.lowStockCount > 0 ? 'warning' : 'default'}
        />
        <KPICard
          id="inv-kpi-warehouses"
          title="Warehouses"
          value={stats.warehouseCount.toLocaleString()}
          subtitle="Active distribution hubs"
          icon={Warehouse}
        />
        <KPICard
          id="inv-kpi-valuation"
          title="Inventory Valuation"
          value={`$${stats.totalValuation.toLocaleString('en-US', { maximumFractionDigits: 0 })}`}
          subtitle="At baseline unit cost"
          icon={DollarSign}
          variant="accent"
        />
        <KPICard
          id="inv-kpi-turnover"
          title="Turnover Velocity"
          value={`${stats.avgTurnover.toFixed(1)}x`}
          subtitle={`${stats.avgDays.toFixed(0)} days avg sell-through`}
          icon={RotateCcw}
          variant="success"
        />
      </div>

      {/* Warehouse Distribution Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {warehouseBreakdown.map((wh) => (
          <div
            key={wh.name}
            id={`warehouse-card-${wh.name.toLowerCase().replace(/[^a-z0-9]/g, '-')}`}
            className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-xs hover:border-slate-300 transition-colors"
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 min-w-0">
                <div className="p-1.5 rounded-lg bg-blue-50 text-blue-600 flex-shrink-0">
                  <Warehouse className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <h4 className="font-semibold text-slate-900 text-sm truncate" title={wh.name}>
                    {wh.name}
                  </h4>
                  <p className="text-xs text-slate-400 truncate">{wh.location} Hub</p>
                </div>
              </div>
              <Badge variant={wh.lowStock > 0 ? 'warning' : 'success'} size="sm">
                {wh.lowStock} Low Stock
              </Badge>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-slate-500 block">Stock Quantity</span>
                <span className="font-bold text-slate-900 text-sm mt-0.5 block">
                  {wh.stock.toLocaleString()}
                </span>
              </div>
              <div className="text-right">
                <span className="text-slate-500 block">Inventory SKUs</span>
                <span className="font-semibold text-slate-700 text-sm mt-0.5 block">
                  {wh.items.toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stock vs Reorder Level Comparison */}
        <div className="lg:col-span-2">
          <ChartCard
            id="chart-stock-vs-reorder"
            title="Stock Level vs Reorder Threshold"
            subtitle="Current available inventory versus dynamic safety buffer and reorder trigger"
          >
            <div className="h-72 w-full">
              {stockComparisonData.length === 0 ? (
                <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                  No inventory records available to display.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stockComparisonData} margin={{ top: 10, right: 15, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                    <XAxis
                      dataKey="sku"
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      tickFormatter={(sku) => sku.replace(/^[A-Z]+-[A-Z]+-/, '')}
                    />
                    <YAxis
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      tickFormatter={(v) => Number(v).toLocaleString()}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0F172A',
                        border: 'none',
                        borderRadius: '8px',
                        color: '#fff',
                        fontSize: '12px'
                      }}
                      formatter={(val: any, name: any) => [`${Number(val).toLocaleString()} units`, name]}
                      labelFormatter={(label: any) => {
                        const item = stockComparisonData.find((d) => d.sku === label);
                        return item ? `${item.sku} — ${item.fullName}` : label;
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '6px' }} />
                    <Bar dataKey="currentStock" name="Current Stock" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="reorderPoint" name="Reorder Point" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="safetyStock" name="Safety Stock" fill="#EF4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </ChartCard>
        </div>

        {/* Stockout Risk Donut */}
        <div className="lg:col-span-1">
          <ChartCard
            id="chart-stockout-risk"
            title="Stockout Risk Profile"
            subtitle="Catalog items categorized by replenishment urgency"
          >
            <div className="h-72 w-full flex flex-col items-center justify-center">
              {riskData.every((d) => d.value === 0) ? (
                <div className="h-full w-full flex items-center justify-center text-slate-400 text-xs">
                  No risk categories available.
                </div>
              ) : (
                <>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={riskData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {riskData.map((entry) => (
                          <Cell
                            key={entry.name}
                            fill={RISK_COLORS[entry.name as keyof typeof RISK_COLORS] || '#64748B'}
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
                        formatter={(val: any) => [`${Number(val).toLocaleString()} SKUs`, 'Count']}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="w-full grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-slate-100 text-xs">
                    {riskData.map((entry) => (
                      <div key={entry.name} className="flex items-center gap-1.5 min-w-0">
                        <span
                          className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                          style={{ backgroundColor: RISK_COLORS[entry.name as keyof typeof RISK_COLORS] || '#64748B' }}
                        />
                        <span className="text-slate-600 truncate">{entry.name}:</span>
                        <span className="font-bold text-slate-900 ml-auto whitespace-nowrap">
                          {entry.value.toLocaleString()} SKUs
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

      {/* Replenishment Inventory Table */}
      <DataTable
        id="table-inventory-replenishment"
        title="Stock Replenishment & Reorder Register"
        subtitle="Catalog inventory status with dynamic safety buffer and purchase order generator"
        data={inventory}
        columns={[
          {
            key: 'sku',
            header: 'SKU',
            sortable: true,
            render: (row) => <span className="font-mono font-semibold text-slate-800 text-xs">{row.sku}</span>
          },
          {
            key: 'productName',
            header: 'Product',
            sortable: true,
            render: (row) => (
              <div className="max-w-[240px] truncate" title={row.productName}>
                <span className="font-medium text-slate-900 block truncate">{row.productName}</span>
                <span className="text-[11px] text-slate-400">{row.category}</span>
              </div>
            )
          },
          {
            key: 'currentStock',
            header: 'On Hand',
            sortable: true,
            align: 'right',
            render: (row) => (
              <span
                className={`font-bold ${
                  row.currentStock <= row.safetyStock ? 'text-rose-600' : 'text-slate-900'
                }`}
              >
                {row.currentStock.toLocaleString()} units
              </span>
            )
          },
          {
            key: 'reorderPoint',
            header: 'Reorder Point',
            sortable: true,
            align: 'right',
            render: (row) => <span className="text-slate-700 font-medium">{row.reorderPoint.toLocaleString()}</span>
          },
          {
            key: 'dailyDemand',
            header: 'Daily Run-Rate',
            sortable: true,
            align: 'right',
            render: (row) => <span className="text-slate-700">{row.dailyDemand.toLocaleString()} / day</span>
          },
          {
            key: 'leadTimeDays',
            header: 'Lead Time',
            sortable: true,
            align: 'right',
            render: (row) => <span className="text-slate-700">{row.leadTimeDays} days</span>
          },
          {
            key: 'turnoverRatio',
            header: 'Turnover',
            sortable: true,
            align: 'right',
            render: (row) => <span className="font-semibold text-slate-800">{row.turnoverRatio}x</span>
          },
          {
            key: 'stockoutRisk',
            header: 'Stockout Risk',
            sortable: true,
            render: (row) => (
              <Badge
                variant={
                  row.stockoutRisk === 'Critical'
                    ? 'danger'
                    : row.stockoutRisk === 'High'
                    ? 'warning'
                    : row.stockoutRisk === 'Moderate'
                    ? 'neutral'
                    : 'success'
                }
                dot
                size="sm"
              >
                {row.stockoutRisk}
              </Badge>
            )
          },
          {
            key: 'action',
            header: 'Replenish',
            render: (row) => {
              const isReordered = reorderedSkus.has(row.sku);
              return (
                <button
                  onClick={() => handleCreatePurchaseOrder(row.sku)}
                  disabled={isReordered}
                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-semibold transition-colors ${
                    isReordered
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 cursor-default'
                      : 'bg-slate-900 text-white hover:bg-slate-800 cursor-pointer'
                  }`}
                >
                  {isReordered ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>PO Issued</span>
                    </>
                  ) : (
                    <>
                      <Plus className="w-3.5 h-3.5" />
                      <span>Order PO</span>
                    </>
                  )}
                </button>
              );
            }
          }
        ]}
      />
    </div>
  );
};
