import Papa from 'papaparse';

/**
 * Enterprise Retail Intelligence Platform - Real Retail Data Types & Loader
 * Maps exactly to the PostgreSQL relational tables and verified CSV schemas.
 */

export interface OrderRecord {
  row_id: number;
  order_id: string;
  order_date: string;
  ship_date: string;
  ship_mode: string;
  customer_id: string;
  product_id: string;
  country: string;
  city: string;
  state: string;
  postal_code: number | string | null;
  region: string;
  sales: number;
  created_at: string;
  category?: string;
  sub_category?: string;
  segment?: string;
}

export interface CustomerRecord {
  customer_id: string;
  customer_name: string;
  segment: string;
  created_at: string;
}

export interface ProductRecord {
  product_id: string;
  product_name: string;
  category: string;
  sub_category: string;
  created_at: string;
}

export interface InventoryRecord {
  inventory_id: number;
  product_id: string;
  supplier_id: number | null;
  warehouse_name: string;
  warehouse_location: string;
  stock_quantity: number;
  reorder_level: number;
  stock_status: 'In Stock' | 'Low Stock' | 'Out of Stock' | string;
  last_restock_date: string;
  last_updated: string;
}

export interface ReturnRecord {
  return_id: number;
  order_row_id: number;
  product_id: string;
  return_date: string;
  return_reason: string;
  refund_amount: number;
  return_status: 'Completed' | 'Approved' | 'Requested' | 'Rejected' | string;
  created_at: string;
}

export interface TransportationRecord {
  transport_id: number;
  order_row_id: number;
  carrier_name: string;
  tracking_number: string;
  shipment_status: 'Delivered' | 'In Transit' | 'Shipped' | 'Pending' | 'Cancelled' | string;
  dispatch_date: string;
  estimated_delivery_date: string;
  actual_delivery_date: string;
  delivery_cost: number;
  created_at: string;
}

export interface RetailDatasetSummary {
  ordersCount: number;
  customersCount: number;
  productsCount: number;
  inventoryCount: number;
  returnsCount: number;
  transportationCount: number;
}

export interface RetailDataset {
  orders: OrderRecord[];
  customers: CustomerRecord[];
  products: ProductRecord[];
  inventory: InventoryRecord[];
  returns: ReturnRecord[];
  transportation: TransportationRecord[];
  loadedAt: Date;
  summary: RetailDatasetSummary;
}

/**
 * Configuration options for loading retail data.
 */
export interface LoadRetailDataOptions {
  /** If true, bypasses the in-memory cache and re-fetches all CSV files. */
  forceReload?: boolean;
  /** Optional custom base path for CSV assets (defaults to resolving from Vite BASE_URL or root). */
  basePath?: string;
}

// In-memory cache variables
let cachedDataset: RetailDataset | null = null;
let pendingLoadPromise: Promise<RetailDataset> | null = null;

/**
 * Resolves the absolute browser path for a public data asset.
 */
function resolveDataPath(fileName: string, customBasePath?: string): string {
  if (customBasePath) {
    const base = customBasePath.endsWith('/') ? customBasePath : `${customBasePath}/`;
    return `${base}${fileName}`;
  }
  const meta = import.meta as unknown as { env?: { BASE_URL?: string } };
  const baseUrl = meta?.env?.BASE_URL || '/';
  const cleanBase = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
  return `${cleanBase}data/${fileName}`;
}

/**
 * Fetches and parses a single CSV file with comprehensive validation and error handling.
 */
async function fetchAndParseCSV<T>(
  url: string,
  datasetName: string,
  requiredColumns: string[]
): Promise<T[]> {
  let rawText = '';

  if (typeof window === 'undefined') {
    try {
      const fs = await import('fs');
      const path = await import('path');
      const normalizedPath = url.replace(/^\/?data\//, '');
      const filePath = path.resolve(process.cwd(), 'public', 'data', normalizedPath);
      rawText = fs.readFileSync(filePath, 'utf-8');
    } catch (nodeErr) {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(
          `[RetailDataLoader] Failed to load ${datasetName} from "${url}". Status: ${response.status}`
        );
      }
      rawText = await response.text();
    }
  } else {
    let response: Response;
    try {
      response = await fetch(url);
    } catch (networkErr) {
      throw new Error(
        `[RetailDataLoader] Network error while fetching ${datasetName} from "${url}": ${
          networkErr instanceof Error ? networkErr.message : String(networkErr)
        }`
      );
    }

    if (!response.ok) {
      throw new Error(
        `[RetailDataLoader] Failed to load ${datasetName} from "${url}". HTTP Status: ${response.status} ${response.statusText}`
      );
    }
    rawText = await response.text();
  }
  if (!rawText || rawText.trim().length === 0) {
    throw new Error(
      `[RetailDataLoader] CSV dataset ${datasetName} at "${url}" is empty or contains only whitespace.`
    );
  }

  const parsed = Papa.parse<T>(rawText, {
    header: true,
    skipEmptyLines: 'greedy',
    dynamicTyping: true,
  });

  if (parsed.errors && parsed.errors.length > 0) {
    const fatalErrors = parsed.errors.filter((e) => e.type !== 'FieldMismatch');
    if (fatalErrors.length > 0) {
      const errorMsg = fatalErrors.map((e) => `Row ${e.row}: ${e.message}`).slice(0, 5).join('; ');
      throw new Error(
        `[RetailDataLoader] Malformed CSV encountered in ${datasetName} ("${url}"): ${errorMsg}`
      );
    }
  }

  if (!parsed.data || parsed.data.length === 0) {
    throw new Error(
      `[RetailDataLoader] Parsed dataset ${datasetName} at "${url}" yielded 0 rows.`
    );
  }

  // Validate required columns
  const fields = parsed.meta.fields || (parsed.data[0] ? Object.keys(parsed.data[0] as object) : []);
  const missingCols = requiredColumns.filter((col) => !fields.includes(col));
  if (missingCols.length > 0) {
    throw new Error(
      `[RetailDataLoader] Schema mismatch in ${datasetName} ("${url}"). Missing required columns: ${missingCols.join(
        ', '
      )}`
    );
  }

  return parsed.data;
}

/**
 * Loads and parses all six retail datasets from public CSV assets.
 * Implements in-memory caching and in-flight promise deduplication.
 */
export async function loadRetailData(options?: LoadRetailDataOptions): Promise<RetailDataset> {
  const forceReload = options?.forceReload ?? false;

  // Return existing cache if available and reload is not forced
  if (cachedDataset && !forceReload) {
    return cachedDataset;
  }

  // Return in-flight promise if currently loading
  if (pendingLoadPromise && !forceReload) {
    return pendingLoadPromise;
  }

  pendingLoadPromise = (async () => {
    try {
      const basePath = options?.basePath;

      const [orders, customers, products, inventory, returns, transportation] = await Promise.all([
        fetchAndParseCSV<OrderRecord>(
          resolveDataPath('orders.csv', basePath),
          'orders',
          ['row_id', 'order_id', 'order_date', 'customer_id', 'product_id', 'sales']
        ),
        fetchAndParseCSV<CustomerRecord>(
          resolveDataPath('customers.csv', basePath),
          'customers',
          ['customer_id', 'customer_name', 'segment']
        ),
        fetchAndParseCSV<ProductRecord>(
          resolveDataPath('products.csv', basePath),
          'products',
          ['product_id', 'product_name', 'category', 'sub_category']
        ),
        fetchAndParseCSV<InventoryRecord>(
          resolveDataPath('inventory.csv', basePath),
          'inventory',
          ['inventory_id', 'product_id', 'warehouse_name', 'stock_quantity', 'stock_status']
        ),
        fetchAndParseCSV<ReturnRecord>(
          resolveDataPath('returns.csv', basePath),
          'returns',
          ['return_id', 'order_row_id', 'product_id', 'return_reason', 'refund_amount']
        ),
        fetchAndParseCSV<TransportationRecord>(
          resolveDataPath('transportation.csv', basePath),
          'transportation',
          ['transport_id', 'order_row_id', 'carrier_name', 'shipment_status', 'delivery_cost']
        ),
      ]);

      // Enrich orders with category and segment for fast filtering
      const prodMap = new Map<string, { category: string; sub_category: string }>();
      for (let i = 0; i < products.length; i++) {
        prodMap.set(products[i].product_id, {
          category: products[i].category,
          sub_category: products[i].sub_category,
        });
      }
      const custMap = new Map<string, string>();
      for (let i = 0; i < customers.length; i++) {
        custMap.set(customers[i].customer_id, customers[i].segment);
      }
      for (let i = 0; i < orders.length; i++) {
        const o = orders[i];
        const p = prodMap.get(o.product_id);
        if (p) {
          o.category = p.category;
          o.sub_category = p.sub_category;
        }
        const s = custMap.get(o.customer_id);
        if (s) {
          o.segment = s;
        }
      }

      const dataset: RetailDataset = {
        orders,
        customers,
        products,
        inventory,
        returns,
        transportation,
        loadedAt: new Date(),
        summary: {
          ordersCount: orders.length,
          customersCount: customers.length,
          productsCount: products.length,
          inventoryCount: inventory.length,
          returnsCount: returns.length,
          transportationCount: transportation.length,
        },
      };

      cachedDataset = dataset;
      return dataset;
    } finally {
      pendingLoadPromise = null;
    }
  })();

  return pendingLoadPromise;
}

/**
 * Returns the currently cached dataset, or null if not yet loaded.
 */
export function getCachedRetailData(): RetailDataset | null {
  return cachedDataset;
}

/**
 * Clears the in-memory cache to allow fresh data retrieval.
 */
export function clearRetailDataCache(): void {
  cachedDataset = null;
  pendingLoadPromise = null;
}
