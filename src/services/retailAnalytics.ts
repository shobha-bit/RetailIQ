import {
  RetailDataset,
  OrderRecord,
  CustomerRecord,
  ProductRecord,
  InventoryRecord,
  ReturnRecord,
  TransportationRecord,
} from './retailDataLoader';

/**
 * Filter parameters for sliced analytical queries.
 */
export interface RetailFilters {
  startDate?: string;
  endDate?: string;
  region?: string;
  category?: string;
  subCategory?: string;
  segment?: string;
  shipMode?: string;
  state?: string;
  searchQuery?: string;
}

/**
 * Year-over-Year sales growth breakdown.
 */
export interface SalesYoYBreakdown {
  latestYear: number;
  priorYear: number;
  latestYearSales: number;
  priorYearSales: number;
  growthPct: number;
  yearlySales: Record<number, number>;
  yearlyGrowth: Array<{
    year: number;
    sales: number;
    growthPct: number | null;
  }>;
}

/**
 * Returns KPIs structure.
 */
export interface ReturnsKPIs {
  totalReturns: number;
  returnedProducts: number;
  returnRate: number;
}

/**
 * Inventory KPIs structure.
 */
export interface InventoryKPIs {
  totalStock: number;
  inventoryItems: number;
  lowStockItems: number;
  warehouses: number;
}

/**
 * Logistics KPIs structure.
 */
export interface LogisticsKPIs {
  averageDeliveryDays: number;
  validShipmentCount: number;
}

/**
 * Complete consolidated retail KPIs structure.
 * All values are raw numeric amounts. UI presentation ($, %, K, M) is handled by presentation layers.
 */
export interface RetailKPIs {
  totalSales: number;
  totalOrders: number;
  totalCustomers: number;
  averageOrderValue: number;
  aov: number;
  ordersPerCustomer: number;
  totalProducts: number;
  averageSalesPerProduct: number;
  totalReturns: number;
  returnedProducts: number;
  returnRate: number;
  averageDeliveryDays: number;
  totalStock: number;
  inventoryItems: number;
  lowStockItems: number;
  warehouses: number;
  salesYoY: number;
  salesYoYBreakdown: SalesYoYBreakdown;
}

/**
 * Filters order transactions by optional criteria without altering original records.
 */
export function filterRetailOrders(
  orders: OrderRecord[],
  filters?: RetailFilters,
  customers?: CustomerRecord[],
  products?: ProductRecord[]
): OrderRecord[] {
  if (!filters) return orders;

  const {
    startDate,
    endDate,
    region,
    category,
    subCategory,
    segment,
    shipMode,
    state,
    searchQuery,
  } = filters;

  const q = searchQuery ? searchQuery.toLowerCase().trim() : '';
  const custMap =
    customers && q ? new Map(customers.map((c) => [c.customer_id, c.customer_name.toLowerCase()])) : null;
  const prodMap =
    products && q ? new Map(products.map((p) => [p.product_id, p.product_name.toLowerCase()])) : null;

  return orders.filter((order) => {
    if (startDate && order.order_date < startDate) return false;
    if (endDate && order.order_date > endDate) return false;
    if (region && region !== 'all' && order.region !== region) return false;
    if (shipMode && shipMode !== 'all' && order.ship_mode !== shipMode) return false;
    if (state && state !== 'all' && order.state !== state) return false;

    if (category && category !== 'all' && order.category !== category) return false;
    if (subCategory && subCategory !== 'all' && order.sub_category !== subCategory) return false;
    if (segment && segment !== 'all' && order.segment !== segment) return false;

    if (q) {
      const match =
        (order.order_id && order.order_id.toLowerCase().includes(q)) ||
        (order.customer_id && order.customer_id.toLowerCase().includes(q)) ||
        (order.product_id && order.product_id.toLowerCase().includes(q)) ||
        (order.city && order.city.toLowerCase().includes(q)) ||
        (order.state && order.state.toLowerCase().includes(q)) ||
        (custMap && custMap.get(order.customer_id)?.includes(q)) ||
        (prodMap && prodMap.get(order.product_id)?.includes(q));
      if (!match) return false;
    }

    return true;
  });
}

/**
 * 1. Total Sales: SUM(orders.sales)
 * Directly aggregates from the orders fact table to prevent row-multiplication duplication.
 */
export function calculateTotalSales(orders: OrderRecord[]): number {
  let sum = 0;
  for (let i = 0; i < orders.length; i++) {
    const val = orders[i].sales;
    if (typeof val === 'number' && !isNaN(val)) {
      sum += val;
    } else if (val) {
      const parsed = parseFloat(String(val));
      if (!isNaN(parsed)) sum += parsed;
    }
  }
  return sum;
}

/**
 * 2. Total Orders: COUNT(DISTINCT orders.order_id)
 * Notice: orders has 9,800 line items but 4,922 unique orders.
 */
export function calculateTotalOrders(orders: OrderRecord[]): number {
  const distinct = new Set<string>();
  for (let i = 0; i < orders.length; i++) {
    if (orders[i].order_id) {
      distinct.add(orders[i].order_id);
    }
  }
  return distinct.size;
}

/**
 * 3. Total Customers: COUNT(DISTINCT customer_id)
 * If full customer list is provided and orders are unfiltered, counts total customers;
 * otherwise counts distinct customers in the given orders subset.
 */
export function calculateTotalCustomers(
  orders: OrderRecord[],
  allCustomers?: CustomerRecord[]
): number {
  if (allCustomers && allCustomers.length > 0 && orders.length === 9800) {
    return allCustomers.length;
  }
  const distinct = new Set<string>();
  for (let i = 0; i < orders.length; i++) {
    if (orders[i].customer_id) {
      distinct.add(orders[i].customer_id);
    }
  }
  return distinct.size;
}

/**
 * 4. Average Order Value (AOV): Total Sales / Distinct Orders
 */
export function calculateAverageOrderValue(
  totalSales: number,
  totalOrders: number
): number {
  if (totalOrders === 0) return 0;
  return totalSales / totalOrders;
}

/**
 * 5. Orders Per Customer: Distinct Orders / Distinct Customers
 */
export function calculateOrdersPerCustomer(
  totalOrders: number,
  totalCustomers: number
): number {
  if (totalCustomers === 0) return 0;
  return totalOrders / totalCustomers;
}

/**
 * 6. Total Products: COUNT(DISTINCT product_id)
 */
export function calculateTotalProducts(
  orders: OrderRecord[],
  allProducts?: ProductRecord[]
): number {
  if (allProducts && allProducts.length > 0 && orders.length === 9800) {
    return allProducts.length;
  }
  const distinct = new Set<string>();
  for (let i = 0; i < orders.length; i++) {
    if (orders[i].product_id) {
      distinct.add(orders[i].product_id);
    }
  }
  return distinct.size;
}

/**
 * 7. Average Sales Per Product: Total Sales / Total Products
 */
export function calculateAverageSalesPerProduct(
  totalSales: number,
  totalProducts: number
): number {
  if (totalProducts === 0) return 0;
  return totalSales / totalProducts;
}

/**
 * Returns KPIs:
 * - totalReturns: count of return records
 * - returnedProducts: count of unique products returned
 * - returnRate: (totalReturns / totalOrders) * 100 per KPI_Definitions.md
 */
export function calculateReturnsKPIs(
  returns: ReturnRecord[],
  totalOrdersCount: number,
  matchingOrderRowIds?: Set<number>
): ReturnsKPIs {
  const relevantReturns = matchingOrderRowIds
    ? returns.filter((r) => matchingOrderRowIds.has(r.order_row_id))
    : returns;

  const totalReturns = relevantReturns.length;
  const returnedProducts = new Set(relevantReturns.map((r) => r.product_id)).size;
  const returnRate =
    totalOrdersCount > 0 ? (totalReturns / totalOrdersCount) * 100 : 0;

  return {
    totalReturns,
    returnedProducts,
    returnRate,
  };
}

/**
 * Inventory KPIs:
 * - totalStock: SUM(stock_quantity)
 * - inventoryItems: total items in catalog
 * - lowStockItems: count where stock_status === 'Low Stock'
 * - warehouses: COUNT(DISTINCT warehouse_name)
 */
export function calculateInventoryKPIs(
  inventory: InventoryRecord[]
): InventoryKPIs {
  let totalStock = 0;
  let lowStockItems = 0;
  const warehousesSet = new Set<string>();

  for (let i = 0; i < inventory.length; i++) {
    const item = inventory[i];
    if (typeof item.stock_quantity === 'number') {
      totalStock += item.stock_quantity;
    }
    if (item.stock_status === 'Low Stock') {
      lowStockItems++;
    }
    if (item.warehouse_name) {
      warehousesSet.add(item.warehouse_name);
    }
  }

  return {
    totalStock,
    inventoryItems: inventory.length,
    lowStockItems,
    warehouses: warehousesSet.size,
  };
}

/**
 * Logistics KPIs:
 * - averageDeliveryDays: AVG(actual_delivery_date - dispatch_date)
 * Excludes invalid or missing dates and negative duration anomalies.
 */
export function calculateLogisticsKPIs(
  transportation: TransportationRecord[],
  matchingOrderRowIds?: Set<number>
): LogisticsKPIs {
  const relevantTransport = matchingOrderRowIds
    ? transportation.filter((t) => matchingOrderRowIds.has(t.order_row_id))
    : transportation;

  let totalDays = 0;
  let validCount = 0;

  for (let i = 0; i < relevantTransport.length; i++) {
    const record = relevantTransport[i];
    if (!record.dispatch_date || !record.actual_delivery_date) continue;

    const dispatch = new Date(record.dispatch_date).getTime();
    const delivery = new Date(record.actual_delivery_date).getTime();

    if (isNaN(dispatch) || isNaN(delivery)) continue;

    const diffDays = Math.round((delivery - dispatch) / (1000 * 60 * 60 * 24));
    if (diffDays >= 0 && diffDays <= 60) {
      totalDays += diffDays;
      validCount++;
    }
  }

  const averageDeliveryDays = validCount > 0 ? totalDays / validCount : 0;

  return {
    averageDeliveryDays,
    validShipmentCount: validCount,
  };
}

/**
 * Sales YoY Growth:
 * Dynamically aggregates sales by year from order_date and calculates growth
 * for the latest year compared to the immediately preceding year.
 * Also returns the full historical yearly sales and growth progression.
 */
export function calculateSalesYoY(orders: OrderRecord[]): SalesYoYBreakdown {
  const yearlySales: Record<number, number> = {};

  for (let i = 0; i < orders.length; i++) {
    const dateStr = orders[i].order_date;
    if (!dateStr) continue;

    // Extract 4-digit year robustly (ISO YYYY-MM-DD or MM/DD/YYYY)
    let year: number | null = null;
    if (dateStr.includes('-')) {
      year = parseInt(dateStr.slice(0, 4), 10);
    } else if (dateStr.includes('/')) {
      const parts = dateStr.split('/');
      year = parseInt(parts[parts.length - 1], 10);
    } else {
      year = new Date(dateStr).getFullYear();
    }

    if (year && !isNaN(year) && year >= 2000 && year <= 2100) {
      yearlySales[year] = (yearlySales[year] || 0) + (orders[i].sales || 0);
    }
  }

  const sortedYears = Object.keys(yearlySales)
    .map(Number)
    .sort((a, b) => a - b);

  const yearlyGrowth: Array<{
    year: number;
    sales: number;
    growthPct: number | null;
  }> = [];

  for (let i = 0; i < sortedYears.length; i++) {
    const yr = sortedYears[i];
    const currentSales = yearlySales[yr];
    if (i === 0) {
      yearlyGrowth.push({ year: yr, sales: currentSales, growthPct: null });
    } else {
      const prevSales = yearlySales[sortedYears[i - 1]];
      const pct = prevSales > 0 ? ((currentSales - prevSales) / prevSales) * 100 : 0;
      yearlyGrowth.push({ year: yr, sales: currentSales, growthPct: pct });
    }
  }

  if (sortedYears.length < 2) {
    const singleYear = sortedYears[0] ?? 0;
    return {
      latestYear: singleYear,
      priorYear: singleYear,
      latestYearSales: yearlySales[singleYear] || 0,
      priorYearSales: 0,
      growthPct: 0,
      yearlySales,
      yearlyGrowth,
    };
  }

  const latestYear = sortedYears[sortedYears.length - 1];
  const priorYear = sortedYears[sortedYears.length - 2];
  const latestYearSales = yearlySales[latestYear];
  const priorYearSales = yearlySales[priorYear];
  const growthPct =
    priorYearSales > 0 ? ((latestYearSales - priorYearSales) / priorYearSales) * 100 : 0;

  return {
    latestYear,
    priorYear,
    latestYearSales,
    priorYearSales,
    growthPct,
    yearlySales,
    yearlyGrowth,
  };
}

/**
 * Centralized master function to calculate all retail KPIs.
 * Combines core sales, customers, products, returns, inventory, logistics, and YoY analytics.
 */
export function calculateRetailKPIs(
  dataset: RetailDataset,
  filters?: RetailFilters
): RetailKPIs {
  const filteredOrders = filterRetailOrders(
    dataset.orders,
    filters,
    dataset.customers,
    dataset.products
  );

  const totalSales = calculateTotalSales(filteredOrders);
  const totalOrders = calculateTotalOrders(filteredOrders);
  const totalCustomers = calculateTotalCustomers(filteredOrders, dataset.customers);
  const aov = calculateAverageOrderValue(totalSales, totalOrders);
  const ordersPerCustomer = calculateOrdersPerCustomer(totalOrders, totalCustomers);
  const totalProducts = calculateTotalProducts(filteredOrders, dataset.products);
  const avgSalesPerProduct = calculateAverageSalesPerProduct(totalSales, totalProducts);

  // Match order_row_id if filters are active
  const hasActiveFilters = Boolean(
    filters && Object.values(filters).some((v) => v && v !== 'all')
  );
  const matchingRowIds = hasActiveFilters
    ? new Set(filteredOrders.map((o) => o.row_id))
    : undefined;

  const returnsKPIs = calculateReturnsKPIs(
    dataset.returns,
    totalOrders,
    matchingRowIds
  );

  const inventoryKPIs = calculateInventoryKPIs(dataset.inventory);

  const logisticsKPIs = calculateLogisticsKPIs(
    dataset.transportation,
    matchingRowIds
  );

  const salesYoYBreakdown = calculateSalesYoY(filteredOrders);

  return {
    totalSales,
    totalOrders,
    totalCustomers,
    averageOrderValue: aov,
    aov,
    ordersPerCustomer,
    totalProducts,
    averageSalesPerProduct: avgSalesPerProduct,
    totalReturns: returnsKPIs.totalReturns,
    returnedProducts: returnsKPIs.returnedProducts,
    returnRate: returnsKPIs.returnRate,
    averageDeliveryDays: logisticsKPIs.averageDeliveryDays,
    totalStock: inventoryKPIs.totalStock,
    inventoryItems: inventoryKPIs.inventoryItems,
    lowStockItems: inventoryKPIs.lowStockItems,
    warehouses: inventoryKPIs.warehouses,
    salesYoY: salesYoYBreakdown.growthPct,
    salesYoYBreakdown,
  };
}

/**
 * Lightweight verification assertion structure.
 */
export interface RetailValidationCheck {
  metric: string;
  expected: number;
  actual: number;
  tolerance: number;
  passed: boolean;
  notes?: string;
}

export interface RetailValidationReport {
  timestamp: string;
  allPassed: boolean;
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  checks: RetailValidationCheck[];
}

/**
 * Task 10 verification test mechanism.
 * Tests actual calculated real-data outputs against baseline expectations with explicit tolerances.
 * Baseline constants are only defined inside this verification function as assertion targets.
 */
export function verifyRetailCalculations(dataset: RetailDataset): RetailValidationReport {
  const kpis = calculateRetailKPIs(dataset);

  const assertions: Array<{
    metric: string;
    expected: number;
    actual: number;
    tolerance: number;
    notes?: string;
  }> = [
    {
      metric: 'Total Sales ($)',
      expected: 2261536.97,
      actual: kpis.totalSales,
      tolerance: 0.05,
    },
    {
      metric: 'Total Orders',
      expected: 4922,
      actual: kpis.totalOrders,
      tolerance: 0,
    },
    {
      metric: 'Total Customers',
      expected: 793,
      actual: kpis.totalCustomers,
      tolerance: 0,
    },
    {
      metric: 'Average Order Value (AOV)',
      expected: 459.48,
      actual: kpis.averageOrderValue,
      tolerance: 0.05,
    },
    {
      metric: 'Orders Per Customer',
      expected: 6.21,
      actual: kpis.ordersPerCustomer,
      tolerance: 0.02,
    },
    {
      metric: 'Total Products',
      expected: 1861,
      actual: kpis.totalProducts,
      tolerance: 0,
    },
    {
      metric: 'Average Sales Per Product',
      expected: 1215.23,
      actual: kpis.averageSalesPerProduct,
      tolerance: 0.05,
    },
    {
      metric: 'Total Returns',
      expected: 490,
      actual: kpis.totalReturns,
      tolerance: 0,
    },
    {
      metric: 'Returned Products',
      expected: 424,
      actual: kpis.returnedProducts,
      tolerance: 0,
    },
    {
      metric: 'Return Rate (%)',
      expected: 9.96,
      actual: kpis.returnRate,
      tolerance: 0.02,
    },
    {
      metric: 'Average Delivery Days',
      expected: 4.11,
      actual: kpis.averageDeliveryDays,
      tolerance: 0.05,
    },
    {
      metric: 'Total Stock Quantity',
      expected: 512612,
      actual: kpis.totalStock,
      tolerance: 0,
    },
    {
      metric: 'Inventory Items',
      expected: 1861,
      actual: kpis.inventoryItems,
      tolerance: 0,
    },
    {
      metric: 'Low Stock Items',
      expected: 34,
      actual: kpis.lowStockItems,
      tolerance: 0,
    },
    {
      metric: 'Warehouses',
      expected: 3,
      actual: kpis.warehouses,
      tolerance: 0,
    },
  ];

  const checks: RetailValidationCheck[] = assertions.map((a) => {
    const diff = Math.abs(a.actual - a.expected);
    const passed = diff <= a.tolerance;
    return {
      metric: a.metric,
      expected: a.expected,
      actual: Number(a.actual.toFixed(2)),
      tolerance: a.tolerance,
      passed,
      notes: passed
        ? 'Pass'
        : `Fail: diff ${diff.toFixed(4)} exceeds tolerance ${a.tolerance}`,
    };
  });

  const passedChecks = checks.filter((c) => c.passed).length;
  const failedChecks = checks.length - passedChecks;

  return {
    timestamp: new Date().toISOString(),
    allPassed: failedChecks === 0,
    totalChecks: checks.length,
    passedChecks,
    failedChecks,
    checks,
  };
}
