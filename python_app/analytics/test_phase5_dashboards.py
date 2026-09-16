import unittest
import pandas as pd
from python_app.data.loader import load_all_retail_data
from python_app.analytics.retail_analytics import (
    calculate_inventory_kpis,
    calculate_stock_by_warehouse,
    calculate_stock_status_distribution,
    calculate_inventory_by_category,
    calculate_low_stock_products,
    calculate_logistics_kpis,
    calculate_carrier_summary,
    calculate_shipment_status_distribution,
    calculate_delivery_trend,
    calculate_returns_kpis,
    calculate_return_reasons,
    calculate_return_status_distribution,
    calculate_monthly_returns,
    calculate_top_returned_products,
    calculate_returns_by_category,
)
from python_app.dashboards.inventory_analysis import render_inventory_analysis
from python_app.dashboards.logistics_analysis import render_logistics_analysis
from python_app.dashboards.returns_analysis import render_returns_analysis


class TestPhase5Dashboards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()

    # =========================================================================
    # 1. INVENTORY ANALYSIS TESTS
    # =========================================================================
    def test_inventory_kpis_ground_truth(self):
        kpis = calculate_inventory_kpis(self.bundle.inventory)
        self.assertEqual(kpis["total_stock"], 512612)
        self.assertEqual(kpis["inventory_items"], 1861)
        self.assertEqual(kpis["low_stock_items"], 34)
        self.assertEqual(kpis["warehouses"], 3)

    def test_stock_by_warehouse(self):
        wh = calculate_stock_by_warehouse(self.bundle.inventory)
        self.assertEqual(len(wh), 3)
        self.assertEqual(wh["stock_quantity"].sum(), 512612)
        self.assertEqual(wh["low_stock_count"].sum(), 34)
        wh_names = set(wh["warehouse_name"])
        self.assertTrue("Office Supply Warehouse" in wh_names)
        self.assertTrue("Technology Warehouse" in wh_names)
        self.assertTrue("Furniture Warehouse" in wh_names)

    def test_stock_status_distribution(self):
        dist = calculate_stock_status_distribution(self.bundle.inventory)
        status_map = dict(zip(dist["stock_status"], dist["count"]))
        self.assertEqual(status_map.get("In Stock"), 1827)
        self.assertEqual(status_map.get("Low Stock"), 34)
        self.assertEqual(dist["count"].sum(), 1861)

    def test_calculate_low_stock_products(self):
        low_df = calculate_low_stock_products(self.bundle.inventory, self.bundle.products)
        self.assertEqual(len(low_df), 34)
        self.assertTrue((low_df["deficit"] >= 0).all())
        self.assertTrue("product_name" in low_df.columns)
        self.assertTrue("category" in low_df.columns)

    def test_calculate_inventory_by_category(self):
        cat_df = calculate_inventory_by_category(self.bundle.inventory, self.bundle.products)
        self.assertEqual(cat_df["stock_quantity"].sum(), 512612)
        categories = set(cat_df["category"])
        self.assertTrue("Office Supplies" in categories)
        self.assertTrue("Technology" in categories)
        self.assertTrue("Furniture" in categories)

    # =========================================================================
    # 2. LOGISTICS ANALYSIS TESTS
    # =========================================================================
    def test_logistics_kpis_ground_truth(self):
        kpis = calculate_logistics_kpis(self.bundle.transportation)
        self.assertAlmostEqual(kpis["average_delivery_days"], 4.11, places=2)
        self.assertAlmostEqual(kpis["on_time_delivery_rate"], 89.51, places=1)
        self.assertEqual(kpis["shipment_count"], 9800)
        self.assertEqual(kpis["delivered_shipments"], 8847)
        self.assertEqual(kpis["delayed_shipments"], 928)

    def test_carrier_summary(self):
        cs = calculate_carrier_summary(self.bundle.transportation)
        self.assertEqual(len(cs), 6)
        self.assertEqual(cs["total_shipments"].sum(), 9800)
        carriers = set(cs["carrier_name"])
        expected_carriers = {"Blue Dart", "Delhivery", "Dhl", "Fedex", "Ups", "Xpressbees"}
        self.assertEqual(carriers, expected_carriers)
        for _, row in cs.iterrows():
            self.assertGreaterEqual(row["on_time_rate"], 0.0)
            self.assertLessEqual(row["on_time_rate"], 100.0)
            self.assertGreater(row["avg_transit_days"], 0.0)

    def test_shipment_status_distribution(self):
        dist = calculate_shipment_status_distribution(self.bundle.transportation)
        self.assertEqual(dist["count"].sum(), 9800)
        statuses = set(dist["shipment_status"])
        self.assertTrue("Delivered" in statuses)
        self.assertTrue("In Transit" in statuses)

    def test_delivery_trend(self):
        trend = calculate_delivery_trend(self.bundle.transportation)
        self.assertFalse(trend.empty)
        self.assertTrue("on_time_rate" in trend.columns)
        self.assertTrue("shipments" in trend.columns)
        self.assertGreater(trend["shipments"].sum(), 0)

    # =========================================================================
    # 3. RETURNS ANALYSIS TESTS
    # =========================================================================
    def test_returns_kpis_ground_truth(self):
        kpis = calculate_returns_kpis(self.bundle.returns, self.bundle.orders)
        self.assertEqual(kpis["total_returns"], 490)
        self.assertEqual(kpis["returned_products"], 424)
        self.assertEqual(kpis["distinct_returned_orders"], 465)
        self.assertAlmostEqual(kpis["return_rate_pct"], 9.96, places=1)
        self.assertAlmostEqual(kpis["total_refund_amount"], 81807.14, places=1)

    def test_return_reasons(self):
        reasons = calculate_return_reasons(self.bundle.returns)
        self.assertEqual(reasons["count"].sum(), 490)
        reason_map = dict(zip(reasons["return_reason"], reasons["count"]))
        self.assertEqual(reason_map.get("Late Delivery"), 105)
        self.assertEqual(reason_map.get("Defective Product"), 92)
        self.assertEqual(reason_map.get("Customer Changed Mind"), 85)
        self.assertEqual(reason_map.get("Wrong Item"), 72)
        self.assertEqual(reason_map.get("Damaged Product"), 70)
        self.assertEqual(reason_map.get("Other"), 66)

    def test_return_status_distribution(self):
        status = calculate_return_status_distribution(self.bundle.returns)
        self.assertEqual(status["count"].sum(), 490)
        status_map = dict(zip(status["return_status"], status["count"]))
        self.assertEqual(status_map.get("Completed"), 338)
        self.assertEqual(status_map.get("Rejected"), 65)
        self.assertEqual(status_map.get("Requested"), 45)
        self.assertEqual(status_map.get("Approved"), 42)

    def test_calculate_top_returned_products(self):
        top = calculate_top_returned_products(self.bundle.returns, self.bundle.products, self.bundle.orders, limit=10)
        self.assertEqual(len(top), 10)
        self.assertTrue("product_id" in top.columns)
        self.assertTrue("recommendation" in top.columns)
        self.assertTrue("total_refund" in top.columns)
        self.assertTrue(top["return_count"].is_monotonic_decreasing)

    def test_calculate_returns_by_category(self):
        cat_ret = calculate_returns_by_category(self.bundle.returns, self.bundle.products)
        self.assertEqual(cat_ret["return_count"].sum(), 490)
        self.assertAlmostEqual(cat_ret["total_refund"].sum(), 81807.14, places=1)

    def test_render_functions_importable(self):
        self.assertTrue(callable(render_inventory_analysis))
        self.assertTrue(callable(render_logistics_analysis))
        self.assertTrue(callable(render_returns_analysis))


if __name__ == "__main__":
    unittest.main()
