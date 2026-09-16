"""
Test Suite for Executive Dashboard & UI Components (Phase 3)
============================================================
Validates the Executive Dashboard analytical pipelines, filters,
formatting utilities, and Plotly data models.
"""

import unittest
import numpy as np
import pandas as pd

from python_app.data.loader import load_all_retail_data
from python_app.analytics.retail_analytics import (
    RetailFilters,
    filter_retail_data,
    calculate_retail_kpis,
    calculate_monthly_sales,
    calculate_sales_by_category,
    calculate_sales_by_region,
    calculate_sales_by_segment,
    calculate_top_products,
    get_filter_options,
)
from python_app.utils.formatting import (
    format_currency,
    format_number,
    format_percentage,
    format_days,
    format_abbreviated_currency,
)


class TestExecutiveDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()

    def test_executive_kpis_baseline(self):
        """Verify baseline Executive KPIs match verified ground truths."""
        kpis = calculate_retail_kpis(self.bundle)
        self.assertAlmostEqual(kpis["total_sales"], 2261536.97, delta=0.01)
        self.assertEqual(kpis["distinct_orders"], 4922)
        self.assertAlmostEqual(kpis["aov"], 459.48, delta=0.01)
        self.assertEqual(kpis["total_returns"], 490)
        self.assertAlmostEqual(kpis["return_rate_pct"], 9.96, delta=0.01)
        self.assertAlmostEqual(kpis["avg_delivery_days"], 4.11, delta=0.01)
        self.assertAlmostEqual(kpis["sales_yoy_growth_pct"], 20.30, delta=0.01)

    def test_filter_region_central(self):
        """Verify Central region filter calculation."""
        f = RetailFilters(region="Central")
        fb = filter_retail_data(self.bundle, f)
        kpis = calculate_retail_kpis(fb)
        self.assertAlmostEqual(kpis["total_sales"], 492646.90, delta=0.01)
        self.assertEqual(kpis["distinct_orders"], 1156)

    def test_filter_category_technology(self):
        """Verify Technology category filter calculation."""
        f = RetailFilters(category="Technology")
        fb = filter_retail_data(self.bundle, f)
        kpis = calculate_retail_kpis(fb)
        self.assertAlmostEqual(kpis["total_sales"], 827455.94, delta=0.01)
        self.assertEqual(kpis["distinct_orders"], 1519)

    def test_filter_segment_consumer(self):
        """Verify Consumer segment filter calculation."""
        f = RetailFilters(segment="Consumer")
        fb = filter_retail_data(self.bundle, f)
        kpis = calculate_retail_kpis(fb)
        self.assertAlmostEqual(kpis["total_sales"], 1148060.51, delta=0.01)
        self.assertEqual(kpis["distinct_orders"], 2537)

    def test_filter_date_presets(self):
        """Verify date presets 7D, 30D, YTD filter calculations relative to max order date."""
        # 7D
        fb_7d = filter_retail_data(self.bundle, RetailFilters(date_range="7D"))
        kpis_7d = calculate_retail_kpis(fb_7d)
        self.assertAlmostEqual(kpis_7d["total_sales"], 17137.63, delta=0.01)
        self.assertEqual(kpis_7d["distinct_orders"], 53)

        # 30D
        fb_30d = filter_retail_data(self.bundle, RetailFilters(date_range="30D"))
        kpis_30d = calculate_retail_kpis(fb_30d)
        self.assertAlmostEqual(kpis_30d["total_sales"], 89675.68, delta=0.01)
        self.assertEqual(kpis_30d["distinct_orders"], 234)

        # YTD
        fb_ytd = filter_retail_data(self.bundle, RetailFilters(date_range="YTD"))
        kpis_ytd = calculate_retail_kpis(fb_ytd)
        self.assertAlmostEqual(kpis_ytd["total_sales"], 722051.96, delta=0.01)
        self.assertEqual(kpis_ytd["distinct_orders"], 1661)

    def test_filter_search_query(self):
        """Verify free text search filtering."""
        fb = filter_retail_data(self.bundle, RetailFilters(search_query="Canon"))
        kpis = calculate_retail_kpis(fb)
        self.assertGreater(kpis["total_sales"], 0)
        self.assertEqual(kpis["distinct_orders"], 31)

    def test_empty_filter_state(self):
        """Verify dashboard data structures handle zero records gracefully without errors."""
        fb = filter_retail_data(self.bundle, RetailFilters(search_query="XYZ999NonExistent"))
        kpis = calculate_retail_kpis(fb)
        self.assertEqual(kpis["total_sales"], 0.0)
        self.assertEqual(kpis["distinct_orders"], 0)
        self.assertTrue(fb.orders.empty)

        monthly = calculate_monthly_sales(fb.orders)
        self.assertTrue(monthly.empty)

        cats = calculate_sales_by_category(fb.orders, self.bundle.products)
        self.assertTrue(cats.empty)

        segs = calculate_sales_by_segment(fb.orders, self.bundle.customers)
        self.assertTrue(segs.empty)

        regs = calculate_sales_by_region(fb.orders)
        self.assertTrue(regs.empty)

        top_p = calculate_top_products(fb.orders, self.bundle.products, 5)
        self.assertTrue(top_p.empty)

    def test_formatting_utilities(self):
        """Verify formatting utility outputs."""
        self.assertEqual(format_currency(2261536.97), "$2,261,536.97")
        self.assertEqual(format_number(4922), "4,922")
        self.assertEqual(format_percentage(9.96), "9.96%")
        self.assertEqual(format_days(4.11), "4.11 days")
        self.assertEqual(format_abbreviated_currency(2261536.97), "$2.26M")
        self.assertEqual(format_abbreviated_currency(492646.90), "$492.6k")

    def test_dynamic_filter_options(self):
        """Verify filter options are derived dynamically from dataset."""
        opts = get_filter_options(self.bundle)
        self.assertEqual(sorted(opts["regions"]), ["Central", "East", "South", "West"])
        self.assertEqual(sorted(opts["categories"]), ["Furniture", "Office Supplies", "Technology"])
        self.assertEqual(sorted(opts["segments"]), ["Consumer", "Corporate", "Home Office"])


if __name__ == "__main__":
    unittest.main()
