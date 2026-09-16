"""
Test Suite for Retail Analytics Engine (Phase 2)
=================================================
Validates:
1. All core KPIs against verified ground-truth baselines.
2. Dataset row counts and referential integrity.
3. Safe analytical joins (zero row multiplication, invariant sales sum).
4. Return analytics definitions (490 records vs 424 products vs 465 orders).
5. Dynamic YoY calculation resilience.
6. Multidimensional filtering (7D, 30D, 90D, YTD, 1Y, Region, Category, Segment, Search).
7. Logistics fulfillment & real carrier tracking.
8. Customer RFM behavioral segmentation.
"""

import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

# Ensure python_app is importable
APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from python_app.data.loader import load_all_retail_data
from python_app.analytics.retail_analytics import (
    calculate_retail_kpis,
    calculate_total_sales,
    calculate_total_orders,
    calculate_total_customers,
    calculate_average_order_value,
    calculate_orders_per_customer,
    calculate_total_products,
    calculate_average_sales_per_product,
    calculate_returns_kpis,
    calculate_inventory_kpis,
    calculate_logistics_kpis,
    calculate_sales_yoy,
    calculate_monthly_sales,
    calculate_sales_by_category,
    calculate_sales_by_region,
    calculate_sales_by_segment,
    calculate_top_products,
    calculate_sales_by_customer,
    calculate_sales_by_ship_mode,
    calculate_stock_by_warehouse,
    calculate_stock_status_distribution,
    calculate_inventory_by_category,
    calculate_carrier_summary,
    calculate_customer_summary,
    calculate_customer_rfm,
    calculate_rfm_segment_summary,
    get_filter_options,
    filter_retail_orders,
    filter_retail_data,
    RetailFilters,
    safe_join_orders_products,
    safe_join_orders_customers,
    safe_join_orders_all,
)


class TestRetailDataIntegrity(unittest.TestCase):
    """Confirm raw dataset record counts, key uniqueness, and baseline invariants."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()

    def test_row_counts(self):
        """Verify exact row counts for all 6 relational datasets."""
        self.assertEqual(len(self.bundle.orders), 9800, "Orders must have exactly 9,800 rows")
        self.assertEqual(len(self.bundle.customers), 793, "Customers must have exactly 793 rows")
        self.assertEqual(len(self.bundle.products), 1861, "Products must have exactly 1,861 rows")
        self.assertEqual(len(self.bundle.inventory), 1861, "Inventory must have exactly 1,861 rows")
        self.assertEqual(len(self.bundle.returns), 490, "Returns must have exactly 490 rows")
        self.assertEqual(len(self.bundle.transportation), 9800, "Transportation must have exactly 9,800 rows")

    def test_distinct_order_ids(self):
        """Orders table contains 9,800 items across 4,922 distinct orders."""
        distinct_orders = self.bundle.orders["order_id"].nunique()
        self.assertEqual(distinct_orders, 4922, "Expected exactly 4,922 distinct order IDs")

    def test_total_sales_sum(self):
        """Sum of orders.sales must equal $2,261,536.97."""
        sales_sum = float(self.bundle.orders["sales"].sum())
        self.assertAlmostEqual(sales_sum, 2261536.97, places=2)

    def test_primary_key_uniqueness(self):
        """Verify that dimension and fact primary keys are unique."""
        self.assertTrue(self.bundle.orders["row_id"].is_unique, "orders.row_id must be unique")
        self.assertTrue(self.bundle.customers["customer_id"].is_unique, "customers.customer_id must be unique")
        self.assertTrue(self.bundle.products["product_id"].is_unique, "products.product_id must be unique")
        self.assertTrue(self.bundle.inventory["inventory_id"].is_unique, "inventory.inventory_id must be unique")
        self.assertTrue(self.bundle.returns["return_id"].is_unique, "returns.return_id must be unique")
        self.assertTrue(self.bundle.transportation["transport_id"].is_unique, "transportation.transport_id must be unique")


class TestCoreRetailKPIs(unittest.TestCase):
    """Test all core retail KPI calculations against verified ground truths."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()
        cls.kpis = calculate_retail_kpis(cls.bundle)

    def test_total_sales(self):
        # Expected: $2,261,536.97
        self.assertAlmostEqual(self.kpis["total_sales"], 2261536.97, places=2)

    def test_total_orders(self):
        # Expected: 4,922
        self.assertEqual(self.kpis["total_orders"], 4922)

    def test_total_customers(self):
        # Expected: 793
        self.assertEqual(self.kpis["customers"], 793)

    def test_average_order_value(self):
        # Expected: $459.48
        self.assertAlmostEqual(self.kpis["aov"], 459.48, delta=0.05)

    def test_orders_per_customer(self):
        # Expected: 6.21
        self.assertAlmostEqual(self.kpis["orders_per_customer"], 6.21, delta=0.02)

    def test_total_products(self):
        # Expected: 1,861
        self.assertEqual(self.kpis["products"], 1861)

    def test_average_sales_per_product(self):
        # Expected: $1,215.23
        self.assertAlmostEqual(self.kpis["average_sales_per_product"], 1215.23, delta=0.05)

    def test_total_returns(self):
        # Expected: 490 return records
        self.assertEqual(self.kpis["returns"], 490)
        self.assertEqual(self.kpis["total_returns"], 490)

    def test_returned_products(self):
        # Expected: 424 unique returned products
        self.assertEqual(self.kpis["returned_products"], 424)

    def test_distinct_returned_orders(self):
        # Expected: 465 distinct returned orders
        self.assertEqual(self.kpis["distinct_returned_orders"], 465)

    def test_return_rate(self):
        # Expected: 9.96%
        self.assertAlmostEqual(self.kpis["return_rate"], 9.96, delta=0.02)

    def test_average_delivery_days(self):
        # Expected: ~4.11 days
        self.assertAlmostEqual(self.kpis["average_delivery_days"], 4.11, delta=0.05)

    def test_inventory_stock(self):
        # Expected: 512,612 units
        self.assertEqual(self.kpis["inventory_stock"], 512612)

    def test_inventory_items(self):
        # Expected: 1,861 catalog items
        self.assertEqual(self.kpis["inventory_items"], 1861)

    def test_low_stock_items(self):
        # Expected: 34 items
        self.assertEqual(self.kpis["low_stock_items"], 34)

    def test_warehouses(self):
        # Expected: 3 warehouses
        self.assertEqual(self.kpis["warehouses"], 3)

    def test_sales_yoy(self):
        # Expected: ~20.30%
        self.assertAlmostEqual(self.kpis["sales_yoy"], 20.30, delta=0.05)


class TestSafeAnalyticalJoins(unittest.TestCase):
    """Verify that joins do not multiply rows or alter base sales totals."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()
        cls.base_sales = float(cls.bundle.orders["sales"].sum())

    def test_safe_join_orders_products(self):
        joined = safe_join_orders_products(self.bundle.orders, self.bundle.products)
        self.assertEqual(len(joined), 9800, "Join with products must preserve 9,800 rows")
        self.assertAlmostEqual(float(joined["sales"].sum()), self.base_sales, places=2)
        self.assertIn("product_name", joined.columns)
        self.assertIn("category", joined.columns)

    def test_safe_join_orders_customers(self):
        joined = safe_join_orders_customers(self.bundle.orders, self.bundle.customers)
        self.assertEqual(len(joined), 9800, "Join with customers must preserve 9,800 rows")
        self.assertAlmostEqual(float(joined["sales"].sum()), self.base_sales, places=2)
        self.assertIn("customer_name", joined.columns)
        self.assertIn("segment", joined.columns)

    def test_safe_join_orders_all(self):
        joined = safe_join_orders_all(self.bundle.orders, self.bundle.products, self.bundle.customers)
        self.assertEqual(len(joined), 9800, "Full join must preserve 9,800 rows")
        self.assertAlmostEqual(float(joined["sales"].sum()), self.base_sales, places=2)


class TestReturnsTerminologyAndLogic(unittest.TestCase):
    """Ensure strict differentiation between return events, unique products, and distinct orders."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()
        cls.returns_kpis = calculate_returns_kpis(cls.bundle.returns, cls.bundle.orders)

    def test_terminology_distinctions(self):
        self.assertEqual(self.returns_kpis["total_returns"], 490, "Total return events = 490")
        self.assertEqual(self.returns_kpis["returned_products"], 424, "Unique returned products = 424")
        self.assertEqual(self.returns_kpis["distinct_returned_orders"], 465, "Distinct returned orders = 465")
        self.assertNotEqual(
            self.returns_kpis["total_returns"],
            self.returns_kpis["distinct_returned_orders"],
            "Return events (490) must NEVER be equated with distinct returned orders (465)"
        )


class TestLogisticsAndCarriers(unittest.TestCase):
    """Validate logistics KPIs and ensure carrier names strictly originate from data."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()
        cls.logistics_kpis = calculate_logistics_kpis(cls.bundle.transportation)
        cls.carrier_df = calculate_carrier_summary(cls.bundle.transportation)

    def test_real_carrier_names(self):
        expected_carriers = {"Blue Dart", "Delhivery", "Dhl", "Fedex", "Ups", "Xpressbees"}
        actual_carriers = set(self.carrier_df["carrier_name"])
        self.assertEqual(actual_carriers, expected_carriers, "Carrier names must match real dataset exactly")

    def test_carrier_shipments_sum(self):
        total_shipments = self.carrier_df["total_shipments"].sum()
        self.assertEqual(total_shipments, 9800, "All carrier shipments must sum to 9,800")

    def test_on_time_delivery_rate_bounds(self):
        ot_rate = self.logistics_kpis["on_time_delivery_rate"]
        self.assertGreater(ot_rate, 80.0)
        self.assertLessEqual(ot_rate, 100.0)


class TestFilterEngine(unittest.TestCase):
    """Verify multidimensional slicing and dynamic date boundary precision."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()

    def test_filter_options_derived_from_data(self):
        options = get_filter_options(self.bundle)
        self.assertIn("Central", options["regions"])
        self.assertIn("Technology", options["categories"])
        self.assertIn("Corporate", options["segments"])
        self.assertEqual(len(options["warehouses"]), 3)

    def test_date_filter_ytd(self):
        # YTD from latest date year (2018)
        filtered = filter_retail_orders(self.bundle.orders, RetailFilters(date_range="YTD"))
        self.assertGreater(len(filtered), 0)
        self.assertTrue((filtered["order_date"].dt.year == 2018).all())

    def test_date_filter_30d(self):
        filtered = filter_retail_orders(self.bundle.orders, RetailFilters(date_range="30D"))
        max_date = self.bundle.orders["order_date"].max()
        min_date = max_date - pd.Timedelta(days=30)
        self.assertTrue((filtered["order_date"] >= min_date).all())
        self.assertTrue((filtered["order_date"] <= max_date).all())

    def test_region_filter(self):
        filtered = filter_retail_orders(self.bundle.orders, RetailFilters(region="West"))
        self.assertTrue((filtered["region"] == "West").all())
        self.assertGreater(len(filtered), 0)

    def test_category_filter(self):
        filtered = filter_retail_orders(
            self.bundle.orders,
            RetailFilters(category="Technology"),
            products=self.bundle.products,
        )
        self.assertGreater(len(filtered), 0)

    def test_search_filter(self):
        # Search for specific order
        sample_order = "CA-2017-152156"
        filtered = filter_retail_orders(self.bundle.orders, RetailFilters(search_query=sample_order))
        self.assertTrue((filtered["order_id"] == sample_order).all())
        self.assertGreater(len(filtered), 0)

    def test_bundle_filtering_synchronization(self):
        # Slicing the whole bundle keeps returns & transportation aligned by order_row_id
        filtered_bundle = filter_retail_data(self.bundle, RetailFilters(region="South"))
        valid_row_ids = set(filtered_bundle.orders["row_id"].unique())
        self.assertTrue(set(filtered_bundle.returns["order_row_id"]).issubset(valid_row_ids))
        self.assertTrue(set(filtered_bundle.transportation["order_row_id"]).issubset(valid_row_ids))


class TestCustomerRFMAnalytics(unittest.TestCase):
    """Verify RFM customer segmentation model aligns with reference logic."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()
        cls.rfm = calculate_customer_rfm(cls.bundle.orders, cls.bundle.customers)
        cls.summary = calculate_rfm_segment_summary(cls.rfm)

    def test_rfm_customer_count(self):
        self.assertEqual(len(self.rfm), 793, "All 793 customers must have an RFM score")

    def test_rfm_segment_names(self):
        expected_segments = {
            "Champions", "Loyal Customers", "Potential Loyalists",
            "At Risk", "Hibernating", "Lost"
        }
        actual_segments = set(self.rfm["rfm_segment"].unique())
        self.assertTrue(actual_segments.issubset(expected_segments))

    def test_rfm_summary_sum(self):
        total_accounted = self.summary["customer_count"].sum()
        self.assertEqual(total_accounted, 793, "Segment counts must sum to exactly 793")


if __name__ == "__main__":
    unittest.main()
