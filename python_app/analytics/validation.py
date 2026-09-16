from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple
import pandas as pd

from python_app.config import EXPECTED_COUNTS, EXPECTED_KPIS
from python_app.data.loader import RetailDataBundle


@dataclass
class ValidationReport:
    is_valid: bool
    row_count_checks: Dict[str, Dict[str, Any]]
    relationship_checks: Dict[str, Dict[str, Any]]
    kpi_checks: Dict[str, Dict[str, Any]]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def validate_dataset_counts(data: RetailDataBundle) -> Dict[str, Dict[str, Any]]:
    """Validate that actual row counts match ground-truth specifications."""
    actuals = data.summary()
    results = {}
    for key, expected in EXPECTED_COUNTS.items():
        actual = actuals.get(key, 0)
        passed = actual == expected
        results[key] = {
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "difference": actual - expected,
        }
    return results


def validate_data_relationships(data: RetailDataBundle) -> Dict[str, Dict[str, Any]]:
    """
    Validate foreign key referential integrity across the 6 datasets:
      1. customers.customer_id -> orders.customer_id
      2. products.product_id -> orders.product_id
      3. returns.order_row_id -> orders.row_id
      4. transportation.order_row_id -> orders.row_id
      5. inventory.product_id -> products.product_id
    """
    results = {}

    # 1. Customers -> Orders
    valid_customer_ids = set(data.customers["customer_id"].unique())
    order_customer_ids = set(data.orders["customer_id"].unique())
    missing_cust_fks = order_customer_ids - valid_customer_ids
    results["orders_to_customers"] = {
        "relation": "orders.customer_id -> customers.customer_id",
        "missing_foreign_keys_count": len(missing_cust_fks),
        "passed": len(missing_cust_fks) == 0,
        "sample_missing": list(missing_cust_fks)[:5] if missing_cust_fks else [],
    }

    # 2. Products -> Orders
    valid_product_ids = set(data.products["product_id"].unique())
    order_product_ids = set(data.orders["product_id"].unique())
    missing_prod_fks = order_product_ids - valid_product_ids
    results["orders_to_products"] = {
        "relation": "orders.product_id -> products.product_id",
        "missing_foreign_keys_count": len(missing_prod_fks),
        "passed": len(missing_prod_fks) == 0,
        "sample_missing": list(missing_prod_fks)[:5] if missing_prod_fks else [],
    }

    # 3. Returns -> Orders (via row_id)
    valid_order_row_ids = set(data.orders["row_id"].unique())
    returns_order_row_ids = set(data.returns["order_row_id"].unique())
    missing_return_fks = returns_order_row_ids - valid_order_row_ids
    results["returns_to_orders"] = {
        "relation": "returns.order_row_id -> orders.row_id",
        "missing_foreign_keys_count": len(missing_return_fks),
        "passed": len(missing_return_fks) == 0,
        "sample_missing": list(missing_return_fks)[:5] if missing_return_fks else [],
    }

    # 4. Transportation -> Orders (via row_id)
    transport_order_row_ids = set(data.transportation["order_row_id"].unique())
    missing_transport_fks = transport_order_row_ids - valid_order_row_ids
    results["transportation_to_orders"] = {
        "relation": "transportation.order_row_id -> orders.row_id",
        "missing_foreign_keys_count": len(missing_transport_fks),
        "passed": len(missing_transport_fks) == 0,
        "sample_missing": list(missing_transport_fks)[:5] if missing_transport_fks else [],
    }

    # 5. Inventory -> Products
    inventory_product_ids = set(data.inventory["product_id"].unique())
    missing_inv_prod_fks = inventory_product_ids - valid_product_ids
    results["inventory_to_products"] = {
        "relation": "inventory.product_id -> products.product_id",
        "missing_foreign_keys_count": len(missing_inv_prod_fks),
        "passed": len(missing_inv_prod_fks) == 0,
        "sample_missing": list(missing_inv_prod_fks)[:5] if missing_inv_prod_fks else [],
    }

    # Check primary key uniqueness
    results["pk_uniqueness"] = {
        "orders_row_id_unique": bool(data.orders["row_id"].is_unique),
        "customers_id_unique": bool(data.customers["customer_id"].is_unique),
        "products_id_unique": bool(data.products["product_id"].is_unique),
        "inventory_id_unique": bool(data.inventory["inventory_id"].is_unique),
        "returns_id_unique": bool(data.returns["return_id"].is_unique),
        "transportation_id_unique": bool(data.transportation["transport_id"].is_unique),
    }

    return results


def calculate_retail_kpis(data: RetailDataBundle) -> Dict[str, Any]:
    """Calculate all real retail KPIs from the raw loaded DataFrames."""
    orders = data.orders
    customers = data.customers
    products = data.products
    inventory = data.inventory
    returns = data.returns
    transportation = data.transportation

    # 1. Total Sales
    total_sales = float(orders["sales"].sum())

    # 2. Total Distinct Orders
    distinct_orders = int(orders["order_id"].nunique())

    # 3. Total Distinct Customers
    total_customers = int(customers["customer_id"].nunique())

    # 4. Average Order Value (AOV)
    aov = total_sales / distinct_orders if distinct_orders > 0 else 0.0

    # 5. Orders per Customer
    orders_per_customer = distinct_orders / total_customers if total_customers > 0 else 0.0

    # 6. Total Products
    total_products = int(products["product_id"].nunique())

    # 7. Average Sales per Product
    avg_sales_per_product = total_sales / total_products if total_products > 0 else 0.0

    # 8. Total Returns
    total_returns = int(len(returns))

    # 9. Returned Unique Products
    returned_products = int(returns["product_id"].nunique())

    # 10. Distinct Returned Orders (matching orders.row_id == returns.order_row_id)
    returned_row_ids = set(returns["order_row_id"].unique())
    distinct_returned_orders = int(
        orders[orders["row_id"].isin(returned_row_ids)]["order_id"].nunique()
    )

    # 11. Return Rate (% of distinct orders)
    return_rate_pct = (total_returns / distinct_orders * 100.0) if distinct_orders > 0 else 0.0

    # 12. Average Delivery Days
    valid_transport = transportation.dropna(subset=["dispatch_date", "actual_delivery_date"])
    diff_days = (
        pd.to_datetime(valid_transport["actual_delivery_date"])
        - pd.to_datetime(valid_transport["dispatch_date"])
    ).dt.total_seconds() / 86400.0
    avg_delivery_days = float(diff_days.mean()) if len(diff_days) > 0 else 0.0

    # 13. Inventory Total Stock
    inventory_stock = int(inventory["stock_quantity"].sum())

    # 14. Low Stock Items (stock_quantity < reorder_level or stock_status == 'Low Stock')
    low_stock_items = int(
        ((inventory["stock_quantity"] < inventory["reorder_level"]) |
         (inventory["stock_status"] == "Low Stock")).sum()
    )

    # 15. Warehouses
    warehouses = int(inventory["warehouse_name"].nunique())

    # 16. Sales YoY (Dynamically computed from yearly sales aggregation)
    orders_with_dates = orders.dropna(subset=["order_date"]).copy()
    orders_with_dates["year"] = pd.to_datetime(orders_with_dates["order_date"]).dt.year
    yearly_sales = (
        orders_with_dates.groupby("year")["sales"].sum().sort_index().to_dict()
    )
    sorted_years = sorted(yearly_sales.keys())
    if len(sorted_years) >= 2:
        latest_year = sorted_years[-1]
        prior_year = sorted_years[-2]
        latest_sales = yearly_sales[latest_year]
        prior_sales = yearly_sales[prior_year]
        sales_yoy_growth_pct = (
            ((latest_sales - prior_sales) / prior_sales) * 100.0 if prior_sales > 0 else 0.0
        )
    else:
        latest_year = sorted_years[0] if sorted_years else 0
        prior_year = latest_year
        sales_yoy_growth_pct = 0.0

    return {
        "total_sales": total_sales,
        "distinct_orders": distinct_orders,
        "customers": total_customers,
        "aov": aov,
        "orders_per_customer": orders_per_customer,
        "products": total_products,
        "avg_sales_per_product": avg_sales_per_product,
        "total_returns": total_returns,
        "returned_products": returned_products,
        "distinct_returned_orders": distinct_returned_orders,
        "return_rate_pct": return_rate_pct,
        "avg_delivery_days": avg_delivery_days,
        "inventory_stock": inventory_stock,
        "low_stock_items": low_stock_items,
        "warehouses": warehouses,
        "sales_yoy_growth_pct": sales_yoy_growth_pct,
        "yearly_sales": yearly_sales,
        "latest_year": latest_year,
        "prior_year": prior_year,
    }


def verify_kpi_ground_truths(kpis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Compare calculated KPIs against ground-truth benchmarks with tolerance thresholds."""
    tolerances = {
        "total_sales": 0.05,
        "distinct_orders": 0,
        "customers": 0,
        "aov": 0.05,
        "orders_per_customer": 0.02,
        "products": 0,
        "avg_sales_per_product": 0.05,
        "total_returns": 0,
        "returned_products": 0,
        "distinct_returned_orders": 0,
        "return_rate_pct": 0.02,
        "avg_delivery_days": 0.05,
        "inventory_stock": 0,
        "low_stock_items": 0,
        "warehouses": 0,
    }

    results = {}
    for key, expected in EXPECTED_KPIS.items():
        actual = kpis.get(key)
        tol = tolerances.get(key, 0.001)
        if actual is None:
            results[key] = {
                "expected": expected,
                "actual": None,
                "passed": False,
                "diff": None,
            }
            continue

        diff = abs(actual - expected)
        passed = diff <= tol
        results[key] = {
            "expected": expected,
            "actual": round(actual, 4) if isinstance(actual, float) else actual,
            "tolerance": tol,
            "diff": round(diff, 4),
            "passed": passed,
        }

    return results


def run_full_validation(data: RetailDataBundle) -> ValidationReport:
    """Run comprehensive validation across counts, relationships, and KPIs."""
    row_counts = validate_dataset_counts(data)
    relationships = validate_data_relationships(data)
    kpis = calculate_retail_kpis(data)
    kpi_checks = verify_kpi_ground_truths(kpis)

    errors = []
    warnings = []

    for name, r in row_counts.items():
        if not r["passed"]:
            errors.append(f"Row count mismatch for {name}: expected {r['expected']}, got {r['actual']}")

    for name, r in relationships.items():
        if name != "pk_uniqueness" and not r.get("passed", True):
            errors.append(f"Foreign key referential breach in {r['relation']}: {r['missing_foreign_keys_count']} missing keys")

    for name, r in kpi_checks.items():
        if not r["passed"]:
            errors.append(f"KPI mismatch for {name}: expected {r['expected']}, got {r['actual']} (diff: {r['diff']})")

    is_valid = len(errors) == 0

    return ValidationReport(
        is_valid=is_valid,
        row_count_checks=row_counts,
        relationship_checks=relationships,
        kpi_checks=kpi_checks,
        errors=errors,
        warnings=warnings,
    )
