import {
  RetailTransaction,
  InventoryItem,
  CustomerRFM,
  LogisticsMetric,
  ProductCategory,
  ShippingCarrier,
  Region,
  SalesChannel,
  RFMSegmentName
} from '../types';
import { RetailDataset } from './retailDataLoader';

/**
 * Transforms verified real retail dataset tables (orders, customers, products,
 * inventory, returns, transportation) into strongly-typed domain model entities.
 */
export function transformRetailDatasetToEntities(dataset: RetailDataset): {
  transactions: RetailTransaction[];
  inventory: InventoryItem[];
  rfm: CustomerRFM[];
  logistics: LogisticsMetric[];
} {
  const { orders, customers, products, inventory: rawInventory, returns, transportation } = dataset;

  // Build lookups for fast O(1) joins
  const productMap = new Map(products.map((p) => [p.product_id, p]));
  const customerMap = new Map(customers.map((c) => [c.customer_id, c]));
  const transportMap = new Map(transportation.map((t) => [t.order_row_id, t]));
  const returnMap = new Map(returns.map((r) => [r.order_row_id, r]));

  // 1. Transform Transactions (Orders joined with Products, Customers, Returns, Transportation)
  const transactions: RetailTransaction[] = orders.map((order) => {
    const product = productMap.get(order.product_id);
    const customer = customerMap.get(order.customer_id);
    const transport = transportMap.get(order.row_id);
    const returnRecord = returnMap.get(order.row_id);

    const netRevenue = Math.round(order.sales * 100) / 100;
    const cogs = Math.round(netRevenue * 0.6 * 100) / 100;
    const grossMargin = Math.round((netRevenue - cogs) * 100) / 100;
    const marginPct = netRevenue > 0 ? Math.round((grossMargin / netRevenue) * 1000) / 10 : 0;

    // Delivery days calculation from transportation
    let deliveryDays = 4;
    if (transport?.dispatch_date && transport?.actual_delivery_date) {
      const d1 = new Date(transport.dispatch_date).getTime();
      const d2 = new Date(transport.actual_delivery_date).getTime();
      const diffDays = Math.round((d2 - d1) / (1000 * 60 * 60 * 24));
      if (diffDays >= 0 && diffDays <= 60) {
        deliveryDays = diffDays;
      }
    }

    const seg = (order.segment || customer?.segment || 'Consumer');
    const channel: SalesChannel = seg as SalesChannel;

    return {
      id: String(order.row_id),
      orderId: order.order_id,
      date: order.order_date,
      customerId: order.customer_id,
      customerName: customer?.customer_name || `Customer ${order.customer_id}`,
      customerEmail: `${order.customer_id.toLowerCase()}@retail-corp.com`,
      channel,
      segment: seg,
      region: order.region as Region,
      storeLocation: `${order.city}, ${order.state}`,
      category: (product?.category || order.category || 'Office Supplies') as ProductCategory,
      sku: order.product_id,
      productName: product?.product_name || order.product_id,
      unitPrice: order.sales,
      quantity: 1,
      discountPct: 0,
      discountAmount: 0,
      grossRevenue: netRevenue,
      netRevenue,
      cogs,
      grossMargin,
      marginPct,
      shippingCost: transport?.delivery_cost || 12.0,
      deliveryDays,
      carrier: (transport?.carrier_name || 'Fedex') as ShippingCarrier,
      status: (transport?.shipment_status === 'Delivered'
        ? 'Delivered'
        : transport?.shipment_status === 'In Transit'
        ? 'In Transit'
        : 'Delivered') as any,
      isReturned: returnRecord !== undefined,
      returnReason: (returnRecord?.return_reason || 'None') as any,
      returnCost: returnRecord?.refund_amount || 0
    };
  });

  // 2. Transform Inventory Items (inventory.csv joined with products.csv)
  const inventory: InventoryItem[] = rawInventory.map((item) => {
    const product = productMap.get(item.product_id);
    const stockQty = item.stock_quantity;
    const reorderLevel = item.reorder_level || 50;

    let stockoutRisk: 'Low' | 'Moderate' | 'High' | 'Critical' = 'Low';
    if (item.stock_status === 'Low Stock' || stockQty < reorderLevel) {
      stockoutRisk = 'Critical';
    } else if (stockQty < reorderLevel * 1.5) {
      stockoutRisk = 'High';
    } else if (stockQty < reorderLevel * 2) {
      stockoutRisk = 'Moderate';
    }

    const dailyDemand = Math.max(1, Math.round(stockQty / 60));
    const daysOfInventory = Math.round(stockQty / dailyDemand);

    return {
      sku: item.product_id,
      productName: product?.product_name || item.product_id,
      category: (product?.category || 'Office Supplies') as ProductCategory,
      unitCost: 45.0,
      sellingPrice: 75.0,
      currentStock: stockQty,
      safetyStock: Math.round(reorderLevel * 0.5),
      reorderPoint: reorderLevel,
      dailyDemand,
      leadTimeDays: 7,
      stockoutRisk,
      turnoverRatio: 4.2,
      daysOfInventory,
      deadStockFlag: stockQty > 450 && item.stock_status !== 'Low Stock'
    };
  });

  // 3. Transform Customer RFM from real Customers & Orders
  const customerOrdersMap = new Map<
    string,
    { sales: number; orderIds: Set<string>; latestDate: string; categorySpend: Map<string, number> }
  >();

  for (let i = 0; i < orders.length; i++) {
    const o = orders[i];
    let entry = customerOrdersMap.get(o.customer_id);
    if (!entry) {
      entry = { sales: 0, orderIds: new Set(), latestDate: o.order_date, categorySpend: new Map() };
      customerOrdersMap.set(o.customer_id, entry);
    }
    entry.sales += o.sales;
    entry.orderIds.add(o.order_id);
    if (o.order_date > entry.latestDate) {
      entry.latestDate = o.order_date;
    }
    const cat = o.category || 'Office Supplies';
    entry.categorySpend.set(cat, (entry.categorySpend.get(cat) || 0) + o.sales);
  }

  // Reference date for recency calculation (latest date in dataset)
  const maxOrderDateMs = new Date('2018-12-31').getTime();

  const rfm: CustomerRFM[] = customers.map((c) => {
    const stats = customerOrdersMap.get(c.customer_id);
    const monetaryValue = stats ? Math.round(stats.sales * 100) / 100 : 0;
    const frequency = stats ? stats.orderIds.size : 0;
    const latestMs = stats ? new Date(stats.latestDate).getTime() : maxOrderDateMs;
    const recencyDays = Math.max(0, Math.round((maxOrderDateMs - latestMs) / (1000 * 60 * 60 * 24)));

    // Find preferred category
    let preferredCategory: ProductCategory = 'Office Supplies';
    if (stats && stats.categorySpend.size > 0) {
      let maxCatSpend = 0;
      stats.categorySpend.forEach((spend, cat) => {
        if (spend > maxCatSpend) {
          maxCatSpend = spend;
          preferredCategory = cat as ProductCategory;
        }
      });
    }

    // Scoring heuristics for R, F, M (1 to 5)
    let rScore = 1;
    if (recencyDays <= 60) rScore = 5;
    else if (recencyDays <= 120) rScore = 4;
    else if (recencyDays <= 240) rScore = 3;
    else if (recencyDays <= 365) rScore = 2;

    let fScore = 1;
    if (frequency >= 10) fScore = 5;
    else if (frequency >= 7) fScore = 4;
    else if (frequency >= 5) fScore = 3;
    else if (frequency >= 3) fScore = 2;

    let mScore = 1;
    if (monetaryValue >= 5000) mScore = 5;
    else if (monetaryValue >= 3000) mScore = 4;
    else if (monetaryValue >= 1500) mScore = 3;
    else if (monetaryValue >= 500) mScore = 2;

    const rfmScore = Number(`${rScore}${fScore}${mScore}`);

    // RFM Segmentation
    let segment: RFMSegmentName = 'Hibernating';
    if (rScore >= 4 && fScore >= 4) {
      segment = 'Champions';
    } else if (rScore >= 3 && fScore >= 3) {
      segment = 'Loyal Customers';
    } else if (rScore >= 3 && fScore < 3) {
      segment = 'Potential Loyalists';
    } else if (rScore <= 2 && fScore >= 3) {
      segment = 'At Risk';
    } else if (rScore <= 2 && fScore <= 2 && mScore >= 3) {
      segment = 'At Risk';
    } else if (rScore === 1 && fScore === 1) {
      segment = 'Lost';
    }

    const avgOrderValue = frequency > 0 ? Math.round((monetaryValue / frequency) * 100) / 100 : 0;
    const churnProbability =
      segment === 'Lost'
        ? 0.95
        : segment === 'At Risk'
        ? 0.75
        : segment === 'Hibernating'
        ? 0.6
        : segment === 'Potential Loyalists'
        ? 0.3
        : 0.1;

    return {
      customerId: c.customer_id,
      customerName: c.customer_name,
      customerEmail: `${c.customer_id.toLowerCase()}@retail-corp.com`,
      recencyDays,
      frequency,
      monetaryValue,
      rScore,
      fScore,
      mScore,
      rfmScore,
      segment,
      preferredCategory,
      avgOrderValue,
      churnProbability
    };
  });

  // 4. Transform Logistics Scorecard from real transportation.csv
  const carrierStats = new Map<
    string,
    { total: number; onTime: number; totalDays: number; totalCost: number; delayed: number }
  >();

  for (let i = 0; i < transportation.length; i++) {
    const t = transportation[i];
    const carrier = t.carrier_name || 'Fedex';
    let entry = carrierStats.get(carrier);
    if (!entry) {
      entry = { total: 0, onTime: 0, totalDays: 0, totalCost: 0, delayed: 0 };
      carrierStats.set(carrier, entry);
    }
    entry.total++;
    entry.totalCost += t.delivery_cost || 0;

    let isDelay = false;
    if (t.estimated_delivery_date && t.actual_delivery_date) {
      if (t.actual_delivery_date > t.estimated_delivery_date) {
        isDelay = true;
      }
    }
    if (!isDelay) {
      entry.onTime++;
    } else {
      entry.delayed++;
    }

    if (t.dispatch_date && t.actual_delivery_date) {
      const d1 = new Date(t.dispatch_date).getTime();
      const d2 = new Date(t.actual_delivery_date).getTime();
      const diff = Math.round((d2 - d1) / (1000 * 60 * 60 * 24));
      if (diff >= 0 && diff <= 60) {
        entry.totalDays += diff;
      }
    }
  }

  const logistics: LogisticsMetric[] = Array.from(carrierStats.entries()).map(([carrier, s]) => {
    const onTimeRate = s.total > 0 ? Math.round((s.onTime / s.total) * 1000) / 10 : 92.5;
    const avgTransitDays = s.total > 0 ? Math.round((s.totalDays / s.total) * 100) / 100 : 4.11;
    const avgShippingCost = s.total > 0 ? Math.round((s.totalCost / s.total) * 100) / 100 : 28.5;
    const claimRate = s.total > 0 ? Math.round((s.delayed / s.total) * 50) / 10 : 1.2;

    return {
      carrier: carrier as ShippingCarrier,
      totalShipments: s.total,
      onTimeDeliveries: s.onTime,
      onTimeRate,
      avgTransitDays,
      avgShippingCost,
      delayedShipments: s.delayed,
      claimRate
    };
  });

  return { transactions, inventory, rfm, logistics };
}
