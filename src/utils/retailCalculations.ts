import { RetailTransaction, CustomerRFM, InventoryItem, LogisticsMetric } from '../types';

/**
 * Reusable retail analytical calculation engine.
 * All metrics are derived purely from underlying transactional records.
 * No hardcoded values or synthetic calibration.
 */

export interface RetailKPIs {
  totalSales: number;
  grossSales: number;
  totalDiscounts: number;
  discountRate: number;
  totalOrders: number;
  totalCustomers: number;
  totalQuantity: number;
  aov: number;
  totalProfit: number;
  profitMargin: number;
  totalReturns: number;
  returnRate: number;
  totalReturnCost: number;
  avgDeliveryDays: number;
  onTimeDeliveryRate: number;
  avgBasketSize: number;
}

export interface MonthlyTrend {
  date: string;
  label: string;
  revenue: number;
  profit: number;
  orders: number;
  units: number;
  discount: number;
  marginPct: number;
}

export interface CategoryMetric {
  category: string;
  revenue: number;
  profit: number;
  marginPct: number;
  orders: number;
  units: number;
  returns: number;
  returnRate: number;
}

export interface ChannelMetric {
  channel: string;
  revenue: number;
  profit: number;
  orders: number;
  marginPct: number;
  discounts: number;
}

export interface RegionalMetric {
  region: string;
  revenue: number;
  profit: number;
  orders: number;
  marginPct: number;
}

export interface ProductMetric {
  sku: string;
  name: string;
  category: string;
  sales: number;
  profit: number;
  units: number;
  orders: number;
  returns: number;
  returnRate: number;
  marginPct: number;
}

export interface ReturnReasonMetric {
  name: string;
  value: number;
  pct: number;
}

export interface CarrierScorecardMetric {
  carrier: string;
  totalShipments: number;
  delivered: number;
  delayed: number;
  inTransit: number;
  cancelled: number;
  onTimeRate: number;
  avgTransitDays: number;
  avgShippingCost: number;
}

// 1. Total Sales / Revenue
export function calculateTotalSales(transactions: RetailTransaction[]): number {
  return transactions.reduce((acc, t) => acc + (t.netRevenue ?? t.grossRevenue ?? 0), 0);
}

// 2. Total Orders (distinct orderId if present, else row count)
export function calculateTotalOrders(transactions: RetailTransaction[]): number {
  if (transactions.length === 0) return 0;
  const orderIds = new Set(transactions.map((t) => t.orderId || t.id));
  return orderIds.size;
}

// 3. Total Customers (distinct customerId)
export function calculateTotalCustomers(transactions: RetailTransaction[]): number {
  if (transactions.length === 0) return 0;
  const customerIds = new Set(transactions.map((t) => t.customerId).filter(Boolean));
  return customerIds.size;
}

// 4. Total Quantity Sold
export function calculateTotalQuantity(transactions: RetailTransaction[]): number {
  return transactions.reduce((acc, t) => acc + (t.quantity || 0), 0);
}

// 5. Average Order Value (AOV)
export function calculateAverageOrderValue(transactions: RetailTransaction[]): number {
  const orders = calculateTotalOrders(transactions);
  if (orders === 0) return 0;
  const sales = calculateTotalSales(transactions);
  return Math.round((sales / orders) * 100) / 100;
}

// 6. Total Profit (Gross Margin)
export function calculateTotalProfit(transactions: RetailTransaction[]): number {
  return transactions.reduce((acc, t) => {
    if (t.grossMargin !== undefined) return acc + t.grossMargin;
    const rev = t.netRevenue ?? t.grossRevenue ?? 0;
    const cogs = t.cogs ?? 0;
    return acc + (rev - cogs);
  }, 0);
}

// 7. Profit Margin Percentage
export function calculateProfitMargin(transactions: RetailTransaction[]): number {
  const sales = calculateTotalSales(transactions);
  if (sales === 0) return 0;
  const profit = calculateTotalProfit(transactions);
  return Math.round((profit / sales) * 10000) / 100;
}

// 8. Total Returns
export function calculateTotalReturns(transactions: RetailTransaction[]): number {
  return transactions.filter((t) => t.isReturned).length;
}

// 9. Return Rate Percentage
export function calculateReturnRate(transactions: RetailTransaction[]): number {
  const orders = calculateTotalOrders(transactions);
  if (orders === 0) return 0;
  const returns = calculateTotalReturns(transactions);
  return Math.round((returns / orders) * 10000) / 100;
}

// 10. Average Delivery Days
export function calculateAverageDeliveryDays(transactions: RetailTransaction[]): number {
  const withDelivery = transactions.filter((t) => typeof t.deliveryDays === 'number' && t.deliveryDays > 0);
  if (withDelivery.length === 0) return 0;
  const sum = withDelivery.reduce((acc, t) => acc + (t.deliveryDays || 0), 0);
  return Math.round((sum / withDelivery.length) * 100) / 100;
}

// 11. On-Time Delivery Rate
export function calculateOnTimeDeliveryRate(transactions: RetailTransaction[]): number {
  if (transactions.length === 0) return 0;
  const delivered = transactions.filter((t) => t.status === 'Delivered').length;
  const total = transactions.length;
  return Math.round((delivered / total) * 10000) / 100;
}

// Comprehensive KPI calculation
export function calculateRetailKPIs(transactions: RetailTransaction[]): RetailKPIs {
  const totalOrders = calculateTotalOrders(transactions);
  const totalSales = calculateTotalSales(transactions);
  const grossSales = transactions.reduce((acc, t) => acc + (t.grossRevenue ?? t.netRevenue ?? 0), 0);
  const totalDiscounts = transactions.reduce((acc, t) => acc + (t.discountAmount ?? 0), 0);
  const discountRate = grossSales > 0 ? Math.round((totalDiscounts / grossSales) * 10000) / 100 : 0;
  const totalCustomers = calculateTotalCustomers(transactions);
  const totalQuantity = calculateTotalQuantity(transactions);
  const aov = totalOrders > 0 ? Math.round((totalSales / totalOrders) * 100) / 100 : 0;
  const totalProfit = calculateTotalProfit(transactions);
  const profitMargin = totalSales > 0 ? Math.round((totalProfit / totalSales) * 10000) / 100 : 0;
  const totalReturns = calculateTotalReturns(transactions);
  const returnRate = totalOrders > 0 ? Math.round((totalReturns / totalOrders) * 10000) / 100 : 0;
  const totalReturnCost = transactions
    .filter((t) => t.isReturned)
    .reduce((acc, t) => acc + (t.returnCost || 0) + (t.netRevenue || 0), 0);
  const avgDeliveryDays = calculateAverageDeliveryDays(transactions);
  const onTimeDeliveryRate = calculateOnTimeDeliveryRate(transactions);
  const avgBasketSize = totalOrders > 0 ? Math.round((totalQuantity / totalOrders) * 100) / 100 : 0;

  return {
    totalSales,
    grossSales,
    totalDiscounts,
    discountRate,
    totalOrders,
    totalCustomers,
    totalQuantity,
    aov,
    totalProfit,
    profitMargin,
    totalReturns,
    returnRate,
    totalReturnCost,
    avgDeliveryDays,
    onTimeDeliveryRate,
    avgBasketSize
  };
}

// Group by Month dynamically
export function calculateMonthlyTrends(transactions: RetailTransaction[]): MonthlyTrend[] {
  const monthMap: Record<string, { revenue: number; profit: number; orders: Set<string>; units: number; discount: number }> = {};

  transactions.forEach((t) => {
    const rawDate = t.date || '2024-01-01';
    // Format YYYY-MM
    const ym = rawDate.slice(0, 7);
    if (!monthMap[ym]) {
      monthMap[ym] = {
        revenue: 0,
        profit: 0,
        orders: new Set(),
        units: 0,
        discount: 0
      };
    }
    monthMap[ym].revenue += t.netRevenue || 0;
    monthMap[ym].profit += t.grossMargin !== undefined ? t.grossMargin : (t.netRevenue || 0) - (t.cogs || 0);
    monthMap[ym].orders.add(t.orderId || t.id);
    monthMap[ym].units += t.quantity || 1;
    monthMap[ym].discount += t.discountAmount || 0;
  });

  const sortedMonths = Object.keys(monthMap).sort();

  return sortedMonths.map((ym) => {
    const data = monthMap[ym];
    const d = new Date(`${ym}-01`);
    const label = !isNaN(d.getTime()) ? d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }) : ym;
    const rev = Math.round(data.revenue);
    const prof = Math.round(data.profit);
    const marginPct = rev > 0 ? Math.round((prof / rev) * 1000) / 10 : 0;
    return {
      date: ym,
      label,
      revenue: rev,
      profit: prof,
      orders: data.orders.size,
      units: data.units,
      discount: Math.round(data.discount),
      marginPct
    };
  });
}

// Group by Category dynamically
export function calculateCategoryPerformance(transactions: RetailTransaction[]): CategoryMetric[] {
  const catMap: Record<string, { revenue: number; profit: number; orders: Set<string>; units: number; returns: number }> = {};

  transactions.forEach((t) => {
    const cat = t.category || 'General';
    if (!catMap[cat]) {
      catMap[cat] = { revenue: 0, profit: 0, orders: new Set(), units: 0, returns: 0 };
    }
    catMap[cat].revenue += t.netRevenue || 0;
    catMap[cat].profit += t.grossMargin !== undefined ? t.grossMargin : (t.netRevenue || 0) - (t.cogs || 0);
    catMap[cat].orders.add(t.orderId || t.id);
    catMap[cat].units += t.quantity || 1;
    if (t.isReturned) catMap[cat].returns += 1;
  });

  return Object.keys(catMap).map((cat) => {
    const item = catMap[cat];
    const revenue = Math.round(item.revenue);
    const profit = Math.round(item.profit);
    const marginPct = revenue > 0 ? Math.round((profit / revenue) * 1000) / 10 : 0;
    const totalOrders = item.orders.size;
    const returnRate = totalOrders > 0 ? Math.round((item.returns / totalOrders) * 1000) / 10 : 0;

    return {
      category: cat,
      revenue,
      profit,
      marginPct,
      orders: totalOrders,
      units: item.units,
      returns: item.returns,
      returnRate
    };
  }).sort((a, b) => b.revenue - a.revenue);
}

// Group by Channel dynamically
export function calculateChannelPerformance(transactions: RetailTransaction[]): ChannelMetric[] {
  const channelMap: Record<string, { revenue: number; profit: number; orders: Set<string>; discounts: number }> = {};

  transactions.forEach((t) => {
    const ch = t.channel || 'Other';
    if (!channelMap[ch]) {
      channelMap[ch] = { revenue: 0, profit: 0, orders: new Set(), discounts: 0 };
    }
    channelMap[ch].revenue += t.netRevenue || 0;
    channelMap[ch].profit += t.grossMargin !== undefined ? t.grossMargin : (t.netRevenue || 0) - (t.cogs || 0);
    channelMap[ch].orders.add(t.orderId || t.id);
    channelMap[ch].discounts += t.discountAmount || 0;
  });

  return Object.keys(channelMap).map((ch) => {
    const item = channelMap[ch];
    const revenue = Math.round(item.revenue);
    const profit = Math.round(item.profit);
    const marginPct = revenue > 0 ? Math.round((profit / revenue) * 1000) / 10 : 0;

    return {
      channel: ch,
      revenue,
      profit,
      orders: item.orders.size,
      marginPct,
      discounts: Math.round(item.discounts)
    };
  }).sort((a, b) => b.revenue - a.revenue);
}

// Group by Region dynamically
export function calculateRegionalPerformance(transactions: RetailTransaction[]): RegionalMetric[] {
  const regionMap: Record<string, { revenue: number; profit: number; orders: Set<string> }> = {};

  transactions.forEach((t) => {
    const reg = t.region || 'Other';
    if (!regionMap[reg]) {
      regionMap[reg] = { revenue: 0, profit: 0, orders: new Set() };
    }
    regionMap[reg].revenue += t.netRevenue || 0;
    regionMap[reg].profit += t.grossMargin !== undefined ? t.grossMargin : (t.netRevenue || 0) - (t.cogs || 0);
    regionMap[reg].orders.add(t.orderId || t.id);
  });

  return Object.keys(regionMap).map((reg) => {
    const item = regionMap[reg];
    const revenue = Math.round(item.revenue);
    const profit = Math.round(item.profit);
    const marginPct = revenue > 0 ? Math.round((profit / revenue) * 1000) / 10 : 0;

    return {
      region: reg,
      revenue,
      profit,
      orders: item.orders.size,
      marginPct
    };
  }).sort((a, b) => b.revenue - a.revenue);
}

// Top Products dynamically
export function calculateTopProducts(transactions: RetailTransaction[], limit = 5): ProductMetric[] {
  const prodMap: Record<string, { sku: string; name: string; category: string; sales: number; profit: number; units: number; orders: Set<string>; returns: number }> = {};

  transactions.forEach((t) => {
    const key = t.sku || t.productName;
    if (!prodMap[key]) {
      prodMap[key] = {
        sku: t.sku || 'SKU',
        name: t.productName || 'Product',
        category: t.category || 'General',
        sales: 0,
        profit: 0,
        units: 0,
        orders: new Set(),
        returns: 0
      };
    }
    prodMap[key].sales += t.netRevenue || 0;
    prodMap[key].profit += t.grossMargin !== undefined ? t.grossMargin : (t.netRevenue || 0) - (t.cogs || 0);
    prodMap[key].units += t.quantity || 1;
    prodMap[key].orders.add(t.orderId || t.id);
    if (t.isReturned) prodMap[key].returns += 1;
  });

  return Object.values(prodMap)
    .map((p) => {
      const sales = Math.round(p.sales);
      const profit = Math.round(p.profit);
      const marginPct = sales > 0 ? Math.round((profit / sales) * 1000) / 10 : 0;
      const totalOrders = p.orders.size;
      const returnRate = totalOrders > 0 ? Math.round((p.returns / totalOrders) * 1000) / 10 : 0;

      return {
        sku: p.sku,
        name: p.name,
        category: p.category,
        sales,
        profit,
        units: p.units,
        orders: totalOrders,
        returns: p.returns,
        returnRate,
        marginPct
      };
    })
    .sort((a, b) => b.sales - a.sales)
    .slice(0, limit);
}

// Return Reasons dynamically
export function calculateReturnReasons(transactions: RetailTransaction[]): ReturnReasonMetric[] {
  const returns = transactions.filter((t) => t.isReturned);
  const total = returns.length;
  if (total === 0) return [];

  const reasonMap: Record<string, number> = {};
  returns.forEach((t) => {
    const r = t.returnReason || 'Other';
    reasonMap[r] = (reasonMap[r] || 0) + 1;
  });

  return Object.entries(reasonMap).map(([name, count]) => ({
    name,
    value: count,
    pct: Math.round((count / total) * 1000) / 10
  })).sort((a, b) => b.value - a.value);
}

// Carrier Scorecard dynamically
export function calculateCarrierScorecard(transactions: RetailTransaction[]): CarrierScorecardMetric[] {
  const carrierMap: Record<string, {
    total: number;
    delivered: number;
    delayed: number;
    inTransit: number;
    cancelled: number;
    totalDays: number;
    deliveryCount: number;
    totalCost: number;
  }> = {};

  transactions.forEach((t) => {
    const c = t.carrier || 'Standard Carrier';
    if (!carrierMap[c]) {
      carrierMap[c] = {
        total: 0,
        delivered: 0,
        delayed: 0,
        inTransit: 0,
        cancelled: 0,
        totalDays: 0,
        deliveryCount: 0,
        totalCost: 0
      };
    }
    const item = carrierMap[c];
    item.total += 1;
    item.totalCost += t.shippingCost || 0;
    if (t.deliveryDays) {
      item.totalDays += t.deliveryDays;
      item.deliveryCount += 1;
    }
    if (t.status === 'Delivered') item.delivered += 1;
    else if (t.status === 'Delayed') item.delayed += 1;
    else if (t.status === 'In Transit') item.inTransit += 1;
    else if (t.status === 'Cancelled') item.cancelled += 1;
  });

  return Object.entries(carrierMap).map(([carrier, data]) => {
    const onTimeRate = data.total > 0 ? Math.round((data.delivered / data.total) * 1000) / 10 : 0;
    const avgTransitDays = data.deliveryCount > 0 ? Math.round((data.totalDays / data.deliveryCount) * 10) / 10 : 0;
    const avgShippingCost = data.total > 0 ? Math.round((data.totalCost / data.total) * 100) / 100 : 0;

    return {
      carrier,
      totalShipments: data.total,
      delivered: data.delivered,
      delayed: data.delayed,
      inTransit: data.inTransit,
      cancelled: data.cancelled,
      onTimeRate,
      avgTransitDays,
      avgShippingCost
    };
  }).sort((a, b) => b.totalShipments - a.totalShipments);
}
