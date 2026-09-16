from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

try:
    import streamlit as st
    cache_decorator = st.cache_data
except ImportError:
    def cache_decorator(func):
        return func

from python_app.config import (
    ORDERS_CSV,
    CUSTOMERS_CSV,
    PRODUCTS_CSV,
    INVENTORY_CSV,
    RETURNS_CSV,
    TRANSPORTATION_CSV,
    REQUIRED_COLUMNS,
    EXPECTED_COUNTS,
)


@dataclass
class RetailDataBundle:
    orders: pd.DataFrame
    customers: pd.DataFrame
    products: pd.DataFrame
    inventory: pd.DataFrame
    returns: pd.DataFrame
    transportation: pd.DataFrame

    def summary(self) -> Dict[str, int]:
        return {
            "orders": len(self.orders),
            "customers": len(self.customers),
            "products": len(self.products),
            "inventory": len(self.inventory),
            "returns": len(self.returns),
            "transportation": len(self.transportation),
        }


def _validate_and_read_csv(
    file_path: Path,
    dataset_name: str,
    required_cols: Optional[List[str]] = None,
    parse_dates: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Safely read and validate a retail CSV file."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset '{dataset_name}' not found at path: {file_path}. "
            "Please ensure the file exists in the public/data directory."
        )

    if file_path.stat().st_size == 0:
        raise ValueError(f"Dataset '{dataset_name}' at {file_path} is completely empty.")

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise RuntimeError(f"Failed to parse CSV for '{dataset_name}': {e}") from e

    if df.empty:
        raise ValueError(f"Dataset '{dataset_name}' contains no rows.")

    # Validate required columns
    expected_cols = required_cols or REQUIRED_COLUMNS.get(dataset_name, [])
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(
            f"Dataset '{dataset_name}' is missing required columns: {missing_cols}. "
            f"Found columns: {list(df.columns)}"
        )

    # Convert date columns if specified and present
    if parse_dates:
        for date_col in parse_dates:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    return df


@cache_decorator
def load_orders(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the 9,800 orders dataset."""
    path = file_path or ORDERS_CSV
    df = _validate_and_read_csv(
        file_path=path,
        dataset_name="orders",
        parse_dates=["order_date", "ship_date"],
    )
    # Ensure sales and row_id are numeric
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce").fillna(0.0)
    df["row_id"] = pd.to_numeric(df["row_id"], errors="coerce").fillna(0).astype(int)
    return df


@cache_decorator
def load_customers(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the 793 customers dataset."""
    path = file_path or CUSTOMERS_CSV
    return _validate_and_read_csv(
        file_path=path,
        dataset_name="customers",
    )


@cache_decorator
def load_products(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the 1,861 catalog products dataset."""
    path = file_path or PRODUCTS_CSV
    return _validate_and_read_csv(
        file_path=path,
        dataset_name="products",
    )


@cache_decorator
def load_inventory(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the 1,861 warehouse inventory records dataset."""
    path = file_path or INVENTORY_CSV
    df = _validate_and_read_csv(
        file_path=path,
        dataset_name="inventory",
        parse_dates=["last_restock_date"],
    )
    df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], errors="coerce").fillna(0).astype(int)
    df["reorder_level"] = pd.to_numeric(df["reorder_level"], errors="coerce").fillna(0).astype(int)
    return df


@cache_decorator
def load_returns(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the 490 return records dataset."""
    path = file_path or RETURNS_CSV
    df = _validate_and_read_csv(
        file_path=path,
        dataset_name="returns",
        parse_dates=["return_date"],
    )
    df["order_row_id"] = pd.to_numeric(df["order_row_id"], errors="coerce").fillna(0).astype(int)
    df["refund_amount"] = pd.to_numeric(df["refund_amount"], errors="coerce").fillna(0.0)
    return df


@cache_decorator
def load_transportation(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the 9,800 logistics fulfillment dataset."""
    path = file_path or TRANSPORTATION_CSV
    df = _validate_and_read_csv(
        file_path=path,
        dataset_name="transportation",
        parse_dates=["dispatch_date", "estimated_delivery_date", "actual_delivery_date"],
    )
    df["order_row_id"] = pd.to_numeric(df["order_row_id"], errors="coerce").fillna(0).astype(int)
    df["delivery_cost"] = pd.to_numeric(df["delivery_cost"], errors="coerce").fillna(0.0)
    return df


@cache_decorator
def load_all_retail_data() -> RetailDataBundle:
    """Load all six retail datasets into a single RetailDataBundle."""
    orders = load_orders()
    customers = load_customers()
    products = load_products()
    inventory = load_inventory()
    returns = load_returns()
    transportation = load_transportation()

    return RetailDataBundle(
        orders=orders,
        customers=customers,
        products=products,
        inventory=inventory,
        returns=returns,
        transportation=transportation,
    )
