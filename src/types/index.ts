export type SalesChannel = 'Online' | 'Retail Store' | 'Marketplace' | 'B2B Wholesale' | 'Consumer' | 'Corporate' | 'Home Office';
export type Region = 'North America' | 'Europe' | 'Asia Pacific' | 'Latin America' | 'West' | 'East' | 'Central' | 'South';
export type ProductCategory = 'Electronics' | 'Apparel & Footwear' | 'Home & Living' | 'Beauty & Health' | 'Sports & Outdoors' | 'Technology' | 'Furniture' | 'Office Supplies';
export type ShippingCarrier = 'FedEx' | 'UPS' | 'DHL Express' | 'USPS' | 'OnTrac' | 'Delhivery' | 'Xpressbees' | 'Blue Dart' | 'Dhl' | 'Fedex' | 'Ups';
export type OrderStatus = 'Delivered' | 'In Transit' | 'Delayed' | 'Cancelled';
export type ReturnReason = 'Wrong Size / Fit' | 'Defective / Damaged' | 'Buyer Remorse' | 'Late Delivery' | 'Item Not as Pictured' | 'None';

export interface RetailTransaction {
  id: string;
  orderId: string;
  date: string;
  customerId: string;
  customerName: string;
  customerEmail: string;
  channel: SalesChannel;
  segment?: string;
  region: Region;
  storeLocation: string;
  category: ProductCategory;
  sku: string;
  productName: string;
  unitPrice: number;
  quantity: number;
  discountPct: number; // e.g. 0.15 for 15%
  discountAmount: number;
  grossRevenue: number;
  netRevenue: number;
  cogs: number;
  grossMargin: number;
  marginPct: number;
  shippingCost: number;
  deliveryDays: number;
  carrier: ShippingCarrier;
  status: OrderStatus;
  isReturned: boolean;
  returnReason: ReturnReason;
  returnCost: number;
}

export type RFMSegmentName =
  | 'Champions'
  | 'Loyal Customers'
  | 'Potential Loyalists'
  | 'At Risk'
  | 'Hibernating'
  | 'Lost';

export interface CustomerRFM {
  customerId: string;
  customerName: string;
  customerEmail: string;
  recencyDays: number;
  frequency: number;
  monetaryValue: number;
  rScore: number;
  fScore: number;
  mScore: number;
  rfmScore: number;
  segment: RFMSegmentName;
  preferredCategory: ProductCategory;
  avgOrderValue: number;
  churnProbability: number;
}

export interface InventoryItem {
  sku: string;
  productName: string;
  category: ProductCategory;
  unitCost: number;
  sellingPrice: number;
  currentStock: number;
  safetyStock: number;
  reorderPoint: number;
  dailyDemand: number;
  leadTimeDays: number;
  stockoutRisk: 'Low' | 'Moderate' | 'High' | 'Critical';
  turnoverRatio: number;
  daysOfInventory: number;
  deadStockFlag: boolean;
}

export interface LogisticsMetric {
  carrier: ShippingCarrier;
  totalShipments: number;
  onTimeDeliveries: number;
  onTimeRate: number; // %
  avgTransitDays: number;
  avgShippingCost: number;
  delayedShipments: number;
  claimRate: number; // %
}

export interface FilterState {
  dateRange: '7d' | '30d' | '90d' | 'ytd' | '1y' | 'all';
  customStartDate?: string;
  customEndDate?: string;
  region: string; // 'all' or specific
  category: string; // 'all' or specific
  channel: string; // 'all' or specific
  searchQuery: string;
}

export interface DatasetColumnMeta {
  name: string;
  type: 'numeric' | 'date' | 'categorical' | 'boolean' | 'unknown';
  sampleValues: (string | number | boolean)[];
  nullCount: number;
  nullPct: number;
  uniqueCount: number;
  min?: number;
  max?: number;
  avg?: number;
}

export interface CleanedDatasetInfo {
  id: string;
  name: string;
  source: 'default' | 'uploaded' | 'sample';
  uploadedAt: string;
  rowCount: number;
  colCount: number;
  columns: DatasetColumnMeta[];
  rawRecords: Record<string, any>[];
  cleaningSummary: {
    nullsFixed: number;
    duplicatesRemoved: number;
    datesStandardized: number;
    outliersCapped: number;
  };
}

export interface PythonScriptMetadata {
  id: string;
  filename: string;
  title: string;
  category: 'ETL' | 'Segmentation' | 'Forecasting' | 'Pricing';
  description: string;
  code: string;
  sampleInput: string;
  executionOutput: {
    status: 'success' | 'running' | 'idle';
    runtimeMs: number;
    logs: string[];
    metrics: Record<string, string | number>;
    visualData?: any;
  };
}
