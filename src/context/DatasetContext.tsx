import React, { createContext, useContext, useState, useMemo, useEffect } from 'react';
import Papa from 'papaparse';
import {
  RetailTransaction,
  InventoryItem,
  CustomerRFM,
  LogisticsMetric,
  CleanedDatasetInfo,
  DatasetColumnMeta
} from '../types';
import {
  INITIAL_TRANSACTIONS,
  INITIAL_INVENTORY,
  INITIAL_RFM,
  INITIAL_LOGISTICS,
  computeRFMSegments
} from '../data/mockData';
import {
  loadRetailData,
  RetailDataset,
  clearRetailDataCache
} from '../services/retailDataLoader';
import {
  calculateRetailKPIs,
  RetailKPIs,
  RetailFilters
} from '../services/retailAnalytics';
import { transformRetailDatasetToEntities } from '../services/retailTransform';

interface DatasetContextType {
  activeDatasetName: string;
  datasetType: 'default' | 'sample_holiday' | 'sample_apparel' | 'custom_uploaded';
  transactions: RetailTransaction[];
  inventory: InventoryItem[];
  rfm: CustomerRFM[];
  logistics: LogisticsMetric[];
  uploadedDataset: CleanedDatasetInfo | null;
  loadSampleDataset: (sampleType: 'default' | 'sample_holiday' | 'sample_apparel') => void;
  processAndLoadCSV: (file: File) => Promise<{ success: boolean; message: string }>;
  processRawCSVText: (csvText: string, datasetName: string) => { success: boolean; message: string };
  exportTransactionsToCSV: () => void;
  resetToDefault: () => void;
  isProcessing: boolean;
  isRealRetailDataLoaded: boolean;
  loadRealRetailTransactions: (data: RetailTransaction[], datasetName?: string) => void;
  loadRealRetailFromCSV: (csvData: string | File, datasetName?: string) => Promise<{ success: boolean; message: string; rows: number }>;
  realDataset: RetailDataset | null;
  isLoadingRetail: boolean;
  retailLoadError: string | null;
  reloadRetailData: () => Promise<void>;
  retailKPIs: RetailKPIs;
  getRetailKPIs: (filters?: RetailFilters) => RetailKPIs;
}

const DatasetContext = createContext<DatasetContextType | undefined>(undefined);

export const DatasetProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeDatasetName, setActiveDatasetName] = useState('Enterprise Retail Intelligence (9,800 Orders)');
  const [datasetType, setDatasetType] = useState<'default' | 'sample_holiday' | 'sample_apparel' | 'custom_uploaded'>('default');
  const [transactions, setTransactions] = useState<RetailTransaction[]>(INITIAL_TRANSACTIONS);
  const [inventory, setInventory] = useState<InventoryItem[]>(INITIAL_INVENTORY);
  const [logistics, setLogistics] = useState<LogisticsMetric[]>(INITIAL_LOGISTICS);
  const [uploadedDataset, setUploadedDataset] = useState<CleanedDatasetInfo | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRealRetailDataLoaded, setIsRealRetailDataLoaded] = useState(false);
  const [realDataset, setRealDataset] = useState<RetailDataset | null>(null);
  const [isLoadingRetail, setIsLoadingRetail] = useState<boolean>(true);
  const [retailLoadError, setRetailLoadError] = useState<string | null>(null);

  // Load real retail data on initialization
  const reloadRetailData = async () => {
    setIsLoadingRetail(true);
    setRetailLoadError(null);
    try {
      const data = await loadRetailData();
      setRealDataset(data);
      const entities = transformRetailDatasetToEntities(data);
      setTransactions(entities.transactions);
      setInventory(entities.inventory);
      setLogistics(entities.logistics);
      setActiveDatasetName('Enterprise Retail Intelligence (9,800 Orders)');
      setIsRealRetailDataLoaded(true);
      setDatasetType('default');
    } catch (err: any) {
      console.error('Failed to load real retail dataset:', err);
      setRetailLoadError(err.message || 'Failed to load retail dataset from CSV files');
    } finally {
      setIsLoadingRetail(false);
    }
  };

  useEffect(() => {
    reloadRetailData();
  }, []);

  // Compute baseline or active KPIs from real retail data
  const retailKPIs = useMemo(() => {
    if (!realDataset) {
      return calculateRetailKPIs({
        orders: [],
        customers: [],
        products: [],
        inventory: [],
        returns: [],
        transportation: [],
        loadedAt: new Date(),
        summary: {
          ordersCount: 0,
          customersCount: 0,
          productsCount: 0,
          inventoryCount: 0,
          returnsCount: 0,
          transportationCount: 0
        }
      });
    }
    return calculateRetailKPIs(realDataset);
  }, [realDataset]);

  const getRetailKPIs = (filters?: RetailFilters): RetailKPIs => {
    if (!realDataset) {
      return retailKPIs;
    }
    return calculateRetailKPIs(realDataset, filters);
  };

  // Recalculate RFM dynamically whenever realDataset or transactions change
  const rfm = useMemo(() => {
    if (realDataset && isRealRetailDataLoaded) {
      const entities = transformRetailDatasetToEntities(realDataset);
      return entities.rfm;
    }
    return computeRFMSegments(transactions);
  }, [realDataset, isRealRetailDataLoaded, transactions]);

  // Load real retail transactions into the retail mode
  const loadRealRetailTransactions = (data: RetailTransaction[], datasetName = 'Production Retail Dataset') => {
    setTransactions(data);
    setActiveDatasetName(datasetName);
    setIsRealRetailDataLoaded(true);
    setDatasetType('default');
  };

  // Parser to ingest real retail dataset (e.g. Superstore CSV format or custom retail CSV)
  const loadRealRetailFromCSV = async (
    csvData: string | File,
    datasetName = 'Production Retail Dataset'
  ): Promise<{ success: boolean; message: string; rows: number }> => {
    setIsProcessing(true);
    return new Promise((resolve) => {
      const handleParsed = (results: Papa.ParseResult<any>) => {
        try {
          if (!results.data || results.data.length === 0) {
            setIsProcessing(false);
            resolve({ success: false, message: 'CSV data is empty', rows: 0 });
            return;
          }

          const rawRows = results.data as Record<string, any>[];
          const mapped = tryMapToRetailTransactions(rawRows);
          if (mapped && mapped.length > 0) {
            setTransactions(mapped);
            setActiveDatasetName(datasetName);
            setIsRealRetailDataLoaded(true);
            setDatasetType('default');
            setIsProcessing(false);
            resolve({
              success: true,
              message: `Successfully loaded ${mapped.length} real retail transactions.`,
              rows: mapped.length
            });
          } else {
            setIsProcessing(false);
            resolve({ success: false, message: 'Could not map columns to retail transactions schema.', rows: 0 });
          }
        } catch (err: any) {
          setIsProcessing(false);
          resolve({ success: false, message: err.message || 'Error processing retail CSV', rows: 0 });
        }
      };

      if (typeof csvData === 'string') {
        Papa.parse(csvData, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true,
          complete: handleParsed,
          error: (err) => {
            setIsProcessing(false);
            resolve({ success: false, message: err.message, rows: 0 });
          }
        });
      } else {
        Papa.parse(csvData, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true,
          complete: handleParsed,
          error: (err) => {
            setIsProcessing(false);
            resolve({ success: false, message: err.message, rows: 0 });
          }
        });
      }
    });
  };

  // Load sample dataset variations
  const loadSampleDataset = (sampleType: 'default' | 'sample_holiday' | 'sample_apparel') => {
    if (sampleType === 'default') {
      setTransactions(INITIAL_TRANSACTIONS);
      setActiveDatasetName('Omnichannel Global Retail 2024-2025');
      setDatasetType('default');
      setUploadedDataset(null);
    } else if (sampleType === 'sample_holiday') {
      // Create holiday promotional focused transactions
      const holidayTx = INITIAL_TRANSACTIONS.map((tx) => {
        const isHoliday = tx.date.includes('-11-') || tx.date.includes('-12-');
        const mult = isHoliday ? 2.2 : 0.8;
        const discountMult = isHoliday ? 0.25 : tx.discountPct;
        const grossRev = Math.round(tx.unitPrice * Math.ceil(tx.quantity * mult) * 100) / 100;
        const discAmt = Math.round(grossRev * discountMult * 100) / 100;
        const netRev = Math.round((grossRev - discAmt) * 100) / 100;
        const grossMargin = Math.round((netRev - tx.cogs * tx.quantity) * 100) / 100;
        return {
          ...tx,
          discountPct: discountMult,
          discountAmount: discAmt,
          grossRevenue: grossRev,
          netRevenue: netRev,
          grossMargin,
          marginPct: Math.round((grossMargin / netRev) * 1000) / 10
        };
      });
      setTransactions(holidayTx);
      setActiveDatasetName('Q4 Holiday Peak & Black Friday Benchmark');
      setDatasetType('sample_holiday');
      setUploadedDataset(null);
    } else if (sampleType === 'sample_apparel') {
      // Apparel returns focus
      const apparelTx = INITIAL_TRANSACTIONS.map((tx) => {
        if (tx.category === 'Apparel & Footwear') {
          return {
            ...tx,
            isReturned: Math.random() > 0.65,
            returnReason: (['Wrong Size / Fit', 'Item Not as Pictured', 'Buyer Remorse'] as const)[
              Math.floor(Math.random() * 3)
            ],
            returnCost: 22.50
          };
        }
        return tx;
      });
      setTransactions(apparelTx);
      setActiveDatasetName('Apparel & Footwear High-Return Benchmark');
      setDatasetType('sample_apparel');
      setUploadedDataset(null);
    }
  };

  // Automated Data Cleaning & Profiler
  const analyzeAndCleanDataset = (
    fileName: string,
    rawRecords: Record<string, any>[]
  ): CleanedDatasetInfo => {
    if (rawRecords.length === 0) {
      throw new Error('Dataset is empty');
    }

    const columnNames = Object.keys(rawRecords[0]);
    let nullsFixed = 0;
    let datesStandardized = 0;
    let outliersCapped = 0;

    // Detect column types and profile
    const columnsMeta: DatasetColumnMeta[] = columnNames.map((col) => {
      let numericCount = 0;
      let dateCount = 0;
      let nullCount = 0;
      const values: any[] = [];
      const uniqueVals = new Set<string>();

      rawRecords.forEach((row) => {
        const val = row[col];
        if (val === null || val === undefined || val === '') {
          nullCount++;
          return;
        }
        values.push(val);
        uniqueVals.add(String(val));

        // Check if numeric
        const num = Number(val);
        if (!isNaN(num) && typeof val !== 'boolean') {
          numericCount++;
        }

        // Check if date
        if (typeof val === 'string' && val.length >= 8 && !isNaN(Date.parse(val))) {
          dateCount++;
        }
      });

      const total = rawRecords.length;
      let type: DatasetColumnMeta['type'] = 'categorical';
      if (numericCount / (total - nullCount) > 0.8) type = 'numeric';
      else if (dateCount / (total - nullCount) > 0.8) type = 'date';
      else if (uniqueVals.size <= 2 && (uniqueVals.has('true') || uniqueVals.has('false') || uniqueVals.has('1') || uniqueVals.has('0'))) {
        type = 'boolean';
      }

      let min: number | undefined;
      let max: number | undefined;
      let avg: number | undefined;

      if (type === 'numeric') {
        const nums = values.map((v) => Number(v)).filter((v) => !isNaN(v));
        if (nums.length > 0) {
          min = Math.min(...nums);
          max = Math.max(...nums);
          avg = Math.round((nums.reduce((a, b) => a + b, 0) / nums.length) * 100) / 100;
        }
      }

      return {
        name: col,
        type,
        sampleValues: values.slice(0, 5),
        nullCount,
        nullPct: Math.round((nullCount / total) * 1000) / 10,
        uniqueCount: uniqueVals.size,
        min,
        max,
        avg
      };
    });

    // Clean records
    const cleanedRecords = rawRecords.map((row) => {
      const cleaned = { ...row };
      columnsMeta.forEach((meta) => {
        const val = cleaned[meta.name];
        if (val === null || val === undefined || val === '') {
          nullsFixed++;
          if (meta.type === 'numeric') {
            cleaned[meta.name] = meta.avg || 0;
          } else if (meta.type === 'date') {
            cleaned[meta.name] = '2024-01-01';
            datesStandardized++;
          } else {
            cleaned[meta.name] = 'Unknown';
          }
        }
      });
      return cleaned;
    });

    return {
      id: `dataset-${Date.now()}`,
      name: fileName,
      source: 'uploaded',
      uploadedAt: new Date().toLocaleTimeString(),
      rowCount: cleanedRecords.length,
      colCount: columnNames.length,
      columns: columnsMeta,
      rawRecords: cleanedRecords,
      cleaningSummary: {
        nullsFixed,
        duplicatesRemoved: 0,
        datesStandardized,
        outliersCapped
      }
    };
  };

  // Convert uploaded records to RetailTransaction if compatible
  const tryMapToRetailTransactions = (records: Record<string, any>[]): RetailTransaction[] | null => {
    if (records.length === 0) return null;
    const sample = records[0];
    const keys = Object.keys(sample).map((k) => k.toLowerCase());

    const hasRevenue = keys.some((k) => k.includes('revenue') || k.includes('price') || k.includes('sales') || k.includes('amount'));
    const hasCategory = keys.some((k) => k.includes('category') || k.includes('dept') || k.includes('product'));

    if (!hasRevenue && !hasCategory) return null;

    return records.map((r, i) => {
      // Fuzzy key finder
      const findKey = (candidates: string[]): any => {
        for (const c of candidates) {
          const found = Object.keys(r).find((k) => k.toLowerCase() === c || k.toLowerCase().includes(c));
          if (found && r[found] !== undefined) return r[found];
        }
        return null;
      };

      const rawPrice = Number(findKey(['revenue', 'netrevenue', 'sales', 'unitprice', 'price', 'amount'])) || 99.99;
      const rawQuantity = Number(findKey(['quantity', 'qty', 'count', 'units'])) || 1;
      const rawCategory = String(findKey(['category', 'dept', 'product_category']) || 'General Retail');
      const rawChannel = String(findKey(['channel', 'platform', 'source']) || 'Online');
      const rawRegion = String(findKey(['region', 'country', 'state', 'location']) || 'North America');
      const rawDate = String(findKey(['date', 'order_date', 'timestamp']) || '2024-06-15');

      const netRevenue = Math.round(rawPrice * 100) / 100;
      const cogs = Math.round(netRevenue * 0.45 * 100) / 100;
      const grossMargin = Math.round((netRevenue - cogs) * 100) / 100;

      return {
        id: `UPL-${i + 1}`,
        orderId: `ORD-UPL-${1000 + i}`,
        date: rawDate.split('T')[0],
        customerId: `CUST-${(i % 25) + 1}`,
        customerName: `Customer ${(i % 25) + 1}`,
        customerEmail: `customer${(i % 25) + 1}@example.com`,
        channel: (rawChannel.includes('Store') ? 'Retail Store' : rawChannel.includes('B2B') ? 'B2B Wholesale' : 'Online') as any,
        region: (rawRegion.includes('Europe') ? 'Europe' : rawRegion.includes('Asia') ? 'Asia Pacific' : 'North America') as any,
        storeLocation: 'Uploaded Distribution',
        category: rawCategory as any,
        sku: `SKU-${100 + (i % 20)}`,
        productName: String(findKey(['productname', 'product', 'name', 'item']) || `Product Item ${(i % 20) + 1}`),
        unitPrice: rawPrice,
        quantity: rawQuantity,
        discountPct: 0.1,
        discountAmount: Math.round(rawPrice * 0.1 * 100) / 100,
        grossRevenue: Math.round(rawPrice * 1.1 * 100) / 100,
        netRevenue,
        cogs,
        grossMargin,
        marginPct: Math.round((grossMargin / netRevenue) * 1000) / 10,
        shippingCost: 12.0,
        deliveryDays: 3,
        carrier: 'FedEx',
        status: 'Delivered',
        isReturned: i % 12 === 0,
        returnReason: i % 12 === 0 ? 'Wrong Size / Fit' : 'None',
        returnCost: i % 12 === 0 ? 15.0 : 0
      };
    });
  };

  const processAndLoadCSV = async (file: File): Promise<{ success: boolean; message: string }> => {
    setIsProcessing(true);
    return new Promise((resolve) => {
      Papa.parse(file, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        complete: (results) => {
          try {
            if (!results.data || results.data.length === 0) {
              setIsProcessing(false);
              resolve({ success: false, message: 'File is empty or contains no parseable headers.' });
              return;
            }

            const cleanedInfo = analyzeAndCleanDataset(file.name, results.data as Record<string, any>[]);
            setUploadedDataset(cleanedInfo);
            setActiveDatasetName(file.name);
            setDatasetType('custom_uploaded');

            setIsProcessing(false);
            resolve({
              success: true,
              message: `Successfully cleaned and profiled ${cleanedInfo.rowCount} rows across ${cleanedInfo.colCount} attributes.`
            });
          } catch (err: any) {
            setIsProcessing(false);
            resolve({ success: false, message: err.message || 'Error processing dataset.' });
          }
        },
        error: (err) => {
          setIsProcessing(false);
          resolve({ success: false, message: `Parse error: ${err.message}` });
        }
      });
    });
  };

  const processRawCSVText = (csvText: string, datasetName: string): { success: boolean; message: string } => {
    try {
      const results = Papa.parse(csvText, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true
      });

      if (!results.data || results.data.length === 0) {
        return { success: false, message: 'CSV text has no rows.' };
      }

      const cleanedInfo = analyzeAndCleanDataset(datasetName, results.data as Record<string, any>[]);
      setUploadedDataset(cleanedInfo);
      setActiveDatasetName(datasetName);
      setDatasetType('custom_uploaded');

      return {
        success: true,
        message: `Parsed and cleaned ${cleanedInfo.rowCount} rows into custom dataset.`
      };
    } catch (err: any) {
      return { success: false, message: err.message || 'Failed to parse CSV text.' };
    }
  };

  const exportTransactionsToCSV = () => {
    const csv = Papa.unparse(transactions);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `retail_intelligence_export_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const resetToDefault = () => {
    loadSampleDataset('default');
  };

  return (
    <DatasetContext.Provider
      value={{
        activeDatasetName,
        datasetType,
        transactions,
        inventory,
        rfm,
        logistics,
        uploadedDataset,
        loadSampleDataset,
        processAndLoadCSV,
        processRawCSVText,
        exportTransactionsToCSV,
        resetToDefault,
        isProcessing,
        isRealRetailDataLoaded,
        loadRealRetailTransactions,
        loadRealRetailFromCSV,
        realDataset,
        isLoadingRetail,
        retailLoadError,
        reloadRetailData,
        retailKPIs,
        getRetailKPIs
      }}
    >
      {children}
    </DatasetContext.Provider>
  );
};

export const useDataset = (): DatasetContextType => {
  const context = useContext(DatasetContext);
  if (!context) {
    throw new Error('useDataset must be used within a DatasetProvider');
  }
  return context;
};
