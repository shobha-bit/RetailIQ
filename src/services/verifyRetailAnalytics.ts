import { loadRetailData } from './retailDataLoader';
import { verifyRetailCalculations, calculateRetailKPIs } from './retailAnalytics';

/**
 * Verification runner script for Phase 15B Part 3 analytics layer.
 * Can be run via tsx or invoked in test suites.
 */
export async function runRetailAnalyticsVerification() {
  console.log('--- PHASE 15B PART 3: RETAIL ANALYTICS LAYER VERIFICATION ---');
  console.log('1. Loading datasets from public/data/ via retailDataLoader...');
  const startLoad = Date.now();
  const dataset = await loadRetailData();
  console.log(`Loaded 6 datasets in ${Date.now() - startLoad}ms.`);
  console.log('Dataset row counts:', dataset.summary);

  console.log('\n2. Computing pure calculations via calculateRetailKPIs...');
  const startCalc = Date.now();
  const kpis = calculateRetailKPIs(dataset);
  console.log(`Calculated all retail KPIs in ${Date.now() - startCalc}ms.`);

  console.log('\n3. Actual Calculated Results:');
  console.log(`- Total Sales: $${kpis.totalSales.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`);
  console.log(`- Total Orders (Distinct): ${kpis.totalOrders.toLocaleString()}`);
  console.log(`- Total Customers: ${kpis.totalCustomers.toLocaleString()}`);
  console.log(`- Average Order Value (AOV): $${kpis.averageOrderValue.toFixed(2)}`);
  console.log(`- Orders Per Customer: ${kpis.ordersPerCustomer.toFixed(2)}`);
  console.log(`- Total Products: ${kpis.totalProducts.toLocaleString()}`);
  console.log(`- Average Sales Per Product: $${kpis.averageSalesPerProduct.toFixed(2)}`);
  console.log(`- Total Returns: ${kpis.totalReturns}`);
  console.log(`- Returned Products: ${kpis.returnedProducts}`);
  console.log(`- Return Rate: ${kpis.returnRate.toFixed(2)}%`);
  console.log(`- Average Delivery Days: ${kpis.averageDeliveryDays.toFixed(2)} days`);
  console.log(`- Total Inventory Stock: ${kpis.totalStock.toLocaleString()}`);
  console.log(`- Inventory Items: ${kpis.inventoryItems.toLocaleString()}`);
  console.log(`- Low Stock Items: ${kpis.lowStockItems}`);
  console.log(`- Warehouses: ${kpis.warehouses}`);
  console.log(`- Sales YoY (2018 vs 2017): ${kpis.salesYoY.toFixed(2)}%`);
  console.log('  Yearly Sales Breakdown:', kpis.salesYoYBreakdown.yearlySales);
  console.log('  Yearly Growth Progression:', kpis.salesYoYBreakdown.yearlyGrowth);

  console.log('\n4. Running validation against Phase 15A baseline benchmarks...');
  const report = verifyRetailCalculations(dataset);

  for (const check of report.checks) {
    const symbol = check.passed ? '✓ PASS' : '✗ FAIL';
    console.log(`  [${symbol}] ${check.metric.padEnd(28)}: Expected ${String(check.expected).padEnd(12)} Actual ${String(check.actual).padEnd(12)} (Tol ±${check.tolerance})`);
  }

  console.log(`\nValidation Summary: ${report.passedChecks}/${report.totalChecks} checks passed.`);
  if (!report.allPassed) {
    throw new Error(`Validation failed: ${report.failedChecks} checks failed.`);
  }
  console.log('ALL CHECKS PASSED PERFECTLY!\n');
  return report;
}

// Allow direct CLI execution if executed directly
if (typeof process !== 'undefined' && process.argv && process.argv[1]?.includes('verifyRetailAnalytics')) {
  // If running in Node, mock fetch to public/data if window is undefined
  if (typeof window === 'undefined') {
    const fs = await import('fs');
    globalThis.fetch = async (url: any) => {
      const urlStr = String(url);
      const match = urlStr.match(/\/data\/([^/?#]+)/);
      if (match) {
        const filePath = `public/data/${match[1]}`;
        if (fs.existsSync(filePath)) {
          const content = fs.readFileSync(filePath, 'utf-8');
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            text: async () => content,
          } as any;
        }
      }
      return { ok: false, status: 404, statusText: 'Not Found', text: async () => '' } as any;
    };
  }

  runRetailAnalyticsVerification().catch((err) => {
    console.error('Verification error:', err);
    process.exit(1);
  });
}
