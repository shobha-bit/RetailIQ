"""
Unit Tests for Phase 6: Business Insights & Strategic Analytics
================================================================
Validates management-level strategic analytics, executive KPIs, dynamic rankings,
RFM retention churn exposure, data-grounded cross-sell co-occurrences,
inventory replenishment deficits, carrier SLA compliance, returns Pareto analysis,
strategic action rules, and price elasticity simulation.

Protects against:
- Hardcoded KPI values
- Inaccurate ranking or percentage math
- Unhandled empty datasets or zero denominators
- Fabrication of unsupported cross-sell claims
"""

import unittest
import pandas as pd

from python_app.data.loader import load_all_retail_data, RetailDataBundle
from python_app.analytics.retail_analytics import RetailFilters
from python_app.analytics.business_insights import (
    calculate_business_summary_kpis,
    calculate_performance_insights,
    calculate_retention_insights,
    calculate_product_opportunities,
    calculate_inventory_risk_insights,
    calculate_logistics_risk_insights,
    calculate_returns_risk_insights,
    generate_strategic_actions,
    simulate_price_elasticity,
    ELASTICITY_BENCHMARKS,
)


class TestPhase6BusinessInsights(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_all_retail_data()

    def test_business_summary_kpis_baseline(self):
        """Verify baseline executive KPIs match verified retail ground truths."""
        kpis = calculate_business_summary_kpis(self.bundle)

        self.assertAlmostEqual(kpis["total_sales"], 2261536.97, delta=0.5)
        self.assertEqual(kpis["total_orders"], 4922)
        self.assertAlmostEqual(kpis["aov"], 459.48, delta=0.5)
        self.assertAlmostEqual(kpis["sales_yoy"], 20.30, delta=0.2)
        self.assertAlmostEqual(kpis["return_rate"], 9.96, delta=0.1)
        self.assertAlmostEqual(kpis["average_delivery_days"], 4.11, delta=0.1)
        self.assertEqual(kpis["low_stock_items"], 34)
        self.assertEqual(kpis["total_stock"], 512612)
        self.assertEqual(kpis["total_customers"], 793)
        self.assertEqual(kpis["total_products"], 1861)
        self.assertEqual(kpis["delayed_shipments"], 928)
        self.assertEqual(kpis["total_shipments"], 9800)
        self.assertAlmostEqual(kpis["on_time_delivery_rate"], 89.51, delta=0.1)
        self.assertEqual(kpis["total_returns"], 490)
        self.assertEqual(kpis["distinct_returned_orders"], 465)
        self.assertEqual(kpis["distinct_returned_skus"], 424)
        self.assertAlmostEqual(kpis["total_refund_amount"], 81807.14, delta=0.5)
        self.assertEqual(kpis["warehouses"], 3)

    def test_business_summary_kpis_with_filters(self):
        """Verify KPI calculations with active filter criteria."""
        tech_filters = RetailFilters(category="Technology")
        kpis_tech = calculate_business_summary_kpis(self.bundle, filters=tech_filters)

        self.assertGreater(kpis_tech["total_sales"], 0.0)
        self.assertLess(kpis_tech["total_sales"], 2261536.97)
        self.assertGreater(kpis_tech["total_orders"], 0)
        self.assertLess(kpis_tech["total_orders"], 4922)

    def test_performance_insights_dynamic_rankings(self):
        """Verify dynamic rankings across regions, categories, and customer segments."""
        perf = calculate_performance_insights(
            self.bundle.orders,
            self.bundle.customers,
            self.bundle.products,
        )

        # Regional rankings (West, East, Central, South)
        self.assertEqual(perf["strongest_region"]["name"], "West")
        self.assertAlmostEqual(perf["strongest_region"]["sales"], 710219.77, delta=1.0)
        self.assertAlmostEqual(perf["strongest_region"]["pct_of_total"], 31.40, delta=0.5)
        self.assertEqual(perf["weakest_region"]["name"], "South")
        self.assertAlmostEqual(perf["weakest_region"]["sales"], 389151.45, delta=1.0)
        self.assertEqual(len(perf["regional_rankings"]), 4)

        # Category rankings (Technology, Furniture, Office Supplies)
        self.assertEqual(perf["strongest_category"]["name"], "Technology")
        self.assertAlmostEqual(perf["strongest_category"]["sales"], 827455.94, delta=1.0)
        self.assertEqual(perf["weakest_category"]["name"], "Office Supplies")
        self.assertAlmostEqual(perf["weakest_category"]["sales"], 705422.28, delta=1.0)
        self.assertEqual(len(perf["category_rankings"]), 3)

        # Segment rankings (Consumer, Corporate, Home Office)
        self.assertEqual(perf["strongest_segment"]["name"], "Consumer")
        self.assertAlmostEqual(perf["strongest_segment"]["sales"], 1148060.51, delta=1.0)
        self.assertAlmostEqual(perf["strongest_segment"]["pct_of_total"], 50.76, delta=0.5)

        # Sales Growth Trend
        self.assertEqual(perf["sales_growth_trend"]["trajectory"], "Strong Expansion")
        self.assertAlmostEqual(perf["sales_growth_trend"]["growth_pct"], 20.30, delta=0.2)

        # Customer concentration
        self.assertGreater(perf["high_value_customer_summary"]["top_10_spend"], 0.0)
        self.assertGreater(perf["high_value_customer_summary"]["top_10_share"], 0.0)

    def test_retention_insights_rfm(self):
        """Verify RFM cohort distribution and churn exposure calculation."""
        ret = calculate_retention_insights(
            self.bundle.orders,
            self.bundle.customers,
            self.bundle.products,
        )

        # Verified segment customer counts
        self.assertEqual(ret["segment_counts"]["Champions"], 272)
        self.assertEqual(ret["segment_counts"]["Loyal Customers"], 247)
        self.assertEqual(ret["segment_counts"]["Potential Loyalists"], 123)
        self.assertEqual(ret["segment_counts"]["At Risk"], 87)
        self.assertEqual(ret["segment_counts"]["Hibernating"], 43)
        self.assertEqual(ret["segment_counts"]["Lost"], 21)
        self.assertEqual(ret["total_customers"], 793)

        # Churn risk exposure: At Risk + Hibernating = 87 + 43 = 130 accounts
        self.assertEqual(ret["at_risk_count"], 130)
        self.assertAlmostEqual(ret["at_risk_pct"], 16.39, delta=0.2)
        self.assertAlmostEqual(ret["at_risk_spend"], 309392.30, delta=1.0)
        self.assertEqual(ret["retention_priority"], "High")

        # Champions opportunity
        self.assertEqual(ret["champions_count"], 272)
        self.assertAlmostEqual(ret["champions_spend"], 1019357.03, delta=1.0)
        self.assertAlmostEqual(ret["champions_pct"], 34.30, delta=0.2)

    def test_product_opportunities_and_cross_sell(self):
        """Verify product concentration and transaction-based cross-sell discovery."""
        prod_opp = calculate_product_opportunities(
            self.bundle.orders,
            self.bundle.products,
            self.bundle.returns,
            limit=10,
        )

        self.assertAlmostEqual(prod_opp["top_products_sales"], 244620.20, delta=1.0)
        self.assertAlmostEqual(prod_opp["top_products_share"], 10.82, delta=0.2)

        # Multi-category orders prevalence
        self.assertEqual(prod_opp["multi_category_order_count"], 1682)
        self.assertAlmostEqual(prod_opp["multi_category_order_pct"], 34.17, delta=0.2)

        # Real cross-sell pairs verified from orders
        pairs = prod_opp["cross_sell_pairs"]
        self.assertGreater(len(pairs), 0)

        # Find Furniture + Office Supplies pair
        fo_pair = next((p for p in pairs if p["type"] == "Category Pair" and set([p["item_a"], p["item_b"]]) == set(["Furniture", "Office Supplies"])), None)
        self.assertIsNotNone(fo_pair)
        self.assertEqual(fo_pair["order_co_occurrences"], 944)

    def test_inventory_risk_insights(self):
        """Verify inventory replenishment metrics and warehouse risk."""
        inv = calculate_inventory_risk_insights(
            self.bundle.inventory,
            self.bundle.products,
        )

        self.assertEqual(inv["low_stock_items"], 34)
        self.assertEqual(inv["total_stock"], 512612)
        self.assertEqual(inv["inventory_items"], 1861)
        self.assertEqual(inv["warehouses"], 3)
        self.assertEqual(inv["total_replenishment_deficit"], 336)
        self.assertAlmostEqual(inv["stock_health_rate"], 98.17, delta=0.1)
        self.assertFalse(inv["top_deficit_skus"].empty)
        self.assertEqual(len(inv["top_deficit_skus"]), 5)

    def test_logistics_risk_insights(self):
        """Verify carrier fulfillment SLA compliance and delivery delays."""
        log = calculate_logistics_risk_insights(
            self.bundle.transportation,
            sla_target_pct=90.0,
        )

        self.assertAlmostEqual(log["on_time_delivery_rate"], 89.51, delta=0.1)
        self.assertAlmostEqual(log["average_delivery_days"], 4.11, delta=0.1)
        self.assertEqual(log["delayed_shipments"], 928)
        self.assertEqual(log["total_shipments"], 9800)
        self.assertFalse(log["carrier_summary"].empty)
        self.assertIn("carrier_name", log["carrier_summary"].columns)

    def test_returns_risk_insights(self):
        """Verify reverse logistics Pareto analysis and return liability."""
        ret = calculate_returns_risk_insights(
            self.bundle.returns,
            self.bundle.orders,
            self.bundle.products,
        )

        self.assertEqual(ret["total_returns"], 490)
        self.assertEqual(ret["distinct_returned_orders"], 465)
        self.assertEqual(ret["distinct_returned_skus"], 424)
        self.assertAlmostEqual(ret["return_rate"], 9.96, delta=0.1)
        self.assertAlmostEqual(ret["total_refund_amount"], 81807.14, delta=0.5)

        # Root cause distribution
        self.assertEqual(ret["top_reason"]["reason"], "Late Delivery")
        self.assertEqual(ret["top_reason"]["count"], 105)
        self.assertAlmostEqual(ret["top_reason"]["pct"], 21.43, delta=0.2)
        self.assertAlmostEqual(ret["top_reason"]["refund"], 14606.05, delta=0.5)

        self.assertEqual(ret["defective_return_count"], 92)
        self.assertEqual(ret["late_delivery_return_count"], 105)

    def test_strategic_actions_generation(self):
        """Verify strategic actions are generated dynamically from operational thresholds."""
        actions = generate_strategic_actions(self.bundle)

        self.assertGreater(len(actions), 0)
        priorities = [a["priority"] for a in actions]
        self.assertIn("High", priorities)
        self.assertIn("Medium", priorities)
        self.assertIn("Low", priorities)

        for a in actions:
            self.assertIn("id", a)
            self.assertIn("category", a)
            self.assertIn("issue", a)
            self.assertIn("supporting_metric", a)
            self.assertIn("recommended_action", a)
            self.assertIn(a["priority"], ["High", "Medium", "Low"])

    def test_price_elasticity_simulator(self):
        """Verify PED math and category benchmarks."""
        # Technology (+10% price change)
        sim_tech = simulate_price_elasticity("Technology", 10.0)
        self.assertEqual(sim_tech["ped"], -1.65)
        self.assertAlmostEqual(sim_tech["demand_change_pct"], -16.5, delta=0.1)
        self.assertAlmostEqual(sim_tech["rev_change_pct"], -8.2, delta=0.1)
        self.assertAlmostEqual(sim_tech["margin_impact"], 8.0, delta=0.1)
        self.assertEqual(sim_tech["optimal_discount"], "10% - 15%")

        # Furniture (+5% price change)
        sim_fur = simulate_price_elasticity("Furniture", 5.0)
        self.assertEqual(sim_fur["ped"], -1.25)
        self.assertAlmostEqual(sim_fur["demand_change_pct"], -6.2, delta=0.1)

        # Office Supplies (-10% price change)
        sim_off = simulate_price_elasticity("Office Supplies", -10.0)
        self.assertEqual(sim_off["ped"], -0.85)
        self.assertAlmostEqual(sim_off["demand_change_pct"], 8.5, delta=0.1)

    def test_defensive_empty_datasets(self):
        """Verify that functions gracefully handle empty datasets without crashing."""
        empty_orders = pd.DataFrame(columns=["order_id", "sales", "row_id", "order_date", "ship_date"])
        empty_customers = pd.DataFrame(columns=["customer_id", "customer_name", "segment"])
        empty_products = pd.DataFrame(columns=["product_id", "product_name", "category", "sub_category"])
        empty_inventory = pd.DataFrame(columns=["product_id", "stock_quantity", "reorder_level", "warehouse_location"])
        empty_returns = pd.DataFrame(columns=["return_id", "order_row_id", "return_reason", "refund_amount"])
        empty_transportation = pd.DataFrame(columns=["order_row_id", "carrier_name", "status", "delivery_cost"])

        perf_empty = calculate_performance_insights(empty_orders, empty_customers, empty_products)
        self.assertEqual(perf_empty["strongest_region"]["name"], "N/A")
        self.assertEqual(perf_empty["strongest_category"]["name"], "N/A")

        ret_empty = calculate_retention_insights(empty_orders, empty_customers, empty_products)
        self.assertEqual(ret_empty["total_customers"], 0)
        self.assertEqual(ret_empty["at_risk_count"], 0)

        prod_empty = calculate_product_opportunities(empty_orders, empty_products, empty_returns)
        self.assertEqual(prod_empty["top_products_sales"], 0.0)

        inv_empty = calculate_inventory_risk_insights(empty_inventory, empty_products)
        self.assertEqual(inv_empty["low_stock_items"], 0)
        self.assertEqual(inv_empty["total_replenishment_deficit"], 0)

        log_empty = calculate_logistics_risk_insights(empty_transportation)
        self.assertEqual(log_empty["delayed_shipments"], 0)
        self.assertEqual(log_empty["on_time_delivery_rate"], 0.0)

        returns_empty = calculate_returns_risk_insights(empty_returns, empty_orders, empty_products)
        self.assertEqual(returns_empty["total_returns"], 0)
        self.assertEqual(returns_empty["return_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
