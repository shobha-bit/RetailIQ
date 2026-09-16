from pathlib import Path

# Base Paths
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DATA_DIR = PROJECT_ROOT / "public" / "data"

# Data file paths
ORDERS_CSV = DATA_DIR / "orders.csv"
CUSTOMERS_CSV = DATA_DIR / "customers.csv"
PRODUCTS_CSV = DATA_DIR / "products.csv"
INVENTORY_CSV = DATA_DIR / "inventory.csv"
RETURNS_CSV = DATA_DIR / "returns.csv"
TRANSPORTATION_CSV = DATA_DIR / "transportation.csv"

# Expected Ground Truth Baselines
EXPECTED_COUNTS = {
    "orders": 9800,
    "customers": 793,
    "products": 1861,
    "inventory": 1861,
    "returns": 490,
    "transportation": 9800,
}

EXPECTED_KPIS = {
    "total_sales": 2261536.97,
    "distinct_orders": 4922,
    "customers": 793,
    "aov": 459.48,
    "orders_per_customer": 6.21,
    "products": 1861,
    "avg_sales_per_product": 1215.23,
    "total_returns": 490,
    "returned_products": 424,
    "distinct_returned_orders": 465,
    "return_rate_pct": 9.96,
    "avg_delivery_days": 4.11,
    "inventory_stock": 512612,
    "low_stock_items": 34,
    "warehouses": 3,
}

# Required columns for schema validation
REQUIRED_COLUMNS = {
    "orders": [
        "row_id", "order_id", "order_date", "ship_date", "ship_mode",
        "customer_id", "product_id", "country", "city", "state",
        "postal_code", "region", "sales"
    ],
    "customers": [
        "customer_id", "customer_name", "segment"
    ],
    "products": [
        "product_id", "product_name", "category", "sub_category"
    ],
    "inventory": [
        "inventory_id", "product_id", "supplier_id", "warehouse_name",
        "warehouse_location", "stock_quantity", "reorder_level", "stock_status"
    ],
    "returns": [
        "return_id", "order_row_id", "product_id", "return_date",
        "return_reason", "refund_amount", "return_status"
    ],
    "transportation": [
        "transport_id", "order_row_id", "carrier_name", "tracking_number",
        "shipment_status", "dispatch_date", "estimated_delivery_date",
        "actual_delivery_date", "delivery_cost"
    ]
}
