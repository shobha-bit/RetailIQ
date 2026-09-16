"""
Test Suite for Phase 4 Dashboards: Sales Analysis & Customer RFM Analysis
=========================================================================
Validates the data pipelines, metric aggregations, and RFM behavioral models
for both new dashboards against the reference implementation and ground truths.
"""

import unittest
import pandas as pd
import numpy as np

from python_app.data.loader import load_all_retail_data
from python_app.analytics.retail_analytics import (
    RetailFilters,
    filter_retail_data,
    calculate_retail_kpis,
    calculate_monthly_sales,
    calculate_sales_by_category,
    calculate_sales_by_region,
    calculate_sales_by_segment,
    calculate_channel_margin,
    calculate_top_products,
    calculate_customer_rfm,
    calculate_rfm_segment_summary,
    safe_join_orders_customers,
    safe_join_orders_products,
)


class TestSalesAnalysisPipeline(unittest.TestCase):
    """Test data pipelines and calculations for Sales Analysis Dashboard."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()

    def test_sales_kpis_unfiltered(self):
        """Verify baseline sales KPIs match verified ground truths."""
        kpis = calculate_retail_kpis(self.bundle)
        self.assertAlmostEqual(kpis["total_sales"], 2261536.97, delta=0.01)
        self.assertEqual(kpis["distinct_orders"], 4922)
        self.assertAlmostEqual(kpis["aov"], 459.48, delta=0.01)
        self.assertAlmostEqual(kpis["sales_yoy_growth_pct"], 20.30, delta=0.01)

    def test_channel_margin_health(self):
        """Verify sales channels (segments) margin and revenue integrity."""
        channel_df = calculate_channel_margin(self.bundle.orders, self.bundle.customers)
        self.assertEqual(len(channel_df), 3, "Expected 3 retail channels")
        self.assertEqual(sorted(channel_df["channel"]), ["Consumer", "Corporate", "Home Office"])

        # Revenue across all 3 channels must sum to total sales
        total_rev = channel_df["revenue"].sum()
        self.assertAlmostEqual(total_rev, 2261536.97, delta=0.01)

        # Margin % is 40.0%
        for _, row in channel_df.iterrows():
            self.assertEqual(row["margin_pct"], 40.0)
            self.assertAlmostEqual(row["profit"], round(row["revenue"] * 0.40, 2), delta=0.02)

    def test_monthly_sales_velocity(self):
        """Verify monthly sales cadence timeline includes both revenue and profit."""
        monthly = calculate_monthly_sales(self.bundle.orders)
        self.assertGreater(len(monthly), 0)
        self.assertIn("sales", monthly.columns)
        self.assertIn("profit", monthly.columns)
        self.assertIn("orders", monthly.columns)
        self.assertIn("aov", monthly.columns)

        # Sum of monthly sales must equal total sales
        self.assertAlmostEqual(monthly["sales"].sum(), 2261536.97, delta=0.01)

    def test_regional_sales_breakdown(self):
        """Verify regional commercial contribution sums to total sales."""
        reg = calculate_sales_by_region(self.bundle.orders)
        self.assertEqual(len(reg), 4, "Expected 4 geographic regions")
        self.assertAlmostEqual(reg["sales"].sum(), 2261536.97, delta=0.01)
        self.assertAlmostEqual(reg["pct_of_total"].sum(), 100.0, delta=0.1)

    def test_top_products_catalog(self):
        """Verify top catalog products aggregation."""
        top_10 = calculate_top_products(self.bundle.orders, self.bundle.products, limit=10)
        self.assertEqual(len(top_10), 10)
        self.assertTrue((top_10["sales"].diff().dropna() <= 0).all(), "Products must be sorted descending by sales")

    def test_transaction_ledger_join(self):
        """Verify orders join with customers and products cleanly without dropping rows."""
        orders = self.bundle.orders
        joined_cust = safe_join_orders_customers(orders, self.bundle.customers)
        self.assertEqual(len(joined_cust), len(orders), "Customer join must preserve exact order rows (9,800)")

        joined_prod = safe_join_orders_products(orders, self.bundle.products)
        self.assertEqual(len(joined_prod), len(orders), "Product join must preserve exact order rows (9,800)")


class TestCustomerRFMAnalysisPipeline(unittest.TestCase):
    """Test data pipelines and RFM behavioral models for Customer Analysis Dashboard."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()
        cls.rfm = calculate_customer_rfm(cls.bundle.orders, cls.bundle.customers, products=cls.bundle.products)
        cls.summary = calculate_rfm_segment_summary(cls.rfm)

    def test_customer_count(self):
        """Verify all 793 customers are evaluated."""
        self.assertEqual(len(self.rfm), 793)

    def test_rfm_segment_counts_match_reference(self):
        """
        Verify exact behavioral segment counts match the React reference implementation:
        Champions: 272, Loyal Customers: 247, Potential Loyalists: 123,
        At Risk: 87, Hibernating: 43, Lost: 21
        """
        counts = self.rfm["rfm_segment"].value_counts().to_dict()
        self.assertEqual(counts.get("Champions", 0), 272, "Champions cohort count mismatch")
        self.assertEqual(counts.get("Loyal Customers", 0), 247, "Loyal Customers count mismatch")
        self.assertEqual(counts.get("Potential Loyalists", 0), 123, "Potential Loyalists count mismatch")
        self.assertEqual(counts.get("At Risk", 0), 87, "At Risk count mismatch")
        self.assertEqual(counts.get("Hibernating", 0), 43, "Hibernating count mismatch")
        self.assertEqual(counts.get("Lost", 0), 21, "Lost count mismatch")

    def test_rfm_monetary_reconciliation(self):
        """Total spend across RFM profiles must reconcile with total net sales."""
        total_rfm_spend = self.rfm["monetary_value"].sum()
        self.assertAlmostEqual(total_rfm_spend, 2261536.97, delta=0.01)

    def test_champions_cohort_spend(self):
        """Verify Champions cohort spend matches reference value ($1,019,357.03)."""
        champions = self.rfm[self.rfm["rfm_segment"] == "Champions"]
        champ_spend = champions["monetary_value"].sum()
        self.assertAlmostEqual(champ_spend, 1019357.03, delta=0.02)

    def test_revenue_at_risk_reconciliation(self):
        """Verify At-Risk + Hibernating headcount (130) and revenue ($309,392.30)."""
        at_risk = self.rfm[self.rfm["rfm_segment"].isin(["At Risk", "Hibernating"])]
        self.assertEqual(len(at_risk), 130)
        self.assertAlmostEqual(at_risk["monetary_value"].sum(), 309392.30, delta=0.02)

    def test_average_clv(self):
        """Verify Average Customer Lifetime Value ($2,852)."""
        avg_clv = self.rfm["monetary_value"].sum() / len(self.rfm)
        self.assertAlmostEqual(avg_clv, 2851.87, delta=0.1)
        self.assertEqual(round(avg_clv), 2852)

    def test_rfm_derived_attributes(self):
        """Verify email, favorite category, and AOV attributes are computed."""
        self.assertIn("customer_email", self.rfm.columns)
        self.assertIn("preferred_category", self.rfm.columns)
        self.assertIn("aov", self.rfm.columns)
        self.assertIn("churn_probability", self.rfm.columns)

        # Emails are well-formed
        self.assertTrue(self.rfm["customer_email"].str.endswith("@retail-corp.com").all())

        # Preferred categories belong to known categories
        known_cats = {"Furniture", "Office Supplies", "Technology"}
        self.assertTrue(set(self.rfm["preferred_category"].unique()).issubset(known_cats))

    def test_segment_summary_completeness(self):
        """Verify segment summary table aggregates headcounts and metrics accurately."""
        self.assertEqual(len(self.summary), 6)
        self.assertEqual(self.summary["customer_count"].sum(), 793)
        self.assertAlmostEqual(self.summary["total_spend"].sum(), 2261536.97, delta=0.01)


if __name__ == "__main__":
    unittest.main()
