import {
  RetailTransaction,
  InventoryItem,
  CustomerRFM,
  LogisticsMetric,
  PythonScriptMetadata,
  SalesChannel,
  Region,
  ProductCategory,
  ShippingCarrier,
  OrderStatus,
  ReturnReason
} from '../types';

export const CHANNELS: SalesChannel[] = ['Online', 'Retail Store', 'Marketplace', 'B2B Wholesale'];
export const REGIONS: Region[] = ['North America', 'Europe', 'Asia Pacific', 'Latin America'];
export const CATEGORIES: ProductCategory[] = [
  'Electronics',
  'Apparel & Footwear',
  'Home & Living',
  'Beauty & Health',
  'Sports & Outdoors'
];
export const CARRIERS: ShippingCarrier[] = ['FedEx', 'UPS', 'DHL Express', 'USPS', 'OnTrac'];

// Base catalog of products
export const PRODUCT_CATALOG: {
  sku: string;
  name: string;
  category: ProductCategory;
  basePrice: number;
  baseCogs: number;
  dailyDemand: number;
  leadTime: number;
}[] = [
  { sku: 'ELE-1001', name: 'UltraHD 4K Noise-Canceling Headphones', category: 'Electronics', basePrice: 299.99, baseCogs: 135.00, dailyDemand: 18, leadTime: 7 },
  { sku: 'ELE-1002', name: 'Pro Smartwatch Series 6 with ECG', category: 'Electronics', basePrice: 349.00, baseCogs: 160.00, dailyDemand: 22, leadTime: 10 },
  { sku: 'ELE-1003', name: 'Ergonomic Mechanical Wireless Keyboard', category: 'Electronics', basePrice: 129.50, baseCogs: 52.00, dailyDemand: 14, leadTime: 5 },
  { sku: 'ELE-1004', name: 'Thunderbolt 4 Docking Station 12-in-1', category: 'Electronics', basePrice: 199.95, baseCogs: 88.00, dailyDemand: 9, leadTime: 12 },
  { sku: 'ELE-1005', name: '4K Ultra-Wide Curved Monitor 34-Inch', category: 'Electronics', basePrice: 599.00, baseCogs: 290.00, dailyDemand: 6, leadTime: 14 },
  { sku: 'APP-2001', name: 'Merino Wool Thermal Performance Knit', category: 'Apparel & Footwear', basePrice: 89.00, baseCogs: 31.00, dailyDemand: 25, leadTime: 6 },
  { sku: 'APP-2002', name: 'All-Weather Waterproof Trail Runner Shoes', category: 'Apparel & Footwear', basePrice: 145.00, baseCogs: 55.00, dailyDemand: 30, leadTime: 8 },
  { sku: 'APP-2003', name: 'Seamless High-Waist Athletic Leggings', category: 'Apparel & Footwear', basePrice: 68.00, baseCogs: 22.00, dailyDemand: 35, leadTime: 4 },
  { sku: 'APP-2004', name: 'Classic Tailored Tech Trench Coat', category: 'Apparel & Footwear', basePrice: 240.00, baseCogs: 95.00, dailyDemand: 8, leadTime: 15 },
  { sku: 'APP-2005', name: 'Breathable Bamboo Crew Tee (3-Pack)', category: 'Apparel & Footwear', basePrice: 54.00, baseCogs: 18.00, dailyDemand: 42, leadTime: 5 },
  { sku: 'HOM-3001', name: 'Aroma Ceramic Ultrasonic Diffuser', category: 'Home & Living', basePrice: 48.00, baseCogs: 16.50, dailyDemand: 20, leadTime: 7 },
  { sku: 'HOM-3002', name: 'Linen Washed Duvet Cover King Set', category: 'Home & Living', basePrice: 175.00, baseCogs: 68.00, dailyDemand: 11, leadTime: 9 },
  { sku: 'HOM-3003', name: 'Cast Iron Enamel Dutch Oven 5.5 Qt', category: 'Home & Living', basePrice: 129.00, baseCogs: 48.00, dailyDemand: 13, leadTime: 11 },
  { sku: 'HOM-3004', name: 'Smart Robot Vacuum & Mop Combo', category: 'Home & Living', basePrice: 420.00, baseCogs: 195.00, dailyDemand: 10, leadTime: 14 },
  { sku: 'BEA-4001', name: 'Botanical Hyaluronic Acid Hydrating Serum', category: 'Beauty & Health', basePrice: 42.00, baseCogs: 9.50, dailyDemand: 45, leadTime: 4 },
  { sku: 'BEA-4002', name: 'Retinol Renewal Night Cream 50ml', category: 'Beauty & Health', basePrice: 58.00, baseCogs: 14.00, dailyDemand: 38, leadTime: 5 },
  { sku: 'BEA-4003', name: 'Sonic Facial Cleansing System', category: 'Beauty & Health', basePrice: 95.00, baseCogs: 32.00, dailyDemand: 16, leadTime: 8 },
  { sku: 'SPO-5001', name: 'Adjustable Quick-Select Dumbbell 50lb Pair', category: 'Sports & Outdoors', basePrice: 320.00, baseCogs: 145.00, dailyDemand: 12, leadTime: 10 },
  { sku: 'SPO-5002', name: 'Ultralight 2-Person Backpacking Tent', category: 'Sports & Outdoors', basePrice: 215.00, baseCogs: 89.00, dailyDemand: 7, leadTime: 12 },
  { sku: 'SPO-5003', name: 'Hydro Insulated Stainless Steel Bottle 32oz', category: 'Sports & Outdoors', basePrice: 38.00, baseCogs: 11.50, dailyDemand: 50, leadTime: 3 }
];

export const CUSTOMER_NAMES = [
  'Sophia Chen', 'Liam Vance', 'Olivia Martinez', 'Ethan Brooks', 'Ava Robinson',
  'Noah Patel', 'Emma Wright', 'Jackson Reed', 'Mia Tanaka', 'Lucas Hughes',
  'Isabella Rossi', 'Oliver Kim', 'Charlotte Dubois', 'Benjamin Hayes', 'Amelia Ward',
  'Henry Jenkins', 'Harper Cooper', 'Alexander Bell', 'Evelyn Scott', 'Daniel Foster',
  'Abigail Morales', 'James Bennett', 'Emily Powell', 'Sebastian Ortiz', 'Ella Henderson',
  'Logan Fisher', 'Scarlett Rivera', 'David Barnes', 'Chloe Simmons', 'Carter Ross'
];

// Generator function for rich retail transactions
function generateTransactions(): RetailTransaction[] {
  const transactions: RetailTransaction[] = [];
  const baseDate = new Date('2024-01-01');
  const daysTotal = 365 + 180; // 1.5 years of transactional depth

  // Deterministic seed PRNG
  let seed = 42891;
  function random() {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
  }

  const stores = [
    'Downtown Flagship (NYC)', 'Westfield Mall (London)', 'Shibuya Crossing (Tokyo)',
    'Michigan Ave (Chicago)', 'Pacific Centre (Vancouver)', 'Galeries Lafayette (Paris)',
    'Union Square (SF)', 'Sydney CBD Store'
  ];

  for (let i = 1; i <= 600; i++) {
    const dayOffset = Math.floor(random() * daysTotal);
    const orderDate = new Date(baseDate.getTime() + dayOffset * 86400000);
    const dateStr = orderDate.toISOString().split('T')[0];

    const prod = PRODUCT_CATALOG[Math.floor(random() * PRODUCT_CATALOG.length)];
    const custIdx = Math.floor(random() * CUSTOMER_NAMES.length);
    const custName = CUSTOMER_NAMES[custIdx];
    const custId = `CUST-${1000 + custIdx}`;
    const custEmail = `${custName.toLowerCase().replace(' ', '.')}@example.com`;

    const channel = CHANNELS[Math.floor(random() * CHANNELS.length)];
    const region = REGIONS[Math.floor(random() * REGIONS.length)];
    const store = channel === 'Retail Store' ? stores[Math.floor(random() * stores.length)] : 'Online Fulfillment Center';

    const quantity = Math.floor(random() * 3) + 1;
    // Discount probability higher on Marketplace or during Q4
    const month = orderDate.getMonth();
    const isHolidaySeason = month === 10 || month === 11;
    const discountRates = [0, 0, 0.05, 0.10, 0.15, 0.20, 0.25];
    const discountPct = isHolidaySeason ? (random() > 0.4 ? 0.20 : 0.10) : discountRates[Math.floor(random() * discountRates.length)];

    const unitPrice = prod.basePrice;
    const grossRevenue = Math.round(unitPrice * quantity * 100) / 100;
    const discountAmount = Math.round(grossRevenue * discountPct * 100) / 100;
    const netRevenue = Math.round((grossRevenue - discountAmount) * 100) / 100;
    const cogs = Math.round(prod.baseCogs * quantity * 100) / 100;
    const grossMargin = Math.round((netRevenue - cogs) * 100) / 100;
    const marginPct = Math.round((grossMargin / netRevenue) * 1000) / 10;

    const carrier = CARRIERS[Math.floor(random() * CARRIERS.length)];
    const shippingCost = Math.round((8.50 + random() * 14.50) * 100) / 100;
    const deliveryDays = Math.floor(random() * 5) + 2;
    
    // Status
    const statusRoll = random();
    let status: OrderStatus = 'Delivered';
    if (statusRoll < 0.04) status = 'Cancelled';
    else if (statusRoll < 0.10) status = 'Delayed';
    else if (statusRoll < 0.18) status = 'In Transit';

    // Returns: Apparel has higher return rate (~18%), Electronics (~7%)
    let isReturned = false;
    let returnReason: ReturnReason = 'None';
    let returnCost = 0;

    const returnThreshold = prod.category === 'Apparel & Footwear' ? 0.22 : prod.category === 'Electronics' ? 0.09 : 0.06;
    if (status === 'Delivered' && random() < returnThreshold) {
      isReturned = true;
      const reasons: ReturnReason[] = [
        'Wrong Size / Fit',
        'Defective / Damaged',
        'Buyer Remorse',
        'Late Delivery',
        'Item Not as Pictured'
      ];
      returnReason = reasons[Math.floor(random() * reasons.length)];
      returnCost = Math.round((14 + random() * 18) * 100) / 100;
    }

    transactions.push({
      id: `TXN-${String(i).padStart(5, '0')}`,
      orderId: `ORD-${2024000 + i}`,
      date: dateStr,
      customerId: custId,
      customerName: custName,
      customerEmail: custEmail,
      channel,
      region,
      storeLocation: store,
      category: prod.category,
      sku: prod.sku,
      productName: prod.name,
      unitPrice,
      quantity,
      discountPct,
      discountAmount,
      grossRevenue,
      netRevenue,
      cogs,
      grossMargin,
      marginPct,
      shippingCost,
      deliveryDays,
      carrier,
      status,
      isReturned,
      returnReason,
      returnCost
    });
  }

  return transactions.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

export const INITIAL_TRANSACTIONS: RetailTransaction[] = generateTransactions();

// Pre-computed inventory items with replenishment models
export const INITIAL_INVENTORY: InventoryItem[] = PRODUCT_CATALOG.map((p, idx) => {
  const currentStock = Math.floor(30 + ((idx * 37) % 240));
  const dailyDemand = p.dailyDemand;
  const leadTimeDays = p.leadTime;
  const safetyStock = Math.ceil(dailyDemand * 3);
  const reorderPoint = Math.ceil(dailyDemand * leadTimeDays + safetyStock);
  
  let stockoutRisk: 'Low' | 'Moderate' | 'High' | 'Critical' = 'Low';
  if (currentStock <= safetyStock * 0.5) stockoutRisk = 'Critical';
  else if (currentStock <= reorderPoint) stockoutRisk = 'High';
  else if (currentStock <= reorderPoint * 1.3) stockoutRisk = 'Moderate';

  const daysOfInventory = Math.round((currentStock / dailyDemand) * 10) / 10;
  const turnoverRatio = Math.round(((dailyDemand * 365) / Math.max(1, currentStock)) * 10) / 10;
  const deadStockFlag = turnoverRatio < 2.5 && currentStock > 150;

  return {
    sku: p.sku,
    productName: p.name,
    category: p.category,
    unitCost: p.baseCogs,
    sellingPrice: p.basePrice,
    currentStock,
    safetyStock,
    reorderPoint,
    dailyDemand,
    leadTimeDays,
    stockoutRisk,
    turnoverRatio,
    daysOfInventory,
    deadStockFlag
  };
});

// RFM Segmentation calculation
export function computeRFMSegments(transactions: RetailTransaction[]): CustomerRFM[] {
  const customerMap = new Map<string, {
    name: string;
    email: string;
    lastDate: string;
    orders: Set<string>;
    totalSpend: number;
    categories: Record<string, number>;
  }>();

  const referenceDate = new Date('2025-06-30');

  transactions.forEach((tx) => {
    if (tx.status === 'Cancelled') return;
    const existing = customerMap.get(tx.customerId) || {
      name: tx.customerName,
      email: tx.customerEmail,
      lastDate: tx.date,
      orders: new Set<string>(),
      totalSpend: 0,
      categories: {}
    };

    if (new Date(tx.date) > new Date(existing.lastDate)) {
      existing.lastDate = tx.date;
    }
    existing.orders.add(tx.orderId);
    existing.totalSpend += tx.netRevenue;
    existing.categories[tx.category] = (existing.categories[tx.category] || 0) + 1;
    customerMap.set(tx.customerId, existing);
  });

  const list: CustomerRFM[] = [];

  customerMap.forEach((data, customerId) => {
    const recencyDays = Math.max(
      1,
      Math.floor((referenceDate.getTime() - new Date(data.lastDate).getTime()) / 86400000)
    );
    const frequency = data.orders.size;
    const monetaryValue = Math.round(data.totalSpend * 100) / 100;

    // Scores 1-5
    const rScore = recencyDays < 30 ? 5 : recencyDays < 75 ? 4 : recencyDays < 150 ? 3 : recencyDays < 250 ? 2 : 1;
    const fScore = frequency >= 12 ? 5 : frequency >= 8 ? 4 : frequency >= 5 ? 3 : frequency >= 3 ? 2 : 1;
    const mScore = monetaryValue > 4000 ? 5 : monetaryValue > 2500 ? 4 : monetaryValue > 1200 ? 3 : monetaryValue > 500 ? 2 : 1;
    const rfmScore = rScore * 100 + fScore * 10 + mScore;

    let segment: CustomerRFM['segment'] = 'Lost';
    if (rScore >= 4 && fScore >= 4 && mScore >= 4) segment = 'Champions';
    else if (rScore >= 3 && fScore >= 3) segment = 'Loyal Customers';
    else if (rScore >= 4 && fScore <= 2) segment = 'Potential Loyalists';
    else if (rScore <= 2 && fScore >= 3) segment = 'At Risk';
    else if (rScore <= 2 && fScore <= 2 && mScore >= 3) segment = 'Hibernating';
    else segment = 'Lost';

    // Find preferred category
    let topCat: ProductCategory = 'Electronics';
    let maxCount = 0;
    Object.entries(data.categories).forEach(([cat, cnt]) => {
      if (cnt > maxCount) {
        maxCount = cnt;
        topCat = cat as ProductCategory;
      }
    });

    const avgOrderValue = Math.round((monetaryValue / Math.max(1, frequency)) * 100) / 100;
    const churnProbability =
      segment === 'Champions'
        ? 0.05
        : segment === 'Loyal Customers'
        ? 0.18
        : segment === 'Potential Loyalists'
        ? 0.32
        : segment === 'At Risk'
        ? 0.65
        : segment === 'Hibernating'
        ? 0.82
        : 0.94;

    list.push({
      customerId,
      customerName: data.name,
      customerEmail: data.email,
      recencyDays,
      frequency,
      monetaryValue,
      rScore,
      fScore,
      mScore,
      rfmScore,
      segment,
      preferredCategory: topCat,
      avgOrderValue,
      churnProbability
    });
  });

  return list.sort((a, b) => b.monetaryValue - a.monetaryValue);
}

export const INITIAL_RFM: CustomerRFM[] = computeRFMSegments(INITIAL_TRANSACTIONS);

// Logistics scorecard per carrier
export const INITIAL_LOGISTICS: LogisticsMetric[] = [
  {
    carrier: 'FedEx',
    totalShipments: 184,
    onTimeDeliveries: 173,
    onTimeRate: 94.0,
    avgTransitDays: 2.8,
    avgShippingCost: 14.20,
    delayedShipments: 11,
    claimRate: 0.8
  },
  {
    carrier: 'UPS',
    totalShipments: 162,
    onTimeDeliveries: 149,
    onTimeRate: 92.0,
    avgTransitDays: 3.1,
    avgShippingCost: 13.85,
    delayedShipments: 13,
    claimRate: 1.1
  },
  {
    carrier: 'DHL Express',
    totalShipments: 115,
    onTimeDeliveries: 111,
    onTimeRate: 96.5,
    avgTransitDays: 2.2,
    avgShippingCost: 18.50,
    delayedShipments: 4,
    claimRate: 0.4
  },
  {
    carrier: 'USPS',
    totalShipments: 95,
    onTimeDeliveries: 82,
    onTimeRate: 86.3,
    avgTransitDays: 4.4,
    avgShippingCost: 9.10,
    delayedShipments: 13,
    claimRate: 2.3
  },
  {
    carrier: 'OnTrac',
    totalShipments: 44,
    onTimeDeliveries: 39,
    onTimeRate: 88.6,
    avgTransitDays: 3.5,
    avgShippingCost: 11.20,
    delayedShipments: 5,
    claimRate: 1.8
  }
];

// Price elasticity test points
export const ELASTICITY_BENCHMARKS = [
  {
    category: 'Technology',
    elasticityCoeff: -1.65,
    interpretation: 'Highly Elastic (Consumers react sharply to price increases on hardware and peripherals)',
    optimalDiscount: '10% - 15%',
    sampleSku: 'TEC-AC-10003033'
  },
  {
    category: 'Furniture',
    elasticityCoeff: -1.25,
    interpretation: 'Moderately Elastic (Planned commercial and residential furnishings)',
    optimalDiscount: '12% - 18%',
    sampleSku: 'FUR-BO-10001798'
  },
  {
    category: 'Office Supplies',
    elasticityCoeff: -0.85,
    interpretation: 'Relatively Inelastic (Essential day-to-day corporate consumables)',
    optimalDiscount: '5% - 8%',
    sampleSku: 'OFF-LA-10000240'
  },
  {
    category: 'Electronics',
    elasticityCoeff: -1.65,
    interpretation: 'Highly Elastic (Consumers react sharply to price increases)',
    optimalDiscount: '12% - 15%',
    sampleSku: 'ELE-1001'
  },
  {
    category: 'Apparel & Footwear',
    elasticityCoeff: -1.95,
    interpretation: 'Very Elastic (Strong substitute availability across competitors)',
    optimalDiscount: '20% - 25%',
    sampleSku: 'APP-2002'
  },
  {
    category: 'Home & Living',
    elasticityCoeff: -1.15,
    interpretation: 'Moderately Elastic (Planned purchases, brand driven)',
    optimalDiscount: '10% - 15%',
    sampleSku: 'HOM-3003'
  },
  {
    category: 'Beauty & Health',
    elasticityCoeff: -0.75,
    interpretation: 'Inelastic (High brand loyalty, routine replenishment)',
    optimalDiscount: '5% - 8%',
    sampleSku: 'BEA-4001'
  },
  {
    category: 'Sports & Outdoors',
    elasticityCoeff: -1.40,
    interpretation: 'Elastic (Seasonal spikes, high promotional sensitivity)',
    optimalDiscount: '15% - 18%',
    sampleSku: 'SPO-5001'
  }
];

// Python ML & Data Science Pipeline metadata & real code
export const PYTHON_PIPELINES: PythonScriptMetadata[] = [
  {
    id: 'etl_pipeline',
    filename: 'etl_pipeline.py',
    title: 'Enterprise Retail ETL & Data Cleansing Engine',
    category: 'ETL',
    description: 'Ingests raw retail POS and web transactions, imputes missing records, caps outliers via IQR, standardizes ISO timestamps, and writes to optimized analytical schema.',
    code: `"""
ETL Pipeline: Enterprise Retail Transaction Normalizer
Author: Retail Intelligence Platform Engine
"""
import pandas as pd
import numpy as np
from datetime import datetime

def run_etl_pipeline(input_csv_path: str) -> pd.DataFrame:
    print(f"[*] Ingesting raw retail transactions from {input_csv_path}...")
    df = pd.read_csv(input_csv_path)
    initial_rows = len(df)
    
    # 1. Deduplication
    df = df.drop_duplicates(subset=['order_id', 'sku'])
    dupes_removed = initial_rows - len(df)
    print(f"[✓] Removed {dupes_removed} duplicate transaction records.")

    # 2. Date Standardization
    df['order_date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['order_date'])

    # 3. Handle Missing Numeric COGS & Prices
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    df['unit_price'] = df.groupby('category')['unit_price'].transform(lambda x: x.fillna(x.median()))

    # 4. Outlier Capping on Quantity using Interquartile Range (IQR)
    q1 = df['quantity'].quantile(0.25)
    q3 = df['quantity'].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 3.0 * iqr
    outliers = (df['quantity'] > upper_bound).sum()
    df['quantity'] = np.where(df['quantity'] > upper_bound, upper_bound, df['quantity'])
    print(f"[✓] Capped {outliers} bulk anomaly order quantities.")

    # 5. Feature Engineering: Net Margin & Revenue
    df['gross_revenue'] = df['unit_price'] * df['quantity']
    df['discount_amount'] = df['gross_revenue'] * df['discount_pct'].fillna(0)
    df['net_revenue'] = df['gross_revenue'] - df['discount_amount']
    df['gross_profit'] = df['net_revenue'] - (df['cogs'] * df['quantity'])
    df['margin_pct'] = (df['gross_profit'] / df['net_revenue']) * 100

    print(f"[✓] ETL Complete. Cleaned shape: {df.shape}. Total Net Revenue: \${df['net_revenue'].sum():,.2f}")
    return df
`,
    sampleInput: 'raw_retail_transactions.csv (600 rows, 24 columns)',
    executionOutput: {
      status: 'idle',
      runtimeMs: 420,
      logs: [
        'Connecting to SQLite/Pandas runtime environment...',
        'Ingesting raw transactions: 600 initial rows parsed.',
        'Verified schema: [order_id, date, sku, customer_id, channel, quantity, unit_price, cogs].',
        'Imputed 4 missing unit prices using category median value.',
        'Standardized ISO timestamps to UTC format.',
        'Calculated net margins and synthesized financial features.',
        'Transferred 600 records to analytical data warehouse cache.'
      ],
      metrics: {
        'Records Processed': 600,
        'Duplicate Rows Dropped': 0,
        'Null Values Imputed': 4,
        'ETL Runtime': '420ms',
        'Data Quality Score': '99.4%'
      }
    }
  },
  {
    id: 'rfm_segmentation',
    filename: 'rfm_segmentation.py',
    title: 'Customer RFM Segmentation & Churn Matrix',
    category: 'Segmentation',
    description: 'Computes Recency, Frequency, and Monetary quintiles (1-5), groups customers into 6 behavior clusters (Champions, Loyal, At Risk, etc.), and predicts churn risk.',
    code: `"""
RFM Customer Segmentation & Churn Probability Model
Algorithm: Quintile Binning with Weighted Behavioral Scoring
"""
import pandas as pd
import numpy as np

def calculate_rfm(df: pd.DataFrame, ref_date: str = '2025-06-30') -> pd.DataFrame:
    snapshot_date = pd.to_datetime(ref_date)
    
    # Aggregate by customer
    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'nunique',
        'net_revenue': 'sum'
    }).reset_index()

    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']

    # Quintile rank (1 to 5)
    rfm['r_score'] = pd.qcut(rfm['recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)

    def segment_label(row):
        r, f, m = row['r_score'], row['f_score'], row['m_score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 2:
            return 'Potential Loyalists'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2 and m >= 3:
            return 'Hibernating'
        else:
            return 'Lost'

    rfm['segment'] = rfm.apply(segment_label, axis=1)
    return rfm
`,
    sampleInput: 'Customer purchase history dataset (30 distinct customer profiles)',
    executionOutput: {
      status: 'idle',
      runtimeMs: 280,
      logs: [
        'Initializing customer RFM aggregation...',
        'Computing days since last interaction against benchmark date (2025-06-30).',
        'Deriving order frequency and cumulative customer lifetime gross/net spend.',
        'Assigned 1-5 quantiles across Recency, Frequency, and Monetary dimensions.',
        'Clustered cohort: 23% Champions, 33% Loyal Customers, 20% At Risk, 10% Hibernating, 14% Lost.',
        'Calculated average Customer Lifetime Value (CLV): $3,842.50.'
      ],
      metrics: {
        'Total Unique Customers': 30,
        'Champions Cohort': '7 (23.3%)',
        'Loyal Cohort': '10 (33.3%)',
        'At Risk Cohort': '6 (20.0%)',
        'Average Customer LTV': '$3,842.50'
      }
    }
  },
  {
    id: 'sales_forecasting',
    filename: 'sales_forecasting.py',
    title: 'Holt-Winters Exponential Smoothing Sales Forecaster',
    category: 'Forecasting',
    description: 'Decomposes daily retail sales into trend, seasonality, and residual noise, generating 90-day predictive revenue forecasts with 95% confidence intervals.',
    code: `"""
Time-Series Revenue Forecaster: Additive Holt-Winters
Forecast Horizon: 90 Days ahead
"""
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def forecast_retail_sales(daily_sales_df: pd.DataFrame, horizon: int = 90):
    ts = daily_sales_df.set_index('date')['net_revenue'].asfreq('D').fillna(method='ffill')
    
    # Fit Holt-Winters triple exponential model with weekly seasonality (period=7)
    model = ExponentialSmoothing(
        ts,
        trend='add',
        seasonal='add',
        seasonal_periods=7
    ).fit()

    forecast = model.forecast(horizon)
    fitted_vals = model.fittedvalues
    
    # Calculate Mean Absolute Percentage Error (MAPE)
    mape = np.mean(np.abs((ts - fitted_vals) / ts)) * 100
    print(f"[✓] Forecast fitted successfully. Training MAPE: {mape:.2f}%")
    return forecast, mape
`,
    sampleInput: 'Daily aggregated revenue time-series (545 sequential days)',
    executionOutput: {
      status: 'idle',
      runtimeMs: 650,
      logs: [
        'Resampling transactions into uniform daily revenue time-series.',
        'Decomposing time-series: Observed weekly cycle (Sunday retail peak).',
        'Fitting Additive Exponential Smoothing (Trend: Additive, Seasonality: 7 days).',
        'Generating 90-day forward projection with upper/lower 95% bounds.',
        'Convergence achieved. In-sample MAPE: 4.82%. R² Score: 0.912.',
        'Forecast points generated and cached for Executive Dashboard.'
      ],
      metrics: {
        'Forecast Horizon': '90 Days',
        'Seasonal Periodicity': 'Weekly (7 Days)',
        'In-Sample MAPE': '4.82%',
        'Projected Q3 Revenue': '$184,200',
        'Model Confidence': '95%'
      }
    }
  },
  {
    id: 'discount_elasticity',
    filename: 'discount_elasticity.py',
    title: 'Price Elasticity of Demand & Promotional Optimizer',
    category: 'Pricing',
    description: 'Calculates Price Elasticity of Demand (PED = %ΔQ / %ΔP) across categories to determine the revenue-maximizing discount rate without eroding gross margin.',
    code: `"""
Price Elasticity of Demand (PED) & Discount Optimization Engine
Formula: PED = (% Change in Quantity Demanded) / (% Change in Price)
"""
import pandas as pd
import numpy as np

def calculate_category_elasticity(df: pd.DataFrame):
    results = []
    for category, group in df.groupby('category'):
        # Log-log regression for constant elasticity
        log_p = np.log(group['unit_price'] * (1 - group['discount_pct']))
        log_q = np.log(group['quantity'])
        
        # Slope = Elasticity
        slope, intercept = np.polyfit(log_p, log_q, 1)
        ped = slope
        
        # Max profit discount recommendation
        opt_discount = max(0.0, min(0.30, abs(1 / (ped + 1)))) if ped < -1 else 0.05
        
        results.append({
            'category': category,
            'elasticity_ped': round(ped, 2),
            'sensitivity': 'Elastic' if abs(ped) > 1 else 'Inelastic',
            'suggested_optimal_discount': f"{round(opt_discount * 100)}%"
        })
    return pd.DataFrame(results)
`,
    sampleInput: 'Transactional pricing variations and quantity response pairs',
    executionOutput: {
      status: 'idle',
      runtimeMs: 340,
      logs: [
        'Segmenting pricing variations across product categories...',
        'Fitting log-log demand curves against effective realized price.',
        'Computed Elasticity Coefficients: Electronics (-1.65), Apparel (-1.95), Beauty (-0.75).',
        'Beauty & Health identified as Inelastic: Discounts unnecessarily sacrifice margin.',
        'Apparel identified as Highly Elastic: 20% discount maximizes gross contribution.',
        'Generated dynamic pricing recommendations matrix.'
      ],
      metrics: {
        'Most Elastic Category': 'Apparel & Footwear (-1.95)',
        'Most Inelastic Category': 'Beauty & Health (-0.75)',
        'Margin Protection Threshold': '18% Max Discount',
        'Projected Margin Uplift': '+3.4%'
      }
    }
  }
];
